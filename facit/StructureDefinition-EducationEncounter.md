# Education Encounter - FHIR-utbildning – Kurs-IG (facit) v0.1.0

* [**Table of Contents**](toc.md)
* [**Artifacts Summary**](artifacts.md)
* **Education Encounter**

## Resource Profile: Education Encounter 

| | |
| :--- | :--- |
| *Official URL*:http://example.org/fhir/education/kursig/StructureDefinition/EducationEncounter | *Version*:0.1.0 |
| Draft as of 2026-10-13 | *Computable Name*:EducationEncounter |

 
Profil för en vårdkontakt i FHIR-utbildningen. 

**Användningar:**

* Exempel för denna Profil: [Encounter/encounter-tolvan-1](Encounter-encounter-tolvan-1.md)
* CapabilityStatements som använder denna Profil: [Krav på FHIR-server för Kurs-IG](CapabilityStatement-EducationServerCapabilities.md)

Du kan också kontrollera [användningar i FHIR IG-statistiken](https://packages2.fhir.org/xig/fhir.education.kursig|current/StructureDefinition/EducationEncounter)

### Formal Views of Profile Content

 [Description of Profiles, Differentials, Snapshots and how the different presentations work](http://build.fhir.org/ig/FHIR/ig-guidance/readingIgs.html#structure-definitions). 

 

Other representations of profile: [CSV](StructureDefinition-EducationEncounter.csv), [Excel](StructureDefinition-EducationEncounter.xlsx), [Schematron](StructureDefinition-EducationEncounter.sch) 



## Resource Content

```json
{
  "resourceType" : "StructureDefinition",
  "id" : "EducationEncounter",
  "url" : "http://example.org/fhir/education/kursig/StructureDefinition/EducationEncounter",
  "version" : "0.1.0",
  "name" : "EducationEncounter",
  "title" : "Education Encounter",
  "status" : "draft",
  "date" : "2026-10-13T17:29:30+00:00",
  "publisher" : "FHIR-utbildning",
  "description" : "Profil för en vårdkontakt i FHIR-utbildningen.",
  "jurisdiction" : [{
    "coding" : [{
      "system" : "urn:iso:std:iso:3166",
      "code" : "SE",
      "display" : "Sweden"
    }]
  }],
  "fhirVersion" : "4.0.1",
  "mapping" : [{
    "identity" : "workflow",
    "uri" : "http://hl7.org/fhir/workflow",
    "name" : "Workflow Pattern"
  },
  {
    "identity" : "rim",
    "uri" : "http://hl7.org/v3",
    "name" : "RIM Mapping"
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
  }],
  "kind" : "resource",
  "abstract" : false,
  "type" : "Encounter",
  "baseDefinition" : "http://hl7.org/fhir/StructureDefinition/Encounter",
  "derivation" : "constraint",
  "differential" : {
    "element" : [{
      "id" : "Encounter",
      "path" : "Encounter",
      "constraint" : [{
        "key" : "edu-enc-1",
        "severity" : "error",
        "human" : "En avslutad vårdkontakt (status = finished) ska ha en sluttid (period.end).",
        "expression" : "status = 'finished' implies period.end.exists()",
        "source" : "http://example.org/fhir/education/kursig/StructureDefinition/EducationEncounter"
      },
      {
        "key" : "edu-enc-2",
        "severity" : "warning",
        "human" : "Sluttiden bör inte ligga före starttiden.",
        "expression" : "period.end.empty() or period.start <= period.end",
        "source" : "http://example.org/fhir/education/kursig/StructureDefinition/EducationEncounter"
      }]
    },
    {
      "id" : "Encounter.status",
      "path" : "Encounter.status",
      "mustSupport" : true
    },
    {
      "id" : "Encounter.class",
      "path" : "Encounter.class",
      "mustSupport" : true,
      "binding" : {
        "strength" : "required",
        "valueSet" : "http://example.org/fhir/education/kursig/ValueSet/education-encounter-class"
      }
    },
    {
      "id" : "Encounter.type",
      "path" : "Encounter.type",
      "min" : 1,
      "max" : "1",
      "mustSupport" : true,
      "binding" : {
        "strength" : "extensible",
        "valueSet" : "http://example.org/fhir/education/kursig/ValueSet/kontakttyp-vs"
      }
    },
    {
      "id" : "Encounter.subject",
      "path" : "Encounter.subject",
      "min" : 1,
      "type" : [{
        "code" : "Reference",
        "targetProfile" : ["http://example.org/fhir/education/kursig/StructureDefinition/EducationPatient"]
      }],
      "mustSupport" : true
    },
    {
      "id" : "Encounter.period",
      "path" : "Encounter.period",
      "min" : 1,
      "mustSupport" : true
    },
    {
      "id" : "Encounter.period.start",
      "path" : "Encounter.period.start",
      "min" : 1,
      "mustSupport" : true
    },
    {
      "id" : "Encounter.period.end",
      "path" : "Encounter.period.end",
      "mustSupport" : true
    },
    {
      "id" : "Encounter.reasonCode",
      "path" : "Encounter.reasonCode",
      "mustSupport" : true
    },
    {
      "id" : "Encounter.serviceProvider",
      "path" : "Encounter.serviceProvider",
      "min" : 1,
      "mustSupport" : true
    },
    {
      "id" : "Encounter.serviceProvider.identifier",
      "path" : "Encounter.serviceProvider.identifier",
      "min" : 1,
      "mustSupport" : true
    },
    {
      "id" : "Encounter.serviceProvider.identifier.system",
      "path" : "Encounter.serviceProvider.identifier.system",
      "patternUri" : "urn:oid:1.2.752.29.4.19"
    }]
  }
}

```
