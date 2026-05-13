# HAPI FHIR Sandbox – Inera Core testdata

En lokal FHIR R4-sandlåda med fem syntetiska testpatienter som följer [Inera Core Implementation Guide](https://inera.se/fhir/core) (se.inera.core v0.2.0).

## Kom igång

Kopiera env-filen och anpassa vid behov:

```bash
# Standardvärden finns i .env – redigera den för att ändra port eller FHIR-version
# Tillåtna värden för FHIR_VERSION: R4, R5
# (R6 är inte stabilt stödd i HAPI ännu)
notepad .env   # eller valfri editor
```

Starta sedan sandlådan:

```bash
bash start.sh
```

| Tjänst | URL |
|--------|-----|
| HAPI FHIR API | http://localhost:8080/fhir (eller `FHIR_API_PORT` i `.env`) |
| Webb-klient | http://localhost:3000 (eller `CLIENT_PORT` i `.env`) |

Webb-klienten visar aktiv FHIR-version som en grön badge i headern.

För att starta om med tom databas: `docker compose down && docker compose up -d`

## Testpatienter

| # | Namn | PNR | Diagnoser |
|---|------|-----|-----------|
| 1 | Arne Arnesson | 19420810-6593 | KOL (J44.1), Hjärtsvikt (I50.0), Diabetes T2 (E11.9), Hypertoni (I10), Förmaksflimmer (I48.0) |
| 2 | Britta Björk | 19550322-2340 | Reumatoid artrit (M05.8), Diabetes T2 (E11.9), Osteoporos (M81.0), Hypotyreos (E03.9) |
| 3 | Clas Carlsson | 19751115-1347 | Diabetes T1 (E10.9), Astma (J45.20), Celiaki (K90.0), Hypertoni (I10) |
| 4 | Diana Dahl | 19890603-2464 | Epilepsi (G40.3), GAD (F41.1), Migrän m aura (G43.1) |
| 5 | Erik Eriksson | 20050825-1238 | Astma (J45.20), Allergisk rinit (J30.1), Jordnötsallergi |

## Datakällor och profiler

- **Diagnoser**: ICD-10 (`http://hl7.org/fhir/sid/icd-10`)
- **Läkemedel**: ATC (`http://www.whocc.no/atc`)
- **Lab**: NPU (`urn:oid:1.2.752.108.1`) + LOINC
- **Vitalparametrar**: LOINC + UCUM
- **Patientidentifierare**: `http://terminology.hl7.se/sid/se-personnummer`
- **HSA-id**: `http://terminology.hl7.se/sid/se-hsaid-organization`

Alla resurser deklarerar relevanta Inera Core-profiler i `meta.profile`.

## Datafiler

Testdata finns per FHIR-version under `data/r4/`, `data/r5/` och `data/r6/`.

Den aktiva versionen väljs via `FHIR_VERSION` i `.env`.

Huvudsaklig skillnad mellan versioner:
- **R4**: `MedicationStatement` med `medicationCodeableConcept` och `reasonReference`
- **R5**: `MedicationStatement` med uppdaterade fältnamn (`medication.concept`, `reason` som CodeableReference) och nya statuskoder
- **R6**: Samma struktur som R5 (R6 är fortfarande i draft)

```
data/
  r4/
    00-shared.json          # Organisation, Läkare, Befattning
    01-arne-arnesson.json
    ...
  r5/                       # Uppdaterade fältnamn och statuskoder (R5-spec)
    ...
  r6/                       # Samma som r5
    ...
```

För att ladda om data manuellt:
```bash
docker compose run --rm fhir-loader
```