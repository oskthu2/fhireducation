// Lösning efter modul 6 (följsamhet).
Profile: EducationEncounter
Parent: Encounter
Id: EducationEncounter
Title: "Education Encounter"
Description: "Profil för en vårdkontakt i FHIR-utbildningen."

* ^status = #draft

* status MS

// --- Övning 3.3a: Bindning till ett eget ValueSet (som räknar upp koder med include) ---
* class MS
* class from EducationEncounterClassVS (required)

// Typ av kontakt: ValueSet som inkluderar ett helt (eget) kodsystem.
// extensible = använd en kod härifrån om det finns en som passar.
* type 1..1 MS
* type from KontakttypVS (extensible)

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

// --- Övning 4: Invarianter (se invariants.fsh) ---
* obeys edu-enc-1 and edu-enc-2
