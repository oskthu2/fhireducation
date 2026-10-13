// Övning 3.3a: Ett eget kodsystem och ett ValueSet som inkluderar hela kodsystemet.
// OBS! Fiktivt kodsystem för utbildningen. I verkligheten används ett nationellt kodverk.
CodeSystem: KontakttypCS
Id: kontakttyp
Title: "Kontakttyp"
Description: "Typ av vårdkontakt (fiktivt kodsystem för utbildningen)."
* ^caseSensitive = true
* ^experimental = true
* #besok "Besök" "Fysiskt besök på en vårdenhet."
* #hembesok "Hembesök" "Besök i patientens hem."
* #video "Videokontakt" "Distanskontakt via video."
* #telefon "Telefonkontakt" "Distanskontakt via telefon."

ValueSet: KontakttypVS
Id: kontakttyp-vs
Title: "Kontakttyp – ValueSet"
Description: "Alla koder i kodsystemet Kontakttyp."
* ^experimental = true
* include codes from system KontakttypCS
