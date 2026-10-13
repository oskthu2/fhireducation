# Modul 6 – Följsamhet, CapabilityStatement och validering

**Tid:** 50 min (≈ 20 min genomgång, 25 min övningar, 5 min avslutning)

## Mål

Efter modulen kan du

- förklara vad det betyder att en lösning **följer** en IG, och hur Must Support och kardinalitet påverkar det
- läsa och skriva ett **CapabilityStatement** och skilja på `instance`, `capability` och `requirements`
- använda capability discovery (`/metadata`, `.well-known/smart-configuration`) för att ta reda på vad en server kan
- **validera** en instans mot en profil och tolka resultatet (OperationOutcome)
- känna till verktyg för konformitetstestning

## Begrepp

| Begrepp | Kort förklaring |
|---------|-----------------|
| Konformitet | En instans är *giltig* mot en profil. Ett system *följer* en IG om det beter sig som IG:n kräver |
| CapabilityStatement `kind = instance` | Beskriver en faktisk, driftsatt server |
| `kind = capability` | Beskriver en mjukvaruprodukt (oavsett installation) |
| `kind = requirements` | Beskriver **krav**, t.ex. i en IG: "en server SKA stödja …" |
| `instantiates` | "Den här servern uppfyller kraven i …" (pekar på ett requirements-CapabilityStatement) |
| `implementationGuide` | Vilka IG:er servern följer |
| `supportedProfile` | Vilka profiler servern stöder för en resurstyp |
| Expectation-extension | `SHALL` / `SHOULD` / `MAY` på interaktioner och sökparametrar |
| OperationOutcome | Resurs med valideringsresultat: `severity` (fatal/error/warning/information), meddelande och plats |

### Validering i praktiken

| Verktyg | När |
|---------|-----|
| **IG Publisher (qa.html)** | Validerar alla exempel i IG:n vid varje bygge |
| **FHIR Validator** (`validator_cli.jar`) | Validera filer från kommandoraden eller i CI, mot valfria IG:er |
| **`$validate`** | Operation på en FHIR-server: `POST [bas]/Patient/$validate` |
| **validator.fhir.org** | Webbgränssnitt för FHIR Validator |
| **Inferno / Touchstone / AEGIS** | Testplattformar för API-beteende (sökning, säkerhet, CapabilityStatement) |

## Övning 6.1 – Läs ett CapabilityStatement (10 min)

Jämför två CapabilityStatement:

- Kursens fasad: öppna senaste körningen av arbetsflödet **HAPI-fasad** under *Actions* och läs tabellen i sammanfattningen,
  eller `http://localhost:8080/fhir/metadata` i Codespaces
- Publika HAPI-servern: <https://hapi.fhir.org/baseR4/metadata>

1. Vilken `kind` har de? Vilken FHIR-version?
2. Vilka interaktioner stöder fasaden för `Patient`? Kan man skapa (`create`) patienter?
3. Vilka sökparametrar stöds för `Encounter`?
4. Vilka profiler (`supportedProfile`) och vilken IG anger fasaden? Vad pekar `instantiates` på?
5. Om du skulle bygga en klient: hur kan klienten med hjälp av `/metadata` ta reda på om servern stöder det klienten behöver?

## Övning 6.2 – Skriv kraven som ett CapabilityStatement (10 min)

Skapa `test-ig/input/fsh/capabilities/EducationServerCapabilities.fsh`: ett CapabilityStatement med
`kind = #requirements` som säger att en server

- SKA (`SHALL`) stödja `read` och `search-type` för `Patient` (profil EducationPatient) med sökparametern `identifier`
- SKA stödja `read` och `search-type` för `Encounter` (profil EducationEncounter) med sökparametern `patient`
- BÖR (`SHOULD`) stödja sökparametern `date` för `Encounter`

Börja så här och fyll i resten:

```fsh
Alias: $expectation = http://hl7.org/fhir/StructureDefinition/capabilitystatement-expectation

Instance: EducationServerCapabilities
InstanceOf: CapabilityStatement
Usage: #definition
* name = "EducationServerCapabilities"
* status = #draft
* date = "2026-10-13"
* kind = #requirements
* fhirVersion = #4.0.1
* format[0] = #json
* rest[0].mode = #server
* rest[0].resource[0].type = #Patient
* rest[0].resource[0].supportedProfile = Canonical(EducationPatient)
* rest[0].resource[0].interaction[0].code = #read
* rest[0].resource[0].interaction[0].extension[$expectation].valueCode = #SHALL
```

Checka in och titta på sidan för CapabilityStatement i din IG. Lösning:
[`../losningar/modul-6/fsh/capabilities/`](../losningar/modul-6/fsh/capabilities/EducationServerCapabilities.fsh).

## Övning 6.3 – Validera instanser mot profilen (15 min)

Mappen `validering/` i repots rot valideras automatiskt av arbetsflödet **Validera instanser** varje gång du
checkar in en fil där. Resultatet visas som en tabell i körningens sammanfattning.

> Förutsätter att din IG innehåller EducationEncounter och invarianterna från modul 4.
> Annars: **Actions → Kom ikapp → modul 4** (eller 6).

1. Kopiera innehållet i filerna i [`exempel/`](exempel/) till nya filer i `validering/`
   (*Add file → Create new file*, t.ex. `validering/patient-fel.json`) och checka in.
2. Öppna körningen av **Validera instanser**. Vilka fel hittade validatorn i
   - `patient-fel.json`?
   - `encounter-fel.json`?
   - `patient-felstavat-system.json`? Varför blev den (nästan) godkänd?
3. Rätta felen i `validering/patient-fel.json` och checka in igen tills den blir grön.
4. Diskutera: Vilka fel hade en mottagare kunnat leva med, och vilka måste avvisas? Vem ansvarar för valideringen,
   avsändaren eller mottagaren?

**Facit:** [facit.md](facit.md)

## Avslutning – hur går jag vidare?

- Skapa en ny IG: kopiera `test-ig`, ändra `id`, `canonical` och `name` i `sushi-config.yaml` och `ig.ini`
- HL7 Sverige: <https://hl7.se> – basprofiler och nationella riktlinjer
- Inera: FHIR-IG:er och mall-repo för IG-utveckling
- Chat: <https://chat.fhir.org> (Zulip) – strömmar för `#shorthand`, `#IG creation`, `#Sweden`
