# Facit – Modul 1

## Övning 1.1 – Patient

1. `resourceType` = `Patient`, `id` = `patient-tolvan`. `meta.versionId` = `3`, alltså den tredje versionen. `meta.lastUpdated` anger när den senast ändrades på servern.
2. `meta.profile` pekar på `EducationPatient`. Det är ett **påstående** från avsändaren om att resursen följer profilen. Det är inte en garanti: mottagaren måste validera för att veta. En resurs kan också följa en profil utan att den står i `meta.profile`.
3. - `identifier`: `Identifier` (komplex, 0..*)
   - `name`: `HumanName` (komplex, 0..*)
   - `gender`: `code` (primitiv, bindning `required` till AdministrativeGender)
   - `birthDate`: `date` (primitiv)
   - `maritalStatus`: `CodeableConcept` (komplex, en eller flera `Coding` + `text`)
   - `generalPractitioner`: `Reference(Organization | Practitioner | PractitionerRole)`
4. `system` skiljer dem åt: personnumret (`http://electronichealth.se/identifier/personnummer`) och ett lokalt patient-id med en OID. Personnumret är **globalt unikt** och fungerar mellan system. Det lokala id:t betyder bara något i det system som skapat det. `use` (`official`/`secondary`) hjälper också till.
5. - `patient-interpreterRequired` är **enkel**: den har en `valueBoolean`.
   - `patient-nationality` är **komplex**: den har inget eget värde, bara nästlade extensions (`code`).
   - `_birthDate` är en extension på ett **primitivt värde**. I JSON skrivs den som ett syskonelement med understreck. Här anger den födelsetiden med `patient-birthTime`.
6. `male | female | other | unknown`. Okänt kön anges med `unknown`. Svenska begrepp som "juridiskt kön" kräver en extension eller en profil.
7. `extensible`: finns det en passande kod i ValueSet:et ska den användas. Finns det ingen (som "registrerat partnerskap" i en svensk kontext) får man använda en annan kod, t.ex. ur ett nationellt kodverk.
8. `generalPractitioner` är en **bokstavlig (literal) referens** (`reference` = `Organization/vardcentralen-kurskoping`) som pekar på en resurs med id. `managingOrganization` är en **logisk referens** (`identifier` med HSA-id) som identifierar organisationen utan att peka på en resurs. `display` är bara text för människor.
9. `meta.security` innehåller säkerhetsmärkning, t.ex. sekretessnivå (`N` = normal), och kan användas av behörighetssystem. `meta.tag` är fria etiketter för arbetsflöden, t.ex. "testdata". De påverkar inte hur resursen ska tolkas.

## Övning 1.2 – Encounter

1. `subject.reference` = `Patient/patient-tolvan`.
2. I R4 är `class` en `Coding` (en kod) och `type` är `CodeableConcept` (0..*). `class` är en grov klassificering (öppenvård/slutenvård/hemsjukvård …) och `type` är mer specifik. (I R5 blev `class` ett `CodeableConcept`.)
3. **Felet:** `status` = `"avslutad"`. `Encounter.status` har bindningen `required` till EncounterStatus. Tillåtna värden är `planned | arrived | triaged | in-progress | onleave | finished | cancelled | entered-in-error | unknown`. Rätt värde är `finished`.
4. Ja. `Reference` kan innehålla `reference`, `identifier` och/eller `display`. Här är det en **logisk referens** via HSA-id.
5. - Internationella: SNOMED CT (`http://snomed.info/sct`), HL7 v3 ActCode, ActPriority och ParticipationType (`terminology.hl7.org`), ICD-10 (`http://hl7.org/fhir/sid/icd-10`)
   - Nationella: HSA-id (`urn:oid:1.2.752.29.4.19`, OID för HSA-katalogen, samma som i HL7 Sveriges basprofiler). I Sverige används ofta ICD-10-SE i stället för WHO:s ICD-10.
