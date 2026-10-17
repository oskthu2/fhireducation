// Logiska modeller som beskriver journalsystemets proprietära REST-API.
// FML-motorn behöver veta hur källdatan ser ut, och det beskrivs med logiska modeller (StructureDefinition, kind = logical).
// JSON-filerna bredvid genereras från den här filen med SUSHI (se README i mappen fml/).

Logical: JournalPatient
Id: JournalPatient
Title: "Journalsystemets patient"
Description: "En patient så som journalsystemets REST-API returnerar den: GET /journalsystem-api/patienter/{personnummer}"
* personnummer 1..1 string "Personnummer, 12 siffror"
* fornamn 0..1 string "Förnamn"
* efternamn 0..1 string "Efternamn"
* kon 0..1 string "Kön: M (man) eller K (kvinna)"
* fodelsedatum 0..1 date "Födelsedatum (ÅÅÅÅ-MM-DD)"
* telefon 0..1 string "Telefonnummer i fritext"

Logical: JournalBesok
Id: JournalBesok
Title: "Journalsystemets besök"
Description: "Ett besök så som journalsystemets REST-API returnerar det: GET /journalsystem-api/patienter/{personnummer}/besok"
* besoksId 1..1 string "Besökets id i journalsystemet"
* personnummer 1..1 string "Patientens personnummer"
* kontakttyp 1..1 string "BES = besök, HEM = hembesök, VID = video, TEL = telefon, DIG = digital kontakt"
* status 1..1 string "PLAN = planerad, PAGAR = pågår, AVSL = avslutad"
* start 1..1 dateTime "Starttid (ISO 8601 med tidszon)"
* slut 0..1 dateTime "Sluttid (ISO 8601 med tidszon)"
* diagnoskod 0..1 string "Diagnoskod enligt ICD-10"
* enhetHsaId 1..1 string "Vårdenhetens HSA-id"
