// Startprofilen för kursen. Den här profilen bygger vi vidare på i modul 3 och 4.
// Namnkonvention: [prefix][Resurstyp] i PascalCase, och samma värde för Id.
Profile: EducationPatient
Parent: Patient
Id: EducationPatient
Title: "Education Patient"
Description: "Patientprofil för FHIR-utbildningen. Profilen byggs ut steg för steg under kursen."

* ^status = #draft

// Kardinalitet: minst en identifierare, ett namn och ett födelsedatum krävs.
// MS (Must Support) betyder att avsändare ska kunna skicka och mottagare kunna hantera elementet.
* identifier 1..* MS
* identifier.system 1..1
* identifier.value 1..1
* name 1..* MS
* name.family 1..1 MS
* name.given MS
* gender MS
* birthDate 1..1 MS
