function Get-FhirVersionFromEnvFile {
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

function Set-IgFhirVersionInSushiConfig {
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
