Instance: encounter-tolvan-1
InstanceOf: EducationEncounter
Title: "Besök på vårdcentral"
Description: "Tolvan besöker vårdcentralen."
Usage: #example

* status = #finished
* class = $v3-ActCode#AMB "ambulatory"
* type = KontakttypCS#besok "Besök"
* subject = Reference(patient-tolvan)
* period.start = "2026-10-01T09:00:00+02:00"
* period.end = "2026-10-01T09:30:00+02:00"
* reasonCode = $ICD10#J45.9 "Asthma, unspecified"
* serviceProvider.identifier.system = $hsaid
* serviceProvider.identifier.value = "SE2321000016-KURS"
* serviceProvider.display = "Vårdcentralen Kursköping"
