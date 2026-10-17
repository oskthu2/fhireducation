# FML-mappningar

| Fil | Innehåll |
|-----|----------|
| `patient.map` | Journalsystemets patient → FHIR `Patient` (profil EducationPatient). **Övning 5.2** |
| `besok.map` | Journalsystemets besök → FHIR `Encounter` (profil EducationEncounter). **Övning 5.3** |
| `logiska-modeller/JournalModeller.fsh` | Logiska modeller som beskriver journalsystemets JSON (källa) |
| `logiska-modeller/StructureDefinition-*.json` | Samma modeller som StructureDefinitions, genererade från FSH-filen |

## FML i korthet

```
map "<url>" = "<namn>"

conceptmap "kon" {                        // inbäddad ConceptMap för kodöversättning
  prefix s = "<källkodsystem>"
  prefix t = "<målkodsystem>"
  s:M == t:male
}

uses "<logisk modell>" alias JournalPatient as source
uses "http://hl7.org/fhir/StructureDefinition/Patient" alias Patient as target

group JournalPatientTillFhir(source src : JournalPatient, target tgt : Patient) {
  src.fodelsedatum as fd -> tgt.birthDate = fd "fodelsedatum";            // kopiera ett värde
  src.kon as kon -> tgt.gender = translate(kon, '#kon', 'code') "kon";    // översätt en kod
  src -> tgt.name as namn, namn.use = 'official' then {                  // skapa ett element och
    src.efternamn as e -> namn.family = e "efternamn";                    // fyll det med inre regler
  } "namn";
}
```

En regel har formen `källa -> mål "namn";`. Finns inte källelementet i JSON körs regeln inte, så inga tomma
element skapas.

Specifikation: <https://hl7.org/fhir/R4/mapping-language.html>

## Tekniska anmärkningar

- Mappningarna körs av `StructureMapUtilities` i HL7:s referensbibliotek (R4), se `mapping/FmlMotor.java`.
- R4-versionen av FML-parsern kräver ordningen `map`, `conceptmap`, `uses`, `group`, och stöder inte
  metadata-rader (`/// title = ...`) som finns i senare versioner av FML.
- Koder med bindestreck skrivs inom citattecken i en conceptmap, t.ex. `t:"in-progress"`.
- Resursens logiska `id` sätts av fasaden (i Java), eftersom det är serverns ansvar och inte mappningens.

## Ändra de logiska modellerna

Redigera `logiska-modeller/JournalModeller.fsh` och generera om JSON-filerna med snapshot:

```bash
mkdir -p /tmp/lm/input/fsh && cp logiska-modeller/JournalModeller.fsh /tmp/lm/input/fsh/
cat > /tmp/lm/sushi-config.yaml <<'YAML'
id: fhir.education.journalsystem
canonical: http://example.org/fhir/education/journalsystem
name: Journalsystem
status: draft
version: 0.1.0
fhirVersion: 4.0.1
FSHOnly: true
YAML
sushi build --snapshot /tmp/lm
cp /tmp/lm/fsh-generated/resources/StructureDefinition-Journal*.json logiska-modeller/
```
