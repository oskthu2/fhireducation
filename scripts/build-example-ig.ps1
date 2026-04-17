#!/usr/bin/env pwsh

param(
  [string]$IgFolder = "test-ig"
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$IgPath = Join-Path $RepoRoot $IgFolder

if (-not (Test-Path $IgPath)) {
  throw "Could not find IG folder '$IgFolder' at path: $IgPath"
}

docker compose -f (Join-Path $RepoRoot "docker-compose.yml") build ig-publisher
docker compose -f (Join-Path $RepoRoot "docker-compose.yml") run --volume "${IgPath}:/usr/src/ig" ig-publisher -ig /usr/src/ig/ig.ini
