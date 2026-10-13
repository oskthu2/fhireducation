// Övning 3.6 (extra): exempel enligt EducationSEPatient.
// Skyddad identitet uttrycks med säkerhetsmärkning (meta.security), så som HL7 Sverige gör.
Instance: patient-tolvan-se
InstanceOf: EducationSEPatient
Title: "Tolvan Tolvansson (SE-bas)"
Description: "Exempelpatient enligt profilen som bygger på HL7 Sveriges basprofil."
Usage: #example

* meta.security = http://hl7.se/fhir/ig/base/CodeSystem/SecurityLabel#sekretessmarkering "Sekretessmarkering"
* identifier[personnummer].value = "191212121212"
* name.use = #official
* name.family = "Tolvansson"
* name.given = "Tolvan"
* gender = #male
* birthDate = "1912-12-12"
