// Övning 3.3a: Ett ValueSet som räknar upp (include) enskilda koder från ett befintligt kodsystem.
ValueSet: EducationEncounterClassVS
Id: education-encounter-class
Title: "Klass av vårdkontakt"
Description: "Ett urval av koder ur HL7 v3 ActCode som får användas i Encounter.class."
* ^experimental = true
* include $v3-ActCode#AMB "ambulatory"
* include $v3-ActCode#IMP "inpatient encounter"
* include $v3-ActCode#EMER "emergency"
* include $v3-ActCode#HH "home health"
* include $v3-ActCode#VR "virtual"
