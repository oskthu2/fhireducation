# Education Patient - FHIR-utbildning – Kurs-IG (facit) v0.1.0

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

* Referera till denna Profil: [Education Encounter](StructureDefinition-EducationEncounter.md)
* Exempel för denna Profil: [Patient/patient-tolvan](Patient-patient-tolvan.md)
* CapabilityStatements som använder denna Profil: [Krav på FHIR-server för Kurs-IG](CapabilityStatement-EducationServerCapabilities.md)

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
  "date" : "2026-10-13T17:29:30+00:00",
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
      "path" : "Patient",
      "constraint" : [{
        "key" : "edu-pat-1",
        "severity" : "error",
        "human" : "Ett personnummer ska bestå av exakt 12 siffror (ÅÅÅÅMMDDNNNN).",
        "expression" : "identifier.where(system = 'http://electronichealth.se/identifier/personnummer').all(value.matches('^[0-9]{12}$'))",
        "source" : "http://example.org/fhir/education/kursig/StructureDefinition/EducationPatient"
      },
      {
        "key" : "edu-pat-2",
        "severity" : "error",
        "human" : "Födelsedatum får inte ligga i framtiden.",
        "expression" : "birthDate.empty() or birthDate <= today()",
        "source" : "http://example.org/fhir/education/kursig/StructureDefinition/EducationPatient"
      }]
    },
    {
      "id" : "Patient.extension",
      "path" : "Patient.extension",
      "slicing" : {
        "discriminator" : [{
          "type" : "value",
          "path" : "url"
        }],
        "ordered" : false,
        "rules" : "open"
      }
    },
    {
      "id" : "Patient.extension:tolkbehov",
      "path" : "Patient.extension",
      "sliceName" : "tolkbehov",
      "min" : 0,
      "max" : "1",
      "type" : [{
        "code" : "Extension",
        "profile" : ["http://hl7.org/fhir/StructureDefinition/patient-interpreterRequired|5.3.0"]
      }],
      "mustSupport" : true
    },
    {
      "id" : "Patient.extension:skyddadIdentitet",
      "path" : "Patient.extension",
      "sliceName" : "skyddadIdentitet",
      "min" : 0,
      "max" : "1",
      "type" : [{
        "code" : "Extension",
        "profile" : ["http://example.org/fhir/education/kursig/StructureDefinition/SkyddadIdentitet"]
      }],
      "mustSupport" : true
    },
    {
      "id" : "Patient.identifier",
      "path" : "Patient.identifier",
      "slicing" : {
        "discriminator" : [{
          "type" : "value",
          "path" : "system"
        }],
        "description" : "Identifierare skiljs åt med hjälp av system.",
        "rules" : "open"
      },
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
      "id" : "Patient.identifier:personnummer",
      "path" : "Patient.identifier",
      "sliceName" : "personnummer",
      "short" : "Personnummer (12 siffror)",
      "min" : 0,
      "max" : "1",
      "mustSupport" : true
    },
    {
      "id" : "Patient.identifier:personnummer.system",
      "path" : "Patient.identifier.system",
      "patternUri" : "http://electronichealth.se/identifier/personnummer"
    },
    {
      "id" : "Patient.identifier:samordningsnummer",
      "path" : "Patient.identifier",
      "sliceName" : "samordningsnummer",
      "short" : "Samordningsnummer (12 siffror)",
      "min" : 0,
      "max" : "1",
      "mustSupport" : true
    },
    {
      "id" : "Patient.identifier:samordningsnummer.system",
      "path" : "Patient.identifier.system",
      "patternUri" : "http://electronichealth.se/identifier/samordningsnummer"
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
    },
    {
      "id" : "Patient.maritalStatus",
      "path" : "Patient.maritalStatus",
      "binding" : {
        "strength" : "required",
        "valueSet" : "http://hl7.org/fhir/ValueSet/marital-status"
      }
    }]
  }
}

```
