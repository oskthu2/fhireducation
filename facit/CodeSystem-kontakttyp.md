# Kontakttyp - FHIR-utbildning – Kurs-IG (facit) v0.1.0

* [**Table of Contents**](toc.md)
* [**Artifacts Summary**](artifacts.md)
* **Kontakttyp**

## CodeSystem: Kontakttyp (Experimental) 

| | |
| :--- | :--- |
| *Official URL*:http://example.org/fhir/education/kursig/CodeSystem/kontakttyp | *Version*:0.1.0 |
| Draft as of 2026-10-13 | *Computable Name*:KontakttypCS |

 
Typ av vårdkontakt (fiktivt kodsystem för utbildningen). 

 This Code system is referenced in the content logical definition of the following value sets: 

* [Kontakttyp – ValueSet](ValueSet-kontakttyp-vs.md)



## Resource Content

```json
{
  "resourceType" : "CodeSystem",
  "id" : "kontakttyp",
  "url" : "http://example.org/fhir/education/kursig/CodeSystem/kontakttyp",
  "version" : "0.1.0",
  "name" : "KontakttypCS",
  "title" : "Kontakttyp",
  "status" : "draft",
  "experimental" : true,
  "date" : "2026-10-13T17:29:30+00:00",
  "publisher" : "FHIR-utbildning",
  "description" : "Typ av vårdkontakt (fiktivt kodsystem för utbildningen).",
  "jurisdiction" : [{
    "coding" : [{
      "system" : "urn:iso:std:iso:3166",
      "code" : "SE",
      "display" : "Sweden"
    }]
  }],
  "caseSensitive" : true,
  "content" : "complete",
  "count" : 4,
  "concept" : [{
    "code" : "besok",
    "display" : "Besök",
    "definition" : "Fysiskt besök på en vårdenhet."
  },
  {
    "code" : "hembesok",
    "display" : "Hembesök",
    "definition" : "Besök i patientens hem."
  },
  {
    "code" : "video",
    "display" : "Videokontakt",
    "definition" : "Distanskontakt via video."
  },
  {
    "code" : "telefon",
    "display" : "Telefonkontakt",
    "definition" : "Distanskontakt via telefon."
  }]
}

```
