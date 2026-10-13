// Ett exempel som visar hur en patient enligt profilen ser ut.
// meta.profile sätts automatiskt av SUSHI utifrån InstanceOf.
Instance: patient-tolvan
InstanceOf: EducationPatient
Title: "Tolvan Tolvansson"
Description: "Exempelpatient (Skatteverkets klassiska testperson)."
Usage: #example

* identifier[0].system = $personnummer
* identifier[0].value = "191212121212"
* name[0].use = #official
* name[0].family = "Tolvansson"
* name[0].given[0] = "Tolvan"
* gender = #male
* birthDate = "1912-12-12"
