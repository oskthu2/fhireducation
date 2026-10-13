// Övning 3.6 (extra): en profil som bygger på HL7 Sveriges basprofil i stället för på basresursen.
// Kräver beroendet hl7se.fhir.base i sushi-config.yaml (se ../dependencies.yaml).
Profile: EducationSEPatient
Parent: http://hl7.se/fhir/ig/base/StructureDefinition/SEBasePatient
Id: EducationSEPatient
Title: "Education SE Patient"
Description: "Patientprofil som bygger på HL7 Sveriges basprofil SEBasePatient."

* ^status = #draft

// Slicen personnummer (och samordningsnummer, nationelltReservnummer) ärvs från SEBasePatient.
* identifier 1..* MS
* identifier[personnummer] MS
// SEBasePatient tillåter högst ett namn (0..1). Vi kan skärpa till 1..1, men inte tillåta fler.
* name 1..1 MS
* name.family 1..1 MS
* gender MS
* birthDate 1..1 MS
