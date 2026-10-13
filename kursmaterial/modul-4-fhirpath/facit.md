# Facit – Modul 4

## Övning 4.0

- `edu-pat-1` (error): ett personnummer ska bestå av exakt 12 siffror.
- `edu-pat-2` (error): födelsedatum får inte ligga i framtiden.
- Liksom `pat-1` består de av nyckel, nivå, beskrivning och ett FHIRPath-uttryck. `pat-1` gäller elementet
  `Patient.contact`, medan våra gäller hela resursen.

## Övning 4.1

| # | Uttryck | Resultat |
|---|---------|----------|
| 1 | `name.given` | `["Tolvan", "Bertil", "Tolle"]` – förnamn från **alla** namn, även smeknamnet |
| 2 | `name.where(use = 'official').family` | `["Tolvansson"]` |
| 3 | `identifier.where(system = '…/personnummer').value` | `["191212121212"]` |
| 4 | `extension('…/patient-interpreterRequired').value` | `[true]` |
| 5 | `telecom.where(system = 'phone').exists()` | `[true]` |
| 6 | `birthDate < @1950-01-01` | `[true]` |
| 7 | `communication.where(preferred = true).language.coding.code` | `["fi"]` |
| 8 | `identifier.where(system = 'http://electronichealth.se/identifier/personnummer').value.matches('^[0-9]{12}$')` | `[true]` |

Extra: extensionen på det primitiva värdet nås med
`birthDate.extension('http://hl7.org/fhir/StructureDefinition/patient-birthTime').value` → `["1912-12-12T04:30:00+01:00"]`.

## Övning 4.2

Med värdet `19121212-1212` får man felet *Constraint failed: edu-pat-1: 'Ett personnummer ska bestå av exakt 12 siffror (ÅÅÅÅMMDDNNNN).'*
i qa.html (och från FHIR Validator).

Observera att `all()` på en tom lista ger `true`. En patient **utan** personnummer bryter alltså inte mot `edu-pat-1`.
Det är avsiktligt: det är kardinaliteten som styr *om* ett personnummer krävs, och invarianten styr *hur* det ser ut.
