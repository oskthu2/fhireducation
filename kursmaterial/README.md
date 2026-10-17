# Kursmaterial – FHIR i praktiken

Sex moduler à 50 minuter (plus 10 minuters paus mellan modulerna), en kort inledning och en avslutning. Hela dagen följer samma två resurser,
**Patient** och **Encounter**, för testpersonen *Tolvan Tolvansson*. Kursens IG i `test-ig/` byggs ut steg för steg.

| # | Modul | Övningar | Lösning |
|---|-------|----------|---------|
| 1 | [Läsa en FHIR-resurs](modul-1-lasa-en-resurs/README.md) | Tolka en Patient, hitta felet i en Encounter | [facit](modul-1-lasa-en-resurs/facit.md) |
| 2 | [Profiler och Implementation Guides](modul-2-profiler-och-ig/README.md) | Läs en profil, vilken slice? | [facit](modul-2-profiler-och-ig/facit.md) |
| 3 | [FHIR Shorthand (FSH)](modul-3-fsh/README.md) | EducationEncounter, terminologi, extensions, slicing | [losningar/modul-3](losningar/modul-3/fsh/) |
| 4 | [FHIRPath och invarianter](modul-4-fhirpath/README.md) | FHIRPath Lab, egna invarianter | [facit](modul-4-fhirpath/facit.md), [losningar/modul-4](losningar/modul-4/fsh/) |
| 5 | [Utveckling med HAPI FHIR](modul-5-hapi-fhir/README.md) | Utforska ett FHIR-API, lägg till en regel i FML-mappningen, ny kod i ConceptMap, scopes | [losningar/modul-5](losningar/modul-5/) |
| 6 | [Följsamhet och validering](modul-6-foljsamhet/README.md) | Kravställning, CapabilityStatement, validera instanser, formulera krav | [facit](modul-6-foljsamhet/facit.md), [losningar/modul-6](losningar/modul-6/fsh/) |
| – | [Avslutning: ta hem miljön](avslutning/README.md) | Lokal installation, starta en egen IG | |

**Facit-IG:** lösningen efter modul 6 publiceras automatiskt på `https://<konto>.github.io/<repo>/facit/`.
Den används i övning 2.1 och 4.0 för att läsa en profil i IG Publishers vyer.

Presentationen finns i [`presentation/FHIR-utbildning.pptx`](../presentation/README.md).

**Kursbok:** fördjupande texter till varje modul, kontrollfrågor och länkar för egna studier finns i
[`kursbok/`](../kursbok/README.md), publicerad på `https://<konto>.github.io/<repo>/kursbok/`.

## Förslag på schema

| Tid | Innehåll |
|-----|----------|
| 09.00 – 09.15 | Inledning: upplägg, röd tråd, kontroll av allas repon |
| 09.15 – 10.05 | 1 – Läsa en FHIR-resurs |
| 10.15 – 11.05 | 2 – Profiler och Implementation Guides |
| 11.15 – 12.05 | 3 – FHIR Shorthand (FSH) |
| 12.05 – 13.00 | Lunch |
| 13.00 – 13.50 | 4 – FHIRPath och invarianter |
| 14.00 – 14.50 | 5 – Utveckling med HAPI FHIR |
| 15.00 – 15.50 | 6 – Följsamhet, kravställning och validering |
| 15.50 – 16.05 | Avslutning: ta hem miljön, frågor och utvärdering |

## Så byggs IG:n upp under dagen

| Läge | Innehåll i `test-ig/input/fsh` | Kom ikapp |
|------|--------------------------------|-----------|
| Start | `EducationPatient` (kardinalitet, Must Support) + exempel | `start` |
| Efter övning 3.2 | + `EducationEncounter` (utan bindningar) + exempel med `type.text` | `3.2` |
| Efter modul 3 | + `Kontakttyp` (CodeSystem/ValueSet), `EducationEncounterClassVS`, bindning till `marital-status`, extensions `tolkbehov` och `SkyddadIdentitet`, slicing av `identifier` | `3` |
| Efter modul 4 | + invarianter `edu-pat-1`, `edu-pat-2`, `edu-enc-1`, `edu-enc-2` | `4` |
| Efter modul 6 | + `EducationServerCapabilities` (CapabilityStatement, requirements) | `6` |
| Extraövning 3.6 | + `EducationSEPatient` på HL7 Sveriges `SEBasePatient`, beroende till `hl7se.fhir.base` | `extra-hl7se` |

**Kom ikapp:** *Actions → Kom ikapp → Run workflow → välj läge*. Arbetsflödet ersätter
`test-ig/input/fsh` med lösningen, sparar deltagarens egna filer i `mina-filer/` och startar bygget.

## Checklista för kursledaren

**Någon vecka före kursen**

- [ ] Gör repot till en mall: *Settings → General → Template repository*.
- [ ] Kör *Actions → Bygg IG → Run workflow* på `main` så att facit-IG:n publiceras under `/facit/`.
- [ ] Kör *Actions → Kontrollera lösningar → Run workflow*. Det bygger alla lösningar med senaste IG Publisher och
      kontrollerar valideringsövningen. IG Publisher och FHIR-paketen uppdateras ofta, så kör den nära kursen.
- [ ] Skicka förberedelser till deltagarna: GitHub-konto, skapa repo från mallen och aktivera GitHub Pages
      (se [README](../README.md#spår-a-github-rekommenderat)).
- [ ] Kontrollera att deltagarnas nätverk når `github.com`, `*.github.io`, `hapi.fhir.org` och `fhirpath-lab.com`.

**Under kursen**

- Övning 3.4–3.5 är valfria under kurstiden. Den som inte hunnit dem kör *Kom ikapp → modul 3* före modul 4.
- Övning 6.1 är en demo: visa CapabilityStatement för fasaden (sammanfattningen i *HAPI-fasad*) och för
  `hapi.fhir.org/baseR4/metadata`.
- Hela bygget tar cirka 2 minuter, men steget *Kör SUSHI* är klart efter ungefär 30 sekunder. Lär deltagarna
  att titta där först: blir det grönt är FSH-koden korrekt.
- Uppmuntra deltagarna att samla flera ändringar per incheckning, eller använda
  github.dev (tryck `.` i repot) för att ändra flera filer i samma incheckning.
- Den som har problem med sitt repo kan följa med i ditt (visa på storskärm) och ta igen med *Kom ikapp*.
- Fel i FSH syns i steget *Kör SUSHI*. Fel i profiler och exempel syns i `qa.html` i den publicerade IG:n.
