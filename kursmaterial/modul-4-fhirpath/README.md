# Modul 4 – FHIRPath och invarianter

**Tid:** 50 min (≈ 20 min genomgång, 25 min övningar, 5 min summering)

## Mål

Efter modulen kan du

- skriva enkla FHIRPath-uttryck för att navigera, filtrera och testa data i en resurs
- läsa invarianter (constraints) i FHIR-specifikationen, t.ex. `pat-1` på Patient
- lägga till en egen invariant i en profil med FSH och se den slå till vid validering

## FHIRPath i korthet

| Uttryck | Betydelse |
|---------|-----------|
| `Patient.name.given` | Navigera: alla förnamn i alla namn |
| `name.where(use = 'official')` | Filtrera en lista |
| `name.exists()` / `name.empty()` | Finns det något / är det tomt? |
| `identifier.count()` | Antal element |
| `telecom.all(system.exists())` | Gäller villkoret för **alla** element? |
| `a implies b` | Om `a` är sant måste `b` vara sant |
| `value.matches('^[0-9]{12}$')` | Reguljärt uttryck |
| `birthDate <= today()` | Jämförelse med dagens datum |
| `extension('http://...').value` | Hämta värdet från en extension med viss url |
| `%resource` | Hela resursen (användbart i invarianter på element) |

> **Viktigt:** FHIRPath arbetar med *listor*. Ett uttryck som inte hittar något ger en tom lista, inte ett fel.
> En invariant räknas som uppfylld om uttrycket ger `true`.

### Exempel från specifikationen (Patient)

Se fliken *Constraints* på <https://hl7.org/fhir/R4/patient.html>:

| Nyckel | Uttryck | Betydelse |
|--------|---------|-----------|
| `pat-1` | `name.exists() or telecom.exists() or address.exists() or organization.exists()` | En kontaktperson (`Patient.contact`) ska ha minst ett namn, telecom, adress eller organisation |
| `ele-1` | `hasValue() or (children().count() > id.count())` | Alla element måste ha ett värde eller barn – tomma element är förbjudna |
| `ext-1` | `extension.exists() != value.exists()` | En extension har antingen ett värde eller nästlade extensions, aldrig båda |
| `dom-6` | `text.\`div\`.exists()` | Resursen bör ha en narrativ (best practice, varning) |

## Övning 4.0 – Läs invarianterna i facit-IG:n (3 min)

Öppna `https://<ditt-konto>.github.io/<repo>/facit/StructureDefinition-EducationPatient.html` och hitta
invarianterna `edu-pat-1` och `edu-pat-2` (längst ned i Differential Table eller i avsnittet *Constraints*).
Vad kontrollerar de? Vilken nivå (error/warning) har de? Jämför med `pat-1` i specifikationen.

## Övning 4.1 – Testa FHIRPath (10 min)

Öppna <https://fhirpath-lab.com/FhirPath> och klistra in
[`../modul-1-lasa-en-resurs/exempel/Patient-tolvan.json`](../modul-1-lasa-en-resurs/exempel/Patient-tolvan.json)
som resurs. Vad blir resultatet av:

1. `name.given`
2. `name.where(use = 'official').family`
3. `identifier.where(system = 'http://electronichealth.se/identifier/personnummer').value`
4. `extension('http://hl7.org/fhir/StructureDefinition/patient-interpreterRequired').value`
5. `telecom.where(system = 'phone').exists()`
6. `birthDate < @1950-01-01`
7. `communication.where(preferred = true).language.coding.code`
8. Skriv ett eget uttryck som returnerar `true` om patienten har ett personnummer med exakt 12 siffror.

## Övning 4.2 – Lägg till invarianter (15 min)

Skapa filen `test-ig/input/fsh/invariants.fsh`:

```fsh
Invariant: edu-pat-1
Description: "Ett personnummer ska bestå av exakt 12 siffror (ÅÅÅÅMMDDNNNN)."
Expression: "identifier.where(system = 'http://electronichealth.se/identifier/personnummer').all(value.matches('^[0-9]{12}$'))"
Severity: #error

Invariant: edu-enc-1
Description: "En avslutad vårdkontakt (status = finished) ska ha en sluttid (period.end)."
Expression: "status = 'finished' implies period.end.exists()"
Severity: #error
```

Koppla dem till profilerna:

```fsh
// i EducationPatient
* obeys edu-pat-1

// i EducationEncounter
* obeys edu-enc-1
```

Checka in och kontrollera att bygget blir grönt. Titta på fliken *Constraints* (eller tabellen i *Snapshot*)
på profilsidan.

**Testa att invarianten fungerar:** Ändra värdet i `examples/patient-tolvan.fsh` till `"19121212-1212"`.
Bygg och öppna **qa.html**. Vilket fel får du? Ändra sedan tillbaka.

## Övning 4.3 – Egna invarianter (extra)

Skriv själv:

- `edu-pat-2`: födelsedatum får inte ligga i framtiden
- `edu-enc-2` (varning): sluttiden ska inte ligga före starttiden

<details><summary>Förslag</summary>

```fsh
Invariant: edu-pat-2
Description: "Födelsedatum får inte ligga i framtiden."
Expression: "birthDate.empty() or birthDate <= today()"
Severity: #error

Invariant: edu-enc-2
Description: "Sluttiden bör inte ligga före starttiden."
Expression: "period.end.empty() or period.start <= period.end"
Severity: #warning
```
</details>

Diskutera: Vad ska stå i en invariant och vad passar bättre i en bindning, en kardinalitet eller i
verksamhetslogiken hos mottagaren?

## Lösning

[`../losningar/modul-4/fsh/`](../losningar/modul-4/fsh/). Kom ikapp: **Actions → Kom ikapp → modul 4**.
