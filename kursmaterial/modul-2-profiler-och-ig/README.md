# Modul 2 – Profiler, Implementation Guides och verktyg

**Tid:** 50 min (≈ 30 min genomgång, 15 min övning, 5 min diskussion)

## Mål

Efter modulen kan du

- förklara vad en **profil** är (en `StructureDefinition` som begränsar eller utökar en basresurs)
- förklara vad en **Implementation Guide (IG)** är och vad den brukar innehålla
- läsa en profil i IG Publishers vyer: *Differential*, *Snapshot*, *Key Elements* och *Must Support*
- förstå **extensions** och **slicing** i en profil, och varför slice-namnen inte syns i instansen
- känna till de vanligaste verktygen för att profilera och validera

## Begrepp

| Begrepp | Kort förklaring |
|---------|-----------------|
| Profil | `StructureDefinition` med `derivation = constraint`. Begränsar kardinalitet, typer och värden, binder terminologi och lägger till extensions och invarianter |
| Differential | Bara det som profilen *ändrar* jämfört med basen |
| Snapshot | Hela den resulterande strukturen (bas + ändringar) |
| Must Support (MS) | Elementet måste kunna hanteras. **Exakt vad det innebär definieras i varje IG!** |
| Extension-definition | `StructureDefinition` med `type = Extension`. Har en `url` och en `context` (var den får användas) |
| Slicing | Dela upp ett upprepande element (t.ex. `identifier`) i namngivna delar (slices) med egna regler |
| Diskriminator | Hur en validator avgör vilken slice ett element tillhör (`value`, `pattern`, `type`, `profile`, `exists`) |
| Slicing-regler | `open` (andra element tillåts), `closed` (bara definierade slices), `openAtEnd` |
| IG | Paket med profiler, extensions, terminologi, exempel, CapabilityStatements och sidor. Publiceras som webbplats och som npm-paket (`package.tgz`) |
| Canonical URL | Globalt unik identifierare för en konformitetsresurs, t.ex. `http://example.org/fhir/education/kursig/StructureDefinition/EducationPatient` |

### Slicing – urvalet försvinner i instansen

En profil kan säga att `identifier` har en slice som heter `personnummer`. I själva instansen finns
**inget** som heter `personnummer`, bara en lista med identifierare:

```json
"identifier": [
  { "system": "http://electronichealth.se/identifier/personnummer", "value": "191212121212" }
]
```

Validatorn (och mottagaren) måste själv räkna ut vilken slice varje element hör till med hjälp
av **diskriminatorn**, här `value` på `system`. Det får konsekvenser:

- Diskriminatorn måste vara något som faktiskt finns i data och har ett **fast värde** i varje slice.
- Med `open` slicing hamnar ett element som inte matchar någon slice bland "övriga". Det valideras
  **inte** mot slicens regler, t.ex. vid ett felstavat `system`.
- Mottagaren kan inte förlita sig på ordningen (om inte `ordered = true`).
- Slicing är ett sätt att **beskriva** data. Det skapar ingen ny struktur.

## Terminologibindning i praktiken

En bindning i en profil är bara början. När data valideras används en **terminologiserver** (t.ex. tx.fhir.org,
eller en nationell/regional server) för att avgöra om en kod är giltig:

| Begrepp | Kort förklaring |
|---------|-----------------|
| `$expand` | Räknar fram alla koder i ett ValueSet (som kan vara definierat med regler, t.ex. *alla undertyper till X i SNOMED CT*) |
| `$validate-code` | Svarar på om en kod finns i ett kodsystem eller ValueSet, och om display-texten stämmer |
| `required` vid validering | Kod utanför ValueSet:et ger **fel** |
| `extensible` vid validering | Kod utanför ValueSet:et ger **varning** (validatorn kan inte avgöra om en passande kod fanns). En kod som påstår sig komma från kodsystemet men inte finns där ger **fel** |
| Versioner | Kodsystem och ValueSets har versioner. SNOMED CT har både version och *edition* (t.ex. svensk edition). Ange version när det spelar roll |
| Display | Fel display-text för en kod kan ge fel i valideringen (vi såg det själva med ICD-10) |

**Svenska kodverk** du stöter på: SNOMED CT (svensk edition), ICD-10-SE, ATC, NPU, KVÅ samt nationella kodverk
från Socialstyrelsen och Inera. HL7 Sveriges basprofiler binder t.ex. civilstånd till ett svenskt ValueSet.

Vid kravställning: ange **vilket ValueSet** (canonical URL och version), **vilken styrka**, och **vilken
terminologiserver** som gäller för validering.

## Verktyg

| Verktyg | Används till |
|---------|--------------|
| **FSH + SUSHI** | Skriva profiler som text och kompilera till FHIR-JSON (modul 3) |
| **IG Publisher** | Bygga en IG-webbplats och ett paket, med kvalitetsrapport (qa.html) |
| **Forge / Simplifier.net** | Grafisk profilering och publicering (Firely) |
| **FHIR Validator (validator_cli.jar)** | Validera instanser mot bas och profiler (modul 6) |
| **HAPI FHIR** | Java-bibliotek och server (modul 5) |
| **FHIRPath Lab** | Testa FHIRPath-uttryck (modul 4) |

## Övning 2.1 – Läs en profil (10 min)

Öppna profilen **EducationPatient** i **facit-IG:n** på din GitHub Pages-sida:

`https://<ditt-konto>.github.io/<repo>/facit/StructureDefinition-EducationPatient.html`

(Facit-IG:n är lösningen efter modul 6, alltså den profil vi själva bygger i modul 3 och 4. Den publiceras
automatiskt av arbetsflödet *Bygg IG*. Saknas den: *Actions → Bygg IG → Run workflow*.)

Använd flikarna **Differential Table**, **Snapshot Table** och **Key Elements Table** och jämför med
basresursen på <https://hl7.org/fhir/R4/patient.html>.

1. Vilken är profilens canonical URL? Vilken basresurs bygger den på?
2. Vilka element har fått en ändrad **kardinalitet**? Från vad till vad?
3. Vilka element är markerade **Must Support**? I vilken flik ser du det tydligast?
4. Vilken **terminologibindning** har ändrats, och till vilken styrka? Är ändringen tillåten?
5. Vilka **extensions** används? Vilken är egendefinierad och vilken kommer från FHIR-standarden?
6. Hur är `identifier` **slicad**? Vilken diskriminator används, och är slicingen öppen eller stängd?

*För den tekniskt intresserade:* samma profil (bara differential) finns som JSON i
[`exempel/StructureDefinition-EducationPatient.json`](exempel/StructureDefinition-EducationPatient.json).
Jämför JSON med Differential Table – vad lägger IG Publisher till för att göra den läsbar?

## Övning 2.2 – Vilken slice? (5 min)

Titta på [`exempel/Patient-identifierare.json`](exempel/Patient-identifierare.json). Den har fyra identifierare.

1. Vilken slice hamnar varje identifierare i (personnummer, samordningsnummer eller ingen)?
2. Är instansen giltig mot profilen? Vad händer med den fjärde identifieraren?
3. Vad skulle hända om slicingen var `closed`?

## Övning 2.3 – Titta på en riktig IG (om tid finns)

Bläddra i en publicerad IG och leta upp en Patient-profil, t.ex.:

- HL7 Sverige, basprofiler: <https://hl7.se/fhir/ig/base/>
- International Patient Summary: <https://hl7.org/fhir/uv/ips/>

Titta på flikarna *Differential Table*, *Snapshot Table* och *Key Elements Table*. Hitta slicing och extensions.

**Facit:** [facit.md](facit.md)
