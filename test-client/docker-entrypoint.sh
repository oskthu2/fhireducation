#!/bin/sh
set -eu

FHIR_VERSION="${FHIR_VERSION:-v4}"
SOURCE_BUNDLE="/opt/test-data/${FHIR_VERSION}/bundle.json"
TARGET_BUNDLE="/usr/share/nginx/html/bundle.json"
TEMPLATE_FILE="/usr/share/nginx/html/index.html.template"
TARGET_FILE="/usr/share/nginx/html/index.html"

if [ ! -f "$SOURCE_BUNDLE" ]; then
  echo "Unsupported FHIR_VERSION '$FHIR_VERSION'. Expected one of: v4, v5, v6." >&2
  exit 1
fi

cp "$SOURCE_BUNDLE" "$TARGET_BUNDLE"
envsubst '${FHIR_VERSION}' < "$TEMPLATE_FILE" > "$TARGET_FILE"
