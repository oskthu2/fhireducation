# Kursmaterial – FHIR i praktiken

Sex moduler à 50 minuter (plus 10 minuters paus mellan modulerna). Hela dagen följer samma två resurser,
**Patient** och **Encounter**, för testpersonen *Tolvan Tolvansson*. Kursens IG i `test-ig/` byggs ut steg för steg.

| # | Modul | Övningar | Lösning |
|---|-------|----------|---------|
| 1 | [Läsa en FHIR-resurs](modul-1-lasa-en-resurs/README.md) | Tolka en Patient, hitta felet i en Encounter | [facit](modul-1-lasa-en-resurs/facit.md) |
| 2 | [Profiler och Implementation Guides](modul-2-profiler-och-ig/README.md) | Läs en profil, vilken slice? | [facit](modul-2-profiler-och-ig/facit.md) |
| 3 | [FHIR Shorthand (FSH)](modul-3-fsh/README.md) | EducationEncounter, terminologi, extensions, slicing | [losningar/modul-3](losningar/modul-3/fsh/) |
| 4 | [FHIRPath och invarianter](modul-4-fhirpath/README.md) | FHIRPath Lab, egna invarianter | [facit](modul-4-fhirpath/facit.md), [losningar/modul-4](losningar/modul-4/fsh/) |
| 5 | [Utveckling med HAPI FHIR](modul-5-hapi-fhir/README.md) | Utforska ett FHIR-API, mappa ett fält i fasaden, scopes | [losningar/modul-5](losningar/modul-5/PatientMapper.java) |
| 6 | [Följsamhet och validering](modul-6-foljsamhet/README.md) | CapabilityStatement, validera instanser | [facit](modul-6-foljsamhet/facit.md), [losningar/modul-6](losningar/modul-6/fsh/) |

Presentationen finns i [`presentation/FHIR-utbildning.pptx`](../presentation/README.md).

## Förslag på schema

| Tid | Modul |
|-----|-------|
| 09.00 – 09.50 | 1 – Läsa en FHIR-resurs |
| 10.00 – 10.50 | 2 – Profiler och Implementation Guides |
| 11.00 – 11.50 | 3 – FHIR Shorthand (FSH) |
| 11.50 – 12.50 | Lunch |
| 12.50 – 13.40 | 4 – FHIRPath och invarianter |
| 13.50 – 14.40 | 5 – Utveckling med HAPI FHIR |
| 14.50 – 15.40 | 6 – Följsamhet och validering |

## Så byggs IG:n upp under dagen

| Läge | Innehåll i `test-ig/input/fsh` | Kom ikapp |
|------|--------------------------------|-----------|
| Start | `EducationPatient` (kardinalitet, Must Support) + exempel | `start` |
| Efter modul 3 | + `EducationEncounter`, `Kontakttyp` (CodeSystem/ValueSet), `EducationEncounterClassVS`, bindning till `marital-status`, extensions `tolkbehov` och `SkyddadIdentitet`, slicing av `identifier` | `3` |
| Efter modul 4 | + invarianter `edu-pat-1`, `edu-pat-2`, `edu-enc-1`, `edu-enc-2` | `4` |
| Efter modul 6 | + `EducationServerCapabilities` (CapabilityStatement, requirements) | `6` |

**Kom ikapp:** *Actions → Kom ikapp → Run workflow → välj läge*. Arbetsflödet ersätter
`test-ig/input/fsh` med lösningen, sparar deltagarens egna filer i `mina-filer/` och startar bygget.

## Checklista för kursledaren

**Någon vecka före kursen**

- [ ] Gör repot till en mall: *Settings → General → Template repository*.
- [ ] Kör *Actions → Kontrollera lösningar → Run workflow*. Det bygger alla lösningar med senaste IG Publisher och
      kontrollerar valideringsövningen. IG Publisher och FHIR-paketen uppdateras ofta, så kör den nära kursen.
- [ ] Skicka förberedelser till deltagarna: GitHub-konto, skapa repo från mallen och aktivera GitHub Pages
      (se [README](../README.md#spår-a-github-rekommenderat)).
- [ ] Kontrollera att deltagarnas nätverk når `github.com`, `*.github.io`, `hapi.fhir.org` och `fhirpath-lab.com`.

**Under kursen**

- Bygget tar 2–4 minuter. Uppmuntra deltagarna att samla flera ändringar per incheckning, eller använda
  github.dev (tryck `.` i repot) för att ändra flera filer i samma incheckning.
- Den som har problem med sitt repo kan följa med i ditt (visa på storskärm) och ta igen med *Kom ikapp*.
- Fel i FSH syns i steget *Kör SUSHI*. Fel i profiler och exempel syns i `qa.html` i den publicerade IG:n.
