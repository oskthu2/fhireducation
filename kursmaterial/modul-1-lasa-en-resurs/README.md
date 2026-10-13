# Modul 1 – Läsa en FHIR-resurs

**Tid:** 50 min (≈ 25 min genomgång, 20 min övning, 5 min summering)

## Mål

Efter modulen kan du

- känna igen strukturen i en FHIR-resurs: `resourceType`, `id`, `meta`, `text`, `extension` och resursens egna element
- skilja på primitiva och komplexa datatyper (t.ex. `string`, `date`, `Identifier`, `CodeableConcept`, `Reference`)
- förklara terminologibindning och de fyra bindningsstyrkorna (`required`, `extensible`, `preferred`, `example`)
- hitta och tolka extensions, både på resurser och på primitiva värden (`_birthDate`)
- förstå vad `meta.profile` betyder – och vad det *inte* betyder

## Begrepp att ha koll på

| Begrepp | Kort förklaring |
|---------|-----------------|
| Resurs | Minsta utbytbara informationsenhet, t.ex. `Patient`, `Encounter`, `Observation` |
| Element | Ett fält i en resurs. Har kardinalitet (t.ex. `0..1`, `1..*`) och datatyp |
| Primitiv datatyp | Enkla värden: `string`, `boolean`, `date`, `dateTime`, `code`, `uri` … |
| Komplex datatyp | Sammansatta värden: `Identifier`, `HumanName`, `CodeableConcept`, `Coding`, `Reference`, `Period` … |
| `meta` | Metadata: version, senast ändrad, profiler, säkerhetsmärkning och taggar |
| `text` | Människoläsbar sammanfattning (narrativ) i XHTML |
| Extension | Standardiserat sätt att lägga till information som inte finns i basresursen. Identifieras med `url` |
| modifierExtension | Extension som *ändrar betydelsen* av resursen – får inte ignoreras av mottagaren |
| Terminologibindning | Kopplar ett kodat element till ett ValueSet med en viss styrka |

### Bindningsstyrkor

| Styrka | Betydelse |
|--------|-----------|
| `required` | Koden **måste** komma från ValueSet:et. Inga undantag. |
| `extensible` | Använd en kod från ValueSet:et om det finns en som passar. Annars får annan kod användas. |
| `preferred` | Rekommenderat ValueSet, men andra koder är tillåtna. |
| `example` | Bara ett exempel på vilka koder som kan användas. |

## Övning 1.1 – Tolka en Patient (10 min)

Öppna [`exempel/Patient-tolvan.json`](exempel/Patient-tolvan.json) direkt här i GitHub.
Ta hjälp av specifikationen: <https://hl7.org/fhir/R4/patient.html>.

1. Vilken resurstyp och vilket logiskt id har resursen? Vilken version av resursen är det?
2. Vad står i `meta.profile`? Betyder det att resursen garanterat följer profilen?
3. Vilka **datatyper** har elementen `identifier`, `name`, `gender`, `birthDate`, `maritalStatus` och `generalPractitioner`?
4. Patienten har två identifierare. Vad skiljer dem åt? Vilken skulle du använda för att söka fram patienten i ett annat system?
5. Hitta alla **extensions**. Vilken är *enkel* och vilken är *komplex*? Vad betyder `_birthDate`?
6. `gender` har bindningen `required` i basspecifikationen. Vilka värden är tillåtna? Hur anger man att kön är okänt?
7. `maritalStatus` har bindningen `extensible`. Vad innebär det om ett svenskt system vill skicka "registrerat partnerskap"?
8. `generalPractitioner` och `managingOrganization` är båda referenser men ser olika ut. Vad är skillnaden?
9. Vad är `meta.security` till för? Och `meta.tag`?

## Övning 1.2 – Hitta felet i en Encounter (5–10 min)

Öppna [`exempel/Encounter-tolvan-1.json`](exempel/Encounter-tolvan-1.json) och
<https://hl7.org/fhir/R4/encounter.html>.

1. Vilken patient gäller vårdkontakten, och hur vet du det?
2. Vilken datatyp har `class` i R4? Och `type`? Varför skiljer de sig?
3. Resursen innehåller **ett fel** som gör den ogiltig mot FHIR-standarden. Hitta det!
   *Tips: titta på bindningsstyrkorna.*
4. `serviceProvider` saknar `reference`. Är det tillåtet? Vad är det för sorts referens?
5. Vilka kodsystem används i resursen? Vilka av dem är internationella och vilka är nationella?

**Facit:** [facit.md](facit.md) – titta efteråt!

## Extra (om du har tid)

- Prova FHIRPath Lab <https://fhirpath-lab.com>: klistra in Patient-resursen och testa uttrycket `name.where(use = 'official').given`.
- Jämför med samma resurs i XML-format på <https://hl7.org/fhir/R4/patient-example.xml.html>.
