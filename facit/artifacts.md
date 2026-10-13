# Artifacts Summary - FHIR-utbildning – Kurs-IG (facit) v0.1.0

* [**Table of Contents**](toc.md)
* **Artifacts Summary**

## Artifacts Summary

This page provides a list of the FHIR artifacts defined as part of this implementation guide.

### Behavior: Capability Statements 

The following artifacts define the specific capabilities that different types of systems are expected to have in order to comply with this implementation guide. Systems conforming to this implementation guide are expected to declare conformance to one or more of the following capability statements.

| | |
| :--- | :--- |
| [Krav på FHIR-server för Kurs-IG](CapabilityStatement-EducationServerCapabilities.md) | Krav på en FHIR-server som tillhandahåller patienter och vårdkontakter enligt kursens profiler. |

### Structures: Resource Profiles 

These define constraints on FHIR resources for systems conforming to this implementation guide.

| | |
| :--- | :--- |
| [Education Encounter](StructureDefinition-EducationEncounter.md) | Profil för en vårdkontakt i FHIR-utbildningen. |
| [Education Patient](StructureDefinition-EducationPatient.md) | Patientprofil för FHIR-utbildningen. Profilen byggs ut steg för steg under kursen. |

### Structures: Extension Definitions 

These define constraints on FHIR data types for systems conforming to this implementation guide.

| | |
| :--- | :--- |
| [Skyddad identitet](StructureDefinition-SkyddadIdentitet.md) | Anger om patienten har skyddade personuppgifter (t.ex. sekretessmarkering eller skyddad folkbokföring). |

### Terminology: Value Sets 

These define sets of codes used by systems conforming to this implementation guide.

| | |
| :--- | :--- |
| [Klass av vårdkontakt](ValueSet-education-encounter-class.md) | Ett urval av koder ur HL7 v3 ActCode som får användas i Encounter.class. |
| [Kontakttyp – ValueSet](ValueSet-kontakttyp-vs.md) | Alla koder i kodsystemet Kontakttyp. |

### Terminology: Code Systems 

These define new code systems used by systems conforming to this implementation guide.

| | |
| :--- | :--- |
| [Kontakttyp](CodeSystem-kontakttyp.md) | Typ av vårdkontakt (fiktivt kodsystem för utbildningen). |

### Example: Example Instances 

These are example instances that show what data produced and consumed by systems conforming with this implementation guide might look like.

| | |
| :--- | :--- |
| [Besök på vårdcentral](Encounter-encounter-tolvan-1.md) | Tolvan besöker vårdcentralen. |
| [Tolvan Tolvansson](Patient-patient-tolvan.md) | Exempelpatient (Skatteverkets klassiska testperson). |

