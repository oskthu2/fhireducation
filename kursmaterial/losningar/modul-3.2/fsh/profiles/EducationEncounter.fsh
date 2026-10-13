// Lösning efter övning 3.2: profilen utan terminologibindningar (de läggs till i övning 3.3).
Profile: EducationEncounter
Parent: Encounter
Id: EducationEncounter
Title: "Education Encounter"
Description: "Profil för en vårdkontakt i FHIR-utbildningen."

* ^status = #draft

* status MS
* class MS
* type 1..1 MS

// Vårdkontakten måste gälla en patient som följer vår patientprofil.
* subject 1..1 MS
* subject only Reference(EducationPatient)

* period 1..1 MS
* period.start 1..1 MS
* period.end MS

* reasonCode MS

// Vårdgivaren anges som en logisk referens med HSA-id.
* serviceProvider 1..1 MS
* serviceProvider.identifier 1..1 MS
* serviceProvider.identifier.system = $hsaid
