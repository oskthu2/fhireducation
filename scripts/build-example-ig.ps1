#!/usr/bin/env pwsh

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$IgPath = Join-Path $RepoRoot "test-ig"

if (-not (Test-Path $IgPath)) {
  throw "Could not find test-ig at path: $IgPath"
}

docker compose -f (Join-Path $RepoRoot "docker-compose.yml") build ig-publisher
docker compose -f (Join-Path $RepoRoot "docker-compose.yml") run --rm --volume "${IgPath}:/usr/src/ig" ig-publisher -ig /usr/src/ig
