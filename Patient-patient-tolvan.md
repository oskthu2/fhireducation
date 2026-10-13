# Tolvan Tolvansson - FHIR-utbildning – Kurs-IG v0.1.0

* [**Table of Contents**](toc.md)
* [**Artifacts Summary**](artifacts.md)
* **Tolvan Tolvansson**

## Example Patient: Tolvan Tolvansson

Profil: [Education Patient](StructureDefinition-EducationPatient.md)

Tolvan Tolvansson (official) Male, Födelsedatum: 1912-12-12 ( http://electronichealth.se/identifier/personnummer#191212121212)

-------



## Resource Content

```json
{
  "resourceType" : "Patient",
  "id" : "patient-tolvan",
  "meta" : {
    "profile" : ["http://example.org/fhir/education/kursig/StructureDefinition/EducationPatient"]
  },
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
  "birthDate" : "1912-12-12"
}

```
