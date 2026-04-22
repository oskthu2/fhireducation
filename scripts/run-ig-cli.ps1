#!/usr/bin/env pwsh

param(
  [string]$IgFolder = "test-ig",
  [ValidateSet("start", "sushi", "publisher", "sushi-publisher", "stop")]
  [string]$Mode = "start",
  [string]$ContainerName = "ig-publisher-cli"
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$ComposeFile = Join-Path $RepoRoot "docker-compose.yml"
$IgPath = Join-Path $RepoRoot $IgFolder

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
  return [bool](docker ps -a --filter "name=^/${Name}$" --format "{{.Names}}")
}

function Ensure-ContainerRunning {
  param([string]$Name)
  $isRunning = [bool](docker ps --filter "name=^/${Name}$" --format "{{.Names}}")
  if (-not $isRunning) {
    throw "Container '$Name' is not running. Start it first: .\scripts\run-ig-cli.ps1 -Mode start"
  }
}

if ($Mode -ne "stop" -and -not (Test-Path $IgPath)) {
  throw "Could not find IG folder '$IgFolder' at path: $IgPath"
}

switch ($Mode) {
  "start" {
    Invoke-DockerCommand -Description "docker compose build ig-publisher" -Command {
      docker compose -f $ComposeFile build ig-publisher
    }

    if (Test-ContainerExists -Name $ContainerName) {
      Invoke-DockerCommand -Description "docker rm -f $ContainerName" -Command {
        docker rm -f $ContainerName | Out-Null
      }
    }

    Invoke-DockerCommand -Description "docker compose run (start alive container)" -Command {
      docker compose -f $ComposeFile run -d --name $ContainerName --volume "${IgPath}:/usr/src/ig" --entrypoint "tail -f /dev/null" ig-publisher | Out-Null
    }

    Write-Host "Container '$ContainerName' is running and mounted to /usr/src/ig."
    Write-Host "Run SUSHI: .\scripts\run-ig-cli.ps1 -Mode sushi -IgFolder $IgFolder"
    Write-Host "Run SUSHI + Publisher: .\scripts\run-ig-cli.ps1 -Mode sushi-publisher -IgFolder $IgFolder"
    Write-Host "Stop container: .\scripts\run-ig-cli.ps1 -Mode stop"
  }
  "sushi" {
    Ensure-ContainerRunning -Name $ContainerName
    Invoke-DockerCommand -Description "docker exec sushi" -Command {
      docker exec $ContainerName sushi --out /usr/src/ig /usr/src/ig
    }
  }
  "publisher" {
    Ensure-ContainerRunning -Name $ContainerName
    Invoke-DockerCommand -Description "docker exec publisher" -Command {
      docker exec $ContainerName java -jar /app/publisher.jar -ig /usr/src/ig/ig.ini
    }
  }
  "sushi-publisher" {
    Ensure-ContainerRunning -Name $ContainerName
    Invoke-DockerCommand -Description "docker exec sushi" -Command {
      docker exec $ContainerName sushi --out /usr/src/ig /usr/src/ig
    }
    Invoke-DockerCommand -Description "docker exec publisher" -Command {
      docker exec $ContainerName java -jar /app/publisher.jar -ig /usr/src/ig/ig.ini
    }
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
