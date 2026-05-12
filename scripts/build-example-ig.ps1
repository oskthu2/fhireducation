#!/usr/bin/env pwsh

param(
  [string]$IgFolder = "test-ig",
  [string]$EnvFile = ".env.fhir"
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$IgPath = Join-Path $RepoRoot $IgFolder
$ComposeFile = Join-Path $RepoRoot "docker-compose.yml"
$EnvFilePath = Join-Path $RepoRoot $EnvFile

if (-not (Test-Path $IgPath)) {
  throw "Could not find IG folder '$IgFolder' at path: $IgPath"
}

if (-not (Test-Path $EnvFilePath)) {
  throw "Could not find env file '$EnvFile' at path: $EnvFilePath"
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
  Set-Content -Path $SushiConfigPath -Value $updated
}

$selectedFhirVersion = Get-FhirVersion -Path $EnvFilePath
Set-IgFhirVersion -SushiConfigPath (Join-Path $IgPath "sushi-config.yaml") -FhirVersion $selectedFhirVersion

docker compose --env-file $EnvFilePath -f $ComposeFile build ig-publisher
docker compose --env-file $EnvFilePath -f $ComposeFile run --volume "${IgPath}:/usr/src/ig" ig-publisher -ig /usr/src/ig/ig.ini
