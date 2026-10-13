# Tolvan Tolvansson - FHIR-utbildning – Kurs-IG (facit) v0.1.0

* [**Table of Contents**](toc.md)
* [**Artifacts Summary**](artifacts.md)
* **Tolvan Tolvansson**

## Example Patient: Tolvan Tolvansson

Profil: [Education Patient](StructureDefinition-EducationPatient.md)

Tolvan Tolvansson (official) Male, Födelsedatum: 1912-12-12 ( http://electronichealth.se/identifier/personnummer#191212121212)

-------

| | |
| :--- | :--- |
| Civilstånd: | Married |
| [Interpreter Required](http://hl7.org/fhir/extensions/5.3.0/StructureDefinition-patient-interpreterRequired.html) | false |
| [Skyddad identitet](StructureDefinition-SkyddadIdentitet.md) | false |



## Resource Content

```json
{
  "resourceType" : "Patient",
  "id" : "patient-tolvan",
  "meta" : {
    "profile" : ["http://example.org/fhir/education/kursig/StructureDefinition/EducationPatient"]
  },
  "extension" : [{
    "url" : "http://hl7.org/fhir/StructureDefinition/patient-interpreterRequired",
    "valueBoolean" : false
  },
  {
    "url" : "http://example.org/fhir/education/kursig/StructureDefinition/SkyddadIdentitet",
    "valueBoolean" : false
  }],
  "identifier" : [{
    "system" : "http://electronichealth.se/identifier/personnummer",
    "value" : "191212121212"
  }],
  "name" : [{
    "use" : "official",
    "family" : "Tolvansson",
    "given" : ["Tolvan"]
  }],
  "gender" : "male",
  "birthDate" : "1912-12-12",
  "maritalStatus" : {
    "coding" : [{
      "system" : "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus",
      "code" : "M",
      "display" : "Married"
    }]
  }
}

```
