# Modul 3 – FHIR Shorthand (FSH)

**Tid:** 50 min (≈ 15 min genomgång, 30 min övningar, 5 min summering)

## Mål

Efter modulen kan du

- läsa och skriva FSH: `Profile`, `Extension`, `ValueSet`, `CodeSystem`, `Instance` och `Alias`
- skapa en enkel profil och se resultatet i den byggda IG:n
- binda ett element till ett ValueSet, både ett eget (med `include`) och ett befintligt (med referens)
- lägga till extensions och slicing i en profil

## Arbetssätt

Alla övningar görs i **ditt eget repo på GitHub**:

1. Öppna filen i `test-ig/input/fsh/` och klicka på pennan (✏️), eller tryck `.` för att öppna webbeditorn github.dev.
2. Gör ändringen och klicka **Commit changes**.
3. Gå till fliken **Actions** och följ bygget **Bygg IG** (≈ 2–4 min).
   - Rött kryss i steget *Kör SUSHI* betyder fel i FSH-koden. Felet står med fil och rad i loggen.
   - Grön bock: öppna din IG på GitHub Pages (länk i körningens sammanfattning) och titta på profilen.

> Har du hamnat efter? Kör **Actions → Kom ikapp → Run workflow** och välj modul `3`.
> Det ersätter dina FSH-filer med lösningen. Dina egna filer sparas i `mina-filer/`.

## FSH i korthet

```fsh
Alias: $personnummer = http://electronichealth.se/identifier/personnummer

Profile: EducationPatient          // namn på profilen
Parent: Patient                    // basresurs eller annan profil
Id: EducationPatient               // id -> del av canonical URL
Title: "Education Patient"
Description: "Beskrivning ..."

* name 1..* MS                     // kardinalitet + Must Support
* gender from http://hl7.org/fhir/ValueSet/administrative-gender (required)  // bindning
* birthDate obeys edu-pat-2        // invariant (modul 4)
* identifier.system = $personnummer // fast värde (pattern)
* deceased[x] only boolean         // begränsa datatyp
* extension contains MinExtension named minExt 0..1   // extension
* ^status = #draft                 // sätt metadata på själva StructureDefinition (^)
```

## Övning 3.1 – Titta på startprofilen (5 min)

Öppna `test-ig/input/fsh/profiles/EducationPatient.fsh` och `examples/patient-tolvan.fsh`.

1. Vilka element har profilen ändrat kardinalitet på?
2. Öppna profilen i din publicerade IG. Jämför flikarna **Differential** och **Snapshot**.
3. Varför står inte `meta.profile` i exempel-FSH:en, men i den genererade JSON:en?

## Övning 3.2 – Skapa profilen EducationEncounter (10 min)

Skapa filen `test-ig/input/fsh/profiles/EducationEncounter.fsh` med en profil på `Encounter` som

- har `Parent: Encounter`, `Id: EducationEncounter` och en titel och beskrivning
- kräver exakt en `type`, en `subject`, en `period` med `period.start` och en `serviceProvider` (alla MS)
- begränsar `subject` till `Reference(EducationPatient)`
- markerar `status`, `class` och `reasonCode` som Must Support

Lägg också till ett exempel i `examples/encounter-tolvan-1.fsh` (`InstanceOf: EducationEncounter`) som refererar till
`patient-tolvan` med `* subject = Reference(patient-tolvan)`.

<details><summary>Tips</summary>

```fsh
* subject 1..1 MS
* subject only Reference(EducationPatient)
* period.start 1..1 MS
```
</details>

## Övning 3.3 – Terminologibindning (10 min)

**a) Eget kodsystem och ValueSet som inkluderar koder (`include`)**

Skapa `test-ig/input/fsh/terminology/Kontakttyp.fsh` med

- ett `CodeSystem: KontakttypCS` (`Id: kontakttyp`) med koderna `besok`, `hembesok`, `video` och `telefon`
- ett `ValueSet: KontakttypVS` som inkluderar **hela** kodsystemet: `* include codes from system KontakttypCS`
- ett `ValueSet: EducationEncounterClassVS` som räknar upp **enskilda** koder ur HL7 v3 ActCode:
  `* include $v3-ActCode#AMB "ambulatory"` (och `IMP`, `EMER`, `HH`, `VR`)

Bind sedan i EducationEncounter:

```fsh
* type from KontakttypVS (extensible)
* class from EducationEncounterClassVS (required)
```

**b) Bindning genom referens till ett befintligt ValueSet**

I EducationPatient: skärp bindningen av civilstånd genom att referera till FHIR:s eget ValueSet:

```fsh
* maritalStatus from http://hl7.org/fhir/ValueSet/marital-status (required)
```

Diskutera: Vad är skillnaden mellan att definiera ett eget ValueSet och att referera till ett befintligt?
Vem äger och förvaltar ValueSet:et? Vad händer när det uppdateras?

## Övning 3.4 – Extensions (5–10 min)

1. Använd en **befintlig** extension från FHIR-standarden för tolkbehov:
   ```fsh
   * extension contains $patient-interpreterRequired named tolkbehov 0..1 MS
   ```
2. Skapa en **egen** extension i `test-ig/input/fsh/extensions/SkyddadIdentitet.fsh`:
   ```fsh
   Extension: SkyddadIdentitet
   Id: SkyddadIdentitet
   Title: "Skyddad identitet"
   Description: "Anger om patienten har skyddade personuppgifter."
   Context: Patient
   * value[x] 1..1
   * value[x] only boolean
   ```
   och lägg till den i profilen med `SkyddadIdentitet named skyddadIdentitet 0..1 MS`.
3. Sätt värden i exemplet: `* extension[tolkbehov].valueBoolean = false`.

Diskutera: Borde skyddad identitet uttryckas med `meta.security` i stället? Vad är för- och nackdelarna?

## Övning 3.5 – Slicing (5–10 min)

Dela upp `identifier` i EducationPatient i två slices, personnummer och samordningsnummer:

```fsh
* identifier ^slicing.discriminator.type = #value
* identifier ^slicing.discriminator.path = "system"
* identifier ^slicing.rules = #open
* identifier contains
    personnummer 0..1 MS and
    samordningsnummer 0..1 MS
* identifier[personnummer].system = $personnummer
* identifier[samordningsnummer].system = $samordningsnummer
```

Ändra exemplet så att det använder slicen: `* identifier[personnummer].value = "191212121212"`.

Titta på resultatet: syns ordet `personnummer` någonstans i exemplets JSON (fliken *JSON* på exempelsidan)?

## Lösning

Den fullständiga lösningen finns i [`../losningar/modul-3/fsh/`](../losningar/modul-3/fsh/).

## Mer att läsa

- FSH School: <https://fshschool.org> (bl.a. FSH Online, en "lekplats" i webbläsaren)
- FSH-specifikationen: <https://build.fhir.org/ig/HL7/fhir-shorthand/>
