# Education Patient - FHIR-utbildning – Kurs-IG v0.1.0

* [**Table of Contents**](toc.md)
* [**Artifacts Summary**](artifacts.md)
* **Education Patient**

## Resource Profile: Education Patient 

| | |
| :--- | :--- |
| *Official URL*:http://example.org/fhir/education/kursig/StructureDefinition/EducationPatient | *Version*:0.1.0 |
| Draft as of 2026-10-13 | *Computable Name*:EducationPatient |

 
Patientprofil för FHIR-utbildningen. Profilen byggs ut steg för steg under kursen. 

**Användningar:**

* Exempel för denna Profil: [Patient/patient-tolvan](Patient-patient-tolvan.md)

Du kan också kontrollera [användningar i FHIR IG-statistiken](https://packages2.fhir.org/xig/fhir.education.kursig|current/StructureDefinition/EducationPatient)

### Formal Views of Profile Content

 [Description of Profiles, Differentials, Snapshots and how the different presentations work](http://build.fhir.org/ig/FHIR/ig-guidance/readingIgs.html#structure-definitions). 

 

Other representations of profile: [CSV](StructureDefinition-EducationPatient.csv), [Excel](StructureDefinition-EducationPatient.xlsx), [Schematron](StructureDefinition-EducationPatient.sch) 



## Resource Content

```json
{
  "resourceType" : "StructureDefinition",
  "id" : "EducationPatient",
  "url" : "http://example.org/fhir/education/kursig/StructureDefinition/EducationPatient",
  "version" : "0.1.0",
  "name" : "EducationPatient",
  "title" : "Education Patient",
  "status" : "draft",
  "date" : "2026-10-13T17:29:18+00:00",
  "publisher" : "FHIR-utbildning",
  "description" : "Patientprofil för FHIR-utbildningen. Profilen byggs ut steg för steg under kursen.",
  "jurisdiction" : [{
    "coding" : [{
      "system" : "urn:iso:std:iso:3166",
      "code" : "SE",
      "display" : "Sweden"
    }]
  }],
  "fhirVersion" : "4.0.1",
  "mapping" : [{
    "identity" : "rim",
    "uri" : "http://hl7.org/v3",
    "name" : "RIM Mapping"
  },
  {
    "identity" : "cda",
    "uri" : "http://hl7.org/v3/cda",
    "name" : "CDA (R2)"
  },
  {
    "identity" : "w5",
    "uri" : "http://hl7.org/fhir/fivews",
    "name" : "FiveWs Pattern Mapping"
  },
  {
    "identity" : "v2",
    "uri" : "http://hl7.org/v2",
    "name" : "HL7 v2 Mapping"
  },
  {
    "identity" : "loinc",
    "uri" : "http://loinc.org",
    "name" : "LOINC code for the element"
  }],
  "kind" : "resource",
  "abstract" : false,
  "type" : "Patient",
  "baseDefinition" : "http://hl7.org/fhir/StructureDefinition/Patient",
  "derivation" : "constraint",
  "differential" : {
    "element" : [{
      "id" : "Patient",
      "path" : "Patient"
    },
    {
      "id" : "Patient.identifier",
      "path" : "Patient.identifier",
      "min" : 1,
      "mustSupport" : true
    },
    {
      "id" : "Patient.identifier.system",
      "path" : "Patient.identifier.system",
      "min" : 1
    },
    {
      "id" : "Patient.identifier.value",
      "path" : "Patient.identifier.value",
      "min" : 1
    },
    {
      "id" : "Patient.name",
      "path" : "Patient.name",
      "min" : 1,
      "mustSupport" : true
    },
    {
      "id" : "Patient.name.family",
      "path" : "Patient.name.family",
      "min" : 1,
      "mustSupport" : true
    },
    {
      "id" : "Patient.name.given",
      "path" : "Patient.name.given",
      "mustSupport" : true
    },
    {
      "id" : "Patient.gender",
      "path" : "Patient.gender",
      "mustSupport" : true
    },
    {
      "id" : "Patient.birthDate",
      "path" : "Patient.birthDate",
      "min" : 1,
      "mustSupport" : true
    }]
  }
}

```
