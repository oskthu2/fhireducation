# Facit – Modul 2

## Övning 2.1 – Läs en profil

(Facit-IG:n innehåller också invarianterna från modul 4. Dem tittar vi på i modul 4.)

1. `url` = `http://example.org/fhir/education/kursig/StructureDefinition/EducationPatient`.
   `baseDefinition` = `http://hl7.org/fhir/StructureDefinition/Patient`, alltså basresursen Patient.
2. - `identifier` 0..\* → **1..\***
   - `identifier.system` 0..1 → **1..1** och `identifier.value` 0..1 → **1..1**
   - `name` 0..\* → **1..\***, `name.family` 0..1 → **1..1**
   - `birthDate` 0..1 → **1..1**
   - Slices och extensions får egna kardinaliteter (0..1).
   - Snapshot Table visar hela strukturen, och Key Elements Table visar de obligatoriska och Must Support-markerade elementen.
3. `identifier` (och båda slices), `name`, `name.family`, `name.given`, `gender`, `birthDate` och båda extensions.
   Tydligast i Key Elements Table eller Differential Table (flaggan **S**).
4. `maritalStatus` binds till `http://hl7.org/fhir/ValueSet/marital-status` med styrkan `required`. I basen är den
   `extensible`. Det är tillåtet att **skärpa** en bindning, men inte att lätta på den.
5. `http://hl7.org/fhir/StructureDefinition/patient-interpreterRequired` kommer från FHIR-standarden.
   `.../StructureDefinition/SkyddadIdentitet` är egendefinierad. Båda läggs till som slices på `Patient.extension`.
   Där är diskriminatorn alltid `value` på `url`.
6. Diskriminator `value` på `system`, och slicingen är `open`. Slices: `personnummer` (system =
   `http://electronichealth.se/identifier/personnummer`) och `samordningsnummer`.

## Övning 2.2 – Vilken slice?

1. - `urn:oid:1.2.752.123.456.1` → **ingen slice** (tillåts eftersom slicingen är öppen)
   - `.../samordningsnummer` → **samordningsnummer**
   - `.../personnummer` → **personnummer**
   - `.../personummer` (felstavat!) → **ingen slice**
2. Ja, instansen är giltig. Den fjärde identifieraren matchar ingen slice och räknas som "övrig". Varken slicens
   regler eller invarianten `edu-pat-1` (som filtrerar på rätt system) fångar att värdet `19900101-2384` har fel format.
   **Lärdom:** öppen slicing är flexibel men fångar inte stavfel i diskriminatorn.
3. Med `closed` slicing blir instansen ogiltig, eftersom identifierare 1 och 4 inte matchar någon slice.
