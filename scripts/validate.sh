#!/usr/bin/env bash
# Validerar JSON-instanser mot kursens profiler med HL7 FHIR Validator.
#
# Används av GitHub Actions (.github/workflows/validera.yml) men kan också köras lokalt:
#
#   ./scripts/validate.sh                      # validerar alla filer i validering/
#   ./scripts/validate.sh validering/patient-ok.json
#
# Profilerna hämtas från SUSHI-resultatet i test-ig/fsh-generated/resources.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IG_FOLDER="${IG_FOLDER:-test-ig}"
VALIDATOR_JAR="${VALIDATOR_JAR:-$REPO_ROOT/input-cache/validator_cli.jar}"
TX_SERVER="${TX_SERVER:-https://tx.fhir.org}"
RESULT_FILE="${RESULT_FILE:-$REPO_ROOT/input-cache/validering-resultat.json}"

if [ "$#" -gt 0 ]; then
  FILES=("$@")
else
  shopt -s nullglob
  FILES=("$REPO_ROOT"/validering/*.json)
fi
if [ "${#FILES[@]}" -eq 0 ]; then
  echo "Inga filer att validera."
  exit 0
fi

# 1. Generera profilerna med SUSHI
"$REPO_ROOT/scripts/build-ig.sh" "$IG_FOLDER" --sushi-only

# 2. Hämta FHIR Validator vid behov
if [ ! -s "$VALIDATOR_JAR" ]; then
  echo "Laddar ner FHIR Validator..."
  mkdir -p "$(dirname "$VALIDATOR_JAR")"
  curl -fsSL https://github.com/hapifhir/org.hl7.fhir.core/releases/latest/download/validator_cli.jar -o "$VALIDATOR_JAR"
fi

FHIR_VERSION="$(grep -E '^fhirVersion:' "$REPO_ROOT/$IG_FOLDER/sushi-config.yaml" | awk '{print $2}')"
mkdir -p "$(dirname "$RESULT_FILE")"

# 3. Validera. Validatorn returnerar felkod om någon instans har fel – det hanterar sammanfattningen.
echo "::group::FHIR Validator"
set +e
java -Xmx4g -jar "$VALIDATOR_JAR" "${FILES[@]}" \
  -version "$FHIR_VERSION" \
  -ig "$REPO_ROOT/$IG_FOLDER/fsh-generated/resources" \
  -tx "$TX_SERVER" \
  -output "$RESULT_FILE"
set -e
echo "::endgroup::"

# 4. Sammanfatta resultatet (och skriv till GitHub-sammanfattningen om den finns)
python3 "$REPO_ROOT/scripts/summarize-validation.py" "$RESULT_FILE"
