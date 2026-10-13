# Skyddad identitet - FHIR-utbildning – Kurs-IG (facit) v0.1.0

* [**Table of Contents**](toc.md)
* [**Artifacts Summary**](artifacts.md)
* **Skyddad identitet**

## Extension: Skyddad identitet 

| | |
| :--- | :--- |
| *Official URL*:http://example.org/fhir/education/kursig/StructureDefinition/SkyddadIdentitet | *Version*:0.1.0 |
| Draft as of 2026-10-13 | *Computable Name*:SkyddadIdentitet |

Anger om patienten har skyddade personuppgifter (t.ex. sekretessmarkering eller skyddad folkbokföring).

**Context of Use**

**Usage info**

**Användningar:**

* Använd denna Extension: [Education Patient](StructureDefinition-EducationPatient.md)
* Exempel för denna Extension: [Patient/patient-tolvan](Patient-patient-tolvan.md)

Du kan också kontrollera [användningar i FHIR IG-statistiken](https://packages2.fhir.org/xig/fhir.education.kursig|current/StructureDefinition/SkyddadIdentitet)

### Formal Views of Extension Content

 [Description of Profiles, Differentials, Snapshots, and how the XML and JSON presentations work](http://build.fhir.org/ig/FHIR/ig-guidance/readingIgs.html#structure-definitions). 

 

Other representations of profile: [CSV](StructureDefinition-SkyddadIdentitet.csv), [Excel](StructureDefinition-SkyddadIdentitet.xlsx), [Schematron](StructureDefinition-SkyddadIdentitet.sch) 

#### Begränsningar



## Resource Content

```json
{
  "resourceType" : "StructureDefinition",
  "id" : "SkyddadIdentitet",
  "url" : "http://example.org/fhir/education/kursig/StructureDefinition/SkyddadIdentitet",
  "version" : "0.1.0",
  "name" : "SkyddadIdentitet",
  "title" : "Skyddad identitet",
  "status" : "draft",
  "date" : "2026-10-13T17:29:30+00:00",
  "publisher" : "FHIR-utbildning",
  "description" : "Anger om patienten har skyddade personuppgifter (t.ex. sekretessmarkering eller skyddad folkbokföring).",
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
  }],
  "kind" : "complex-type",
  "abstract" : false,
  "context" : [{
    "type" : "element",
    "expression" : "Patient"
  }],
  "type" : "Extension",
  "baseDefinition" : "http://hl7.org/fhir/StructureDefinition/Extension",
  "derivation" : "constraint",
  "differential" : {
    "element" : [{
      "id" : "Extension",
      "path" : "Extension",
      "short" : "Skyddad identitet",
      "definition" : "Anger om patienten har skyddade personuppgifter (t.ex. sekretessmarkering eller skyddad folkbokföring)."
    },
    {
      "id" : "Extension.extension",
      "path" : "Extension.extension",
      "max" : "0"
    },
    {
      "id" : "Extension.url",
      "path" : "Extension.url",
      "fixedUri" : "http://example.org/fhir/education/kursig/StructureDefinition/SkyddadIdentitet"
    },
    {
      "id" : "Extension.value[x]",
      "path" : "Extension.value[x]",
      "min" : 1,
      "type" : [{
        "code" : "boolean"
      }]
    }]
  }
}

```
