# Krav på FHIR-server för Kurs-IG - FHIR-utbildning – Kurs-IG (facit) v0.1.0

* [**Table of Contents**](toc.md)
* [**Artifacts Summary**](artifacts.md)
* **Krav på FHIR-server för Kurs-IG**

## CapabilityStatement: Krav på FHIR-server för Kurs-IG (Experimental) 

| | |
| :--- | :--- |
| *Official URL*:http://example.org/fhir/education/kursig/CapabilityStatement/EducationServerCapabilities | *Version*:0.1.0 |
| Draft as of 2026-10-13 | *Computable Name*:EducationServerCapabilities |

 
Krav på en FHIR-server som tillhandahåller patienter och vårdkontakter enligt kursens profiler. 

 [Raw OpenAPI-Swagger Definition file](EducationServerCapabilities.openapi.json) | [Download](EducationServerCapabilities.openapi.json) 



## Resource Content

```json
{
  "resourceType" : "CapabilityStatement",
  "id" : "EducationServerCapabilities",
  "url" : "http://example.org/fhir/education/kursig/CapabilityStatement/EducationServerCapabilities",
  "version" : "0.1.0",
  "name" : "EducationServerCapabilities",
  "title" : "Krav på FHIR-server för Kurs-IG",
  "status" : "draft",
  "experimental" : true,
  "date" : "2026-10-13",
  "publisher" : "FHIR-utbildning",
  "description" : "Krav på en FHIR-server som tillhandahåller patienter och vårdkontakter enligt kursens profiler.",
  "jurisdiction" : [{
    "coding" : [{
      "system" : "urn:iso:std:iso:3166",
      "code" : "SE",
      "display" : "Sweden"
    }]
  }],
  "kind" : "requirements",
  "fhirVersion" : "4.0.1",
  "format" : ["json"],
  "implementationGuide" : ["http://example.org/fhir/education/kursig/ImplementationGuide/fhir.education.kursig"],
  "rest" : [{
    "mode" : "server",
    "documentation" : "Servern ska stödja läsning och sökning av patienter och vårdkontakter.",
    "resource" : [{
      "type" : "Patient",
      "supportedProfile" : ["http://example.org/fhir/education/kursig/StructureDefinition/EducationPatient"],
      "interaction" : [{
        "extension" : [{
          "url" : "http://hl7.org/fhir/StructureDefinition/capabilitystatement-expectation",
          "valueCode" : "SHALL"
        }],
        "code" : "read"
      },
      {
        "extension" : [{
          "url" : "http://hl7.org/fhir/StructureDefinition/capabilitystatement-expectation",
          "valueCode" : "SHALL"
        }],
        "code" : "search-type"
      }],
      "searchParam" : [{
        "extension" : [{
          "url" : "http://hl7.org/fhir/StructureDefinition/capabilitystatement-expectation",
          "valueCode" : "SHALL"
        }],
        "name" : "identifier",
        "definition" : "http://hl7.org/fhir/SearchParameter/Patient-identifier",
        "type" : "token"
      }]
    },
    {
      "type" : "Encounter",
      "supportedProfile" : ["http://example.org/fhir/education/kursig/StructureDefinition/EducationEncounter"],
      "interaction" : [{
        "extension" : [{
          "url" : "http://hl7.org/fhir/StructureDefinition/capabilitystatement-expectation",
          "valueCode" : "SHALL"
        }],
        "code" : "read"
      },
      {
        "extension" : [{
          "url" : "http://hl7.org/fhir/StructureDefinition/capabilitystatement-expectation",
          "valueCode" : "SHALL"
        }],
        "code" : "search-type"
      }],
      "searchParam" : [{
        "extension" : [{
          "url" : "http://hl7.org/fhir/StructureDefinition/capabilitystatement-expectation",
          "valueCode" : "SHALL"
        }],
        "name" : "patient",
        "definition" : "http://hl7.org/fhir/SearchParameter/clinical-patient",
        "type" : "reference"
      },
      {
        "extension" : [{
          "url" : "http://hl7.org/fhir/StructureDefinition/capabilitystatement-expectation",
          "valueCode" : "SHOULD"
        }],
        "name" : "date",
        "definition" : "http://hl7.org/fhir/SearchParameter/clinical-date",
        "type" : "date"
      }]
    }]
  }]
}

```
