#!/usr/bin/env pwsh

param(
  [string]$IgFolder = "test-ig",
  [ValidateSet("start", "sushi", "publisher", "sushi-publisher", "stop")]
  [string]$Mode = "start",
  [string]$ContainerName = "ig-publisher-cli",
  [string]$EnvFile = ".env.fhir"
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$ComposeFile = Join-Path $RepoRoot "docker-compose.yml"
$IgPath = Join-Path $RepoRoot $IgFolder
$EnvFilePath = Join-Path $RepoRoot $EnvFile
$KeepAliveCommand = "tail -f /dev/null"

function Invoke-DockerCommand {
  param(
    [scriptblock]$Command,
    [string]$Description
  )

  & $Command
  if ($LASTEXITCODE -ne 0) {
    throw "$Description failed with exit code $LASTEXITCODE."
  }
}

function Test-ContainerExists {
  param([string]$Name)
  $names = @(docker ps -a --format "{{.Names}}")
  return $Name -in $names
}

function Assert-ContainerRunning {
  param([string]$Name)
  $runningNames = @(docker ps --format "{{.Names}}")
  $isRunning = $Name -in $runningNames
  if (-not $isRunning) {
    throw "Container '$Name' is not running. Start it first: .\scripts\run-ig-cli.ps1 -Mode start"
  }
}

function Invoke-SushiCommand {
  param([string]$Name)
  Invoke-DockerCommand -Description "docker exec sushi" -Command {
    docker exec $Name sushi --out /usr/src/ig /usr/src/ig
  }
}

function Invoke-PublisherCommand {
  param([string]$Name)
  Invoke-DockerCommand -Description "docker exec publisher" -Command {
    docker exec $Name java -jar /app/publisher.jar -ig /usr/src/ig/ig.ini
  }
}

function Get-FhirVersion {
  param([string]$Path)

  $rawValue = $null
  foreach ($line in Get-Content $Path) {
    $trimmed = $line.Trim()
    if ($trimmed -eq "" -or $trimmed.StartsWith("#")) {
      continue
    }
    $parts = $trimmed -split "=", 2
    if ($parts.Count -eq 2 -and $parts[0].Trim() -eq "FHIR_VERSION") {
      $rawValue = $parts[1].Trim()
      break
    }
  }

  if (-not $rawValue) {
    throw "FHIR_VERSION is missing in env file '$Path'."
  }

  switch ($rawValue.ToLowerInvariant()) {
    "v4" { return "4.0.1" }
    "v5" { return "5.0.0" }
    "v6" { return "6.0.0-ballot3" }
    default { return $rawValue }
  }
}

function Set-IgFhirVersion {
  param(
    [string]$SushiConfigPath,
    [string]$FhirVersion
  )

  if (-not (Test-Path $SushiConfigPath)) {
    throw "Could not find sushi-config.yaml at path: $SushiConfigPath"
  }

  $content = Get-Content -Raw $SushiConfigPath
  $updated = [regex]::Replace($content, "(?m)^fhirVersion:\s*.*$", "fhirVersion: $FhirVersion")
  if ($updated -ne $content) {
    Set-Content -Path $SushiConfigPath -Value $updated -NoNewline
  }
}

if ($Mode -ne "stop" -and -not (Test-Path $IgPath)) {
  throw "Could not find IG folder '$IgFolder' at path: $IgPath"
}

if ($Mode -ne "stop" -and -not (Test-Path $EnvFilePath)) {
  throw "Could not find env file '$EnvFile' at path: $EnvFilePath"
}

if ($Mode -ne "stop") {
  $selectedFhirVersion = Get-FhirVersion -Path $EnvFilePath
  Set-IgFhirVersion -SushiConfigPath (Join-Path $IgPath "sushi-config.yaml") -FhirVersion $selectedFhirVersion
}

switch ($Mode) {
  "start" {
    Invoke-DockerCommand -Description "docker compose build ig-publisher" -Command {
      docker compose --env-file $EnvFilePath -f $ComposeFile build ig-publisher
    }

    if (Test-ContainerExists -Name $ContainerName) {
      Invoke-DockerCommand -Description "docker rm -f $ContainerName" -Command {
        docker rm -f $ContainerName | Out-Null
      }
    }

    Invoke-DockerCommand -Description "docker compose run (start alive container)" -Command {
      docker compose --env-file $EnvFilePath -f $ComposeFile run -d --name $ContainerName --volume "${IgPath}:/usr/src/ig" --entrypoint $KeepAliveCommand ig-publisher | Out-Null
    }

    Write-Host "Container '$ContainerName' is running and mounted to /usr/src/ig."
    Write-Host "Run SUSHI: .\scripts\run-ig-cli.ps1 -Mode sushi -IgFolder $IgFolder"
    Write-Host "Run SUSHI + Publisher: .\scripts\run-ig-cli.ps1 -Mode sushi-publisher -IgFolder $IgFolder"
    Write-Host "Stop container: .\scripts\run-ig-cli.ps1 -Mode stop"
  }
  "sushi" {
    Assert-ContainerRunning -Name $ContainerName
    Invoke-SushiCommand -Name $ContainerName
  }
  "publisher" {
    Assert-ContainerRunning -Name $ContainerName
    Invoke-PublisherCommand -Name $ContainerName
  }
  "sushi-publisher" {
    Assert-ContainerRunning -Name $ContainerName
    Invoke-SushiCommand -Name $ContainerName
    Invoke-PublisherCommand -Name $ContainerName
  }
  "stop" {
    if (Test-ContainerExists -Name $ContainerName) {
      Invoke-DockerCommand -Description "docker rm -f $ContainerName" -Command {
        docker rm -f $ContainerName | Out-Null
      }
      Write-Host "Container '$ContainerName' was removed."
    } else {
      Write-Host "Container '$ContainerName' does not exist."
    }
  }
}
