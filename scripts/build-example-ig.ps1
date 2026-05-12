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

. (Join-Path $PSScriptRoot "fhir-version-utils.ps1")

if (-not (Test-Path $IgPath)) {
  throw "Could not find IG folder '$IgFolder' at path: $IgPath"
}

if (-not (Test-Path $EnvFilePath)) {
  throw "Could not find env file '$EnvFile' at path: $EnvFilePath"
}

$selectedFhirVersion = Get-FhirVersionFromEnvFile -Path $EnvFilePath
Set-IgFhirVersionInSushiConfig -SushiConfigPath (Join-Path $IgPath "sushi-config.yaml") -FhirVersion $selectedFhirVersion

docker compose --env-file $EnvFilePath -f $ComposeFile build ig-publisher
docker compose --env-file $EnvFilePath -f $ComposeFile run --volume "${IgPath}:/usr/src/ig" ig-publisher -ig /usr/src/ig/ig.ini
