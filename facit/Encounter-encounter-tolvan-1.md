# Besök på vårdcentral - FHIR-utbildning – Kurs-IG (facit) v0.1.0

* [**Table of Contents**](toc.md)
* [**Artifacts Summary**](artifacts.md)
* **Besök på vårdcentral**

## Example Encounter: Besök på vårdcentral

Profil: [Education Encounter](StructureDefinition-EducationEncounter.md)

**status**: Finished

**class**: [ActCode: AMB](http://terminology.hl7.org/7.4.0/CodeSystem-v3-ActCode.html#v3-ActCode-AMB) (ambulatory)

**type**: Besök

**subject**: [Tolvan Tolvansson (official) Male, Födelsedatum: 1912-12-12 ( http://electronichealth.se/identifier/personnummer#191212121212)](Patient-patient-tolvan.md)

**period**: 2026-10-01 09:00:00+0200 --> 2026-10-01 09:30:00+0200

**reasonCode**: Asthma, unspecified

**serviceProvider**: Vårdcentralen Kursköping (Identifier: `urn:oid:1.2.752.29.4.19`/SE2321000016-KURS)



## Resource Content

```json
{
  "resourceType" : "Encounter",
  "id" : "encounter-tolvan-1",
  "meta" : {
    "profile" : ["http://example.org/fhir/education/kursig/StructureDefinition/EducationEncounter"]
  },
  "status" : "finished",
  "class" : {
    "system" : "http://terminology.hl7.org/CodeSystem/v3-ActCode",
    "code" : "AMB",
    "display" : "ambulatory"
  },
  "type" : [{
    "coding" : [{
      "system" : "http://example.org/fhir/education/kursig/CodeSystem/kontakttyp",
      "code" : "besok",
      "display" : "Besök"
    }]
  }],
  "subject" : {
    "reference" : "Patient/patient-tolvan"
  },
  "period" : {
    "start" : "2026-10-01T09:00:00+02:00",
    "end" : "2026-10-01T09:30:00+02:00"
  },
  "reasonCode" : [{
    "coding" : [{
      "system" : "http://hl7.org/fhir/sid/icd-10",
      "code" : "J45.9",
      "display" : "Asthma, unspecified"
    }]
  }],
  "serviceProvider" : {
    "identifier" : {
      "system" : "urn:oid:1.2.752.29.4.19",
      "value" : "SE2321000016-KURS"
    },
    "display" : "Vårdcentralen Kursköping"
  }
}

```
