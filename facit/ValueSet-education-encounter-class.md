# Klass av vårdkontakt - FHIR-utbildning – Kurs-IG (facit) v0.1.0

* [**Table of Contents**](toc.md)
* [**Artifacts Summary**](artifacts.md)
* **Klass av vårdkontakt**

## ValueSet: Klass av vårdkontakt (Experimental) 

| | |
| :--- | :--- |
| *Official URL*:http://example.org/fhir/education/kursig/ValueSet/education-encounter-class | *Version*:0.1.0 |
| Draft as of 2026-10-13 | *Computable Name*:EducationEncounterClassVS |

 
Ett urval av koder ur HL7 v3 ActCode som får användas i Encounter.class. 

 **References** 

* [Education Encounter](StructureDefinition-EducationEncounter.md)

### Logisk definition (CLD)

 

### Expansion

-------

 Explanation of the columns that may appear on this page: 

| | |
| :--- | :--- |
| Level | A few code lists that FHIR defines are hierarchical - each code is assigned a level. In this scheme, some codes are under other codes, and imply that the code they are under also applies |
| System | The source of the definition of the code (when the value set draws in codes defined elsewhere) |
| Code | The code (used as the code in the resource instance) |
| Display | The display (used in the*display*element of a[Coding](http://hl7.org/fhir/R4/datatypes.html#Coding)). If there is no display, implementers should not simply display the code, but map the concept into their application |
| Definition | An explanation of the meaning of the concept |
| Comments | Additional notes about how to use the code |



## Resource Content

```json
{
  "resourceType" : "ValueSet",
  "id" : "education-encounter-class",
  "url" : "http://example.org/fhir/education/kursig/ValueSet/education-encounter-class",
  "version" : "0.1.0",
  "name" : "EducationEncounterClassVS",
  "title" : "Klass av vårdkontakt",
  "status" : "draft",
  "experimental" : true,
  "date" : "2026-10-13T17:29:30+00:00",
  "publisher" : "FHIR-utbildning",
  "description" : "Ett urval av koder ur HL7 v3 ActCode som får användas i Encounter.class.",
  "jurisdiction" : [{
    "coding" : [{
      "system" : "urn:iso:std:iso:3166",
      "code" : "SE",
      "display" : "Sweden"
    }]
  }],
  "compose" : {
    "include" : [{
      "system" : "http://terminology.hl7.org/CodeSystem/v3-ActCode",
      "concept" : [{
        "code" : "AMB",
        "display" : "ambulatory"
      },
      {
        "code" : "IMP",
        "display" : "inpatient encounter"
      },
      {
        "code" : "EMER",
        "display" : "emergency"
      },
      {
        "code" : "HH",
        "display" : "home health"
      },
      {
        "code" : "VR",
        "display" : "virtual"
      }]
    }]
  }
}

```
