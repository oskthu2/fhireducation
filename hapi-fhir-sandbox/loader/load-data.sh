#!/bin/sh
# Loads all FHIR JSON files from /data into the FHIR server.
# Transaction Bundles are POSTed to the base URL.
# Individual resources are POSTed to /{ResourceType}.

FHIR_URL="${FHIR_BASE_URL:-http://hapi-fhir:8080/fhir}"

echo "Waiting for FHIR server at $FHIR_URL ..."
retries=60
while [ "$retries" -gt 0 ]; do
  curl -sf -o /dev/null "$FHIR_URL/metadata" && break
  retries=$((retries - 1))
  printf "."
  sleep 5
done
[ "$retries" -eq 0 ] && { echo " timed out. Exiting."; exit 1; }
echo " ready!"
echo ""

loaded=0; failed=0; found=0

for file in /data/*.json; do
  [ -f "$file" ] || continue
  found=$((found + 1))
  name=$(basename "$file")
  printf "  Loading %s ... " "$name"

  rt=$(grep -o '"resourceType"[[:space:]]*:[[:space:]]*"[^"]*"' "$file" | \
       head -1 | sed 's/.*"\([A-Za-z]*\)".*/\1/')

  if [ "$rt" = "Bundle" ]; then
    url="$FHIR_URL"
  elif [ -n "$rt" ]; then
    url="$FHIR_URL/$rt"
  else
    echo "SKIPPED (could not determine resourceType)"
    continue
  fi

  code=$(curl -s -o /dev/null -w "%{http_code}" -X POST \
    -H "Content-Type: application/fhir+json" \
    --data-binary @"$file" "$url")

  if [ "$code" -ge 200 ] 2>/dev/null && [ "$code" -lt 300 ] 2>/dev/null; then
    echo "OK ($code)"; loaded=$((loaded + 1))
  else
    echo "FAILED ($code)"; failed=$((failed + 1))
  fi
done

if [ "$found" -eq 0 ]; then
  echo "No .json files found in /data/ — nothing to load."
  echo "Add FHIR JSON files to the data/ directory and restart."
fi

echo ""
echo "Done. Loaded: $loaded  Failed: $failed"
