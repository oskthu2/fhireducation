#!/usr/bin/env bash
# Bygger en IG med SUSHI och IG Publisher.
#
# Används av GitHub Actions (.github/workflows/build-ig.yml) men kan också köras
# lokalt på Linux, macOS, WSL eller i GitHub Codespaces:
#
#   ./scripts/build-ig.sh                 # bygger test-ig
#   ./scripts/build-ig.sh min-nya-ig      # bygger en annan IG-mapp
#   ./scripts/build-ig.sh test-ig --sushi-only       # bara SUSHI (snabbt)
#   ./scripts/build-ig.sh test-ig --publisher-only   # bara IG Publisher
#
# Kräver: Java 17+, Node.js (SUSHI) och Ruby/Jekyll (IG Publisher).
set -euo pipefail

IG_FOLDER="test-ig"
SUSHI_ONLY=false
PUBLISHER_ONLY=false
for arg in "$@"; do
  case "$arg" in
    --sushi-only) SUSHI_ONLY=true ;;
    --publisher-only) PUBLISHER_ONLY=true ;;
    *) IG_FOLDER="$arg" ;;
  esac
done

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IG_PATH="$REPO_ROOT/$IG_FOLDER"
ENV_FILE="$REPO_ROOT/.env.fhir"
PUBLISHER_JAR="${PUBLISHER_JAR:-$REPO_ROOT/input-cache/publisher.jar}"
TX_SERVER="${TX_SERVER:-https://tx.fhir.org}"

[ -d "$IG_PATH" ] || { echo "Hittar inte IG-mappen: $IG_PATH" >&2; exit 1; }

# 1. FHIR-version från .env.fhir (samma logik som PowerShell-skripten).
if [ -f "$ENV_FILE" ]; then
  RAW_VERSION="$(grep -E '^\s*FHIR_VERSION\s*=' "$ENV_FILE" | head -1 | cut -d= -f2 | tr -d '[:space:]' | tr '[:upper:]' '[:lower:]' || true)"
  case "$RAW_VERSION" in
    v4) FHIR_VERSION="4.0.1" ;;
    v5) FHIR_VERSION="5.0.0" ;;
    v6) FHIR_VERSION="6.0.0-ballot3" ;;
    *) FHIR_VERSION="$RAW_VERSION" ;;
  esac
  if [ -n "$FHIR_VERSION" ]; then
    echo "FHIR-version från .env.fhir: $FHIR_VERSION"
    sed -i.bak -E "s/^fhirVersion:.*/fhirVersion: $FHIR_VERSION/" "$IG_PATH/sushi-config.yaml"
    rm -f "$IG_PATH/sushi-config.yaml.bak"
  fi
fi

# 2. SUSHI: FSH -> FHIR-resurser (JSON) i fsh-generated/
if [ "$PUBLISHER_ONLY" = false ]; then
  echo "::group::SUSHI"
  sushi build "$IG_PATH"
  echo "::endgroup::"
fi

if [ "$SUSHI_ONLY" = true ]; then
  exit 0
fi

# 3. IG Publisher: FHIR-resurser + sidor -> färdig webbplats i output/
if [ ! -s "$PUBLISHER_JAR" ]; then
  echo "Laddar ner IG Publisher..."
  mkdir -p "$(dirname "$PUBLISHER_JAR")"
  curl -fsSL https://github.com/HL7/fhir-ig-publisher/releases/latest/download/publisher.jar -o "$PUBLISHER_JAR"
fi

publish() {
  java -Xmx4g -jar "$PUBLISHER_JAR" -ig "$IG_PATH/ig.ini" "$@"
}

echo "::group::IG Publisher"
if publish -tx "$TX_SERVER"; then
  echo "Bygget lyckades."
else
  echo "Första försöket misslyckades (ofta tillfälligt fel mot terminologiservern). Försöker igen om 30 s..."
  sleep 30
  if publish -tx "$TX_SERVER"; then
    echo "Bygget lyckades vid andra försöket."
  else
    echo "::warning::Terminologiservern svarar inte – bygger utan terminologivalidering (-tx n/a)."
    publish -tx n/a
  fi
fi
echo "::endgroup::"
