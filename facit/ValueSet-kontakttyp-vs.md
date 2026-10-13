# Kontakttyp – ValueSet - FHIR-utbildning – Kurs-IG (facit) v0.1.0

* [**Table of Contents**](toc.md)
* [**Artifacts Summary**](artifacts.md)
* **Kontakttyp – ValueSet**

## ValueSet: Kontakttyp – ValueSet (Experimental) 

| | |
| :--- | :--- |
| *Official URL*:http://example.org/fhir/education/kursig/ValueSet/kontakttyp-vs | *Version*:0.1.0 |
| Draft as of 2026-10-13 | *Computable Name*:KontakttypVS |

 
Alla koder i kodsystemet Kontakttyp. 

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
  "id" : "kontakttyp-vs",
  "url" : "http://example.org/fhir/education/kursig/ValueSet/kontakttyp-vs",
  "version" : "0.1.0",
  "name" : "KontakttypVS",
  "title" : "Kontakttyp – ValueSet",
  "status" : "draft",
  "experimental" : true,
  "date" : "2026-10-13T17:29:30+00:00",
  "publisher" : "FHIR-utbildning",
  "description" : "Alla koder i kodsystemet Kontakttyp.",
  "jurisdiction" : [{
    "coding" : [{
      "system" : "urn:iso:std:iso:3166",
      "code" : "SE",
      "display" : "Sweden"
    }]
  }],
  "compose" : {
    "include" : [{
      "system" : "http://example.org/fhir/education/kursig/CodeSystem/kontakttyp"
    }]
  }
}

```
