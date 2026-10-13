# Modul 6 – Följsamhet, CapabilityStatement och validering

**Tid:** 50 min (≈ 20 min genomgång med demo, 25 min övningar, 5 min summering)

## Mål

Efter modulen kan du

- förklara vad det betyder att en lösning **följer** en IG, och hur Must Support och kardinalitet påverkar det
- läsa och skriva ett **CapabilityStatement** och skilja på `instance`, `capability` och `requirements`
- använda capability discovery (`/metadata`, `.well-known/smart-configuration`) för att ta reda på vad en server kan
- **validera** en instans mot en profil och tolka resultatet (OperationOutcome)
- känna till verktyg för konformitetstestning
- **kravställa** mot en IG med krav som går att verifiera

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

## Kravställa mot en IG

En IG blir ett krav först när kravställningen pekar ut den entydigt och säger hur följsamheten ska verifieras.

| Kravområde | Exempel på verifierbart krav | Verifieras med |
|------------|------------------------------|----------------|
| Vilken IG | Lösningen SKA följa `fhir.education.kursig` version `0.1.0` (canonical `http://example.org/fhir/education/kursig`) | Granskning |
| Beroenden | Profilerna SKA bygga på HL7 Sveriges basprofiler `hl7se.fhir.base#1.1.0` | Granskning av IG/paket |
| Data | Alla Patient- och Encounter-resurser SKA validera **utan fel** mot EducationPatient och EducationEncounter med HL7 FHIR Validator | FHIR Validator i test och CI |
| Must Support | Avsändaren SKA skicka alla MS-element när informationen finns. Mottagaren SKA kunna ta emot och visa dem | Testfall med fullständiga och ofullständiga data |
| API | Servern SKA uppfylla `EducationServerCapabilities` och ange det i `CapabilityStatement.instantiates` | `GET /metadata`, Inferno/Touchstone |
| Sökning | Servern SKA stödja `Encounter?patient=` och BÖR stödja `date` | Testfall, CapabilityStatement |
| Säkerhet | Åtkomst SKA kräva SMART Backend Services med scope `system/Encounter.rs` | Säkerhetstest |
| Terminologi | `Encounter.type` SKA kodas med ValueSet `…/ValueSet/kontakttyp-vs` version X | Validering mot terminologiserver |
| Förvaltning | Leverantören SKA stödja ny minor-version av IG:n inom N månader | Avtal |

Tumregler:

- Peka ut IG:n med **paket-id och version**, inte bara ett namn eller en länk.
- Skriv krav med **SKA / BÖR / KAN** (SHALL / SHOULD / MAY), och ange **hur** varje krav verifieras.
- Lägg krav på system i ett **CapabilityStatement** (`kind = requirements`) i IG:n, så att de blir maskinläsbara.
- Kräv att leverantören visar **valideringsresultat** och ett **CapabilityStatement** innan avtal och vid leverans.

## Demo 6.1 – Läs ett CapabilityStatement (kursledaren visar, 5 min)

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

## Övning 6.3 – Validera instanser mot profilen (10 min)

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

## Övning 6.4 – Formulera krav (5 min, i par)

Ni ska upphandla en tjänst som visar patientens vårdkontakter från flera vårdgivare.
Formulera **tre krav** som går att verifiera, med hjälp av tabellen ovan. För varje krav: *vad* ska gälla,
*vilken nivå* (SKA/BÖR) och *hur* det verifieras. Diskutera sedan: vilket av kraven skulle en leverantör
kunna tolka på mer än ett sätt?

**Facit:** [facit.md](facit.md)

## Avslutning – hur går jag vidare?

Se [Avslutning: ta hem miljön](../avslutning/README.md).
