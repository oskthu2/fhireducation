# Facit – Modul 6

## Demo 6.1

1. Fasaden: `kind = instance` (en driftsatt server). Den publika HAPI-servern: `instance`. Båda R4 (`4.0.1`).
2. `read` och `search-type`. Nej, `create` finns inte. Det syns i CapabilityStatement eftersom fasaden saknar en `@Create`-metod.
3. `patient` och `date`.
4. `supportedProfile` = EducationPatient respektive EducationEncounter.
   `implementationGuide` = kursens IG. `instantiates` = kursens requirements-CapabilityStatement (övning 6.2).
5. Klienten hämtar `/metadata` och kontrollerar `fhirVersion`, `rest.resource.type`, `interaction`, `searchParam`
   och gärna `instantiates` och `supportedProfile`. Det kallas *capability discovery*. För säkerhet läser man
   `.well-known/smart-configuration`.

## Övning 6.3

Alla filer får också varningen **dom-6** ("A resource should have narrative"). Det är en best practice-regel
i basspecifikationen: resurser bör ha en människoläsbar `text`. Det är en varning, inte ett fel.

**`patient-fel.json`** – 5 fel

- `gender` = `kvinna`: inte ett giltigt värde i den required-bundna värdemängden AdministrativeGender. Ska vara `female`. (Två meddelanden.)
- `Patient.name.family`: minimum required = 1, but only found 0. Profilen kräver efternamn.
- `edu-pat-1`: personnumret `19121212-1212` har inte 12 siffror.
- `edu-pat-2`: födelsedatumet `2099-12-12` ligger i framtiden.

**`encounter-fel.json`** – 3 fel, 1 extra varning

- `Unknown code 'akutbesok'`: koden finns inte i kodsystemet Kontakttyp (**fel**).
- Varning: ingen coding kommer från `KontakttypVS`. Bindningen är `extensible`, så det hade varit tillåtet att använda en
  kod från ett *annat* kodsystem om ingen passande fanns, men en kod som påstår sig vara från Kontakttyp måste finnas där.
- `Encounter.serviceProvider: minimum required = 1`: profilen kräver vårdgivare.
- `edu-enc-1`: `status = finished` men `period.end` saknas.

**`patient-felstavat-system.json`** – giltig

Identifieraren har `system` = `…/personumer` (felstavat). Den matchar ingen slice, och slicingen är öppen.
Invarianten `edu-pat-1` filtrerar på det **rätta** systemet och hittar därför inget att kontrollera.
Resultatet blir att instansen är **giltig**, fast värdet `1912121212` har fel format och systemet inte finns.

**Lärdom:** Validering mot profil fångar mycket, men inte allt. Mottagaren behöver fortfarande verksamhetsregler,
och profilen kan behöva skärpas, t.ex. med en invariant som kräver att *minst en* identifierare har ett känt system:

```fsh
Invariant: edu-pat-3
Description: "Patienten ska ha personnummer eller samordningsnummer."
Expression: "identifier.where(system = 'http://electronichealth.se/identifier/personnummer' or system = 'http://electronichealth.se/identifier/samordningsnummer').exists()"
Severity: #error
```

## Övning 6.4 – Exempel på bra krav

| Krav | Nivå | Verifiering |
|------|------|-------------|
| Tjänsten SKA hämta vårdkontakter via FHIR R4 från servrar som uppfyller `EducationServerCapabilities` (`fhir.education.kursig#0.1.0`) | SKA | Kontroll av `instantiates` i varje servers `/metadata` |
| Alla Encounter-resurser som tjänsten skickar eller visar SKA validera utan fel mot `EducationEncounter` | SKA | FHIR Validator på testdata i CI och vid acceptanstest |
| Tjänsten SKA visa `period`, `type` och `serviceProvider` (Must Support) och BÖR visa `reasonCode` | SKA/BÖR | Testfall med och utan värden |

Vanliga otydligheter att diskutera: "stödja FHIR" (vilken version, vilka resurser, vilken IG?),
"hantera Must Support" (betyder det visa, lagra eller bara inte krascha?) och "följa HL7 Sverige"
(vilken version av basprofilerna?).
