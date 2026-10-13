// Lösning efter modul 6 (följsamhet), med extraövning 3.6.
Profile: EducationPatient
Parent: Patient
Id: EducationPatient
Title: "Education Patient"
Description: "Patientprofil för FHIR-utbildningen. Profilen byggs ut steg för steg under kursen."

* ^status = #draft

// --- Startprofilen ---
* identifier 1..* MS
* identifier.system 1..1
* identifier.value 1..1
* name 1..* MS
* name.family 1..1 MS
* name.given MS
* gender MS
* birthDate 1..1 MS

// --- Övning 3.3b: Bindning genom referens till ett befintligt ValueSet ---
// Basresursen binder maritalStatus med styrkan extensible. Vi skärper till required.
* maritalStatus from http://hl7.org/fhir/ValueSet/marital-status (required)

// --- Övning 3.4: Extensions ---
// En befintlig extension från FHIR-standarden och en egen extension (se extensions/SkyddadIdentitet.fsh).
* extension contains
    $patient-interpreterRequired named tolkbehov 0..1 MS and
    SkyddadIdentitet named skyddadIdentitet 0..1 MS

// --- Övning 3.5: Slicing av identifier ---
// Diskriminatorn talar om HUR en validator avgör vilken slice ett element hör till.
// Här: värdet i identifier.system. Öppen slicing tillåter även andra identifierare.
* identifier ^slicing.discriminator.type = #value
* identifier ^slicing.discriminator.path = "system"
* identifier ^slicing.rules = #open
* identifier ^slicing.description = "Identifierare skiljs åt med hjälp av system."
* identifier contains
    personnummer 0..1 MS and
    samordningsnummer 0..1 MS
* identifier[personnummer] ^short = "Personnummer (12 siffror)"
* identifier[personnummer].system = $personnummer
* identifier[samordningsnummer] ^short = "Samordningsnummer (12 siffror)"
* identifier[samordningsnummer].system = $samordningsnummer

// --- Övning 4: Invarianter (se invariants.fsh) ---
* obeys edu-pat-1 and edu-pat-2
