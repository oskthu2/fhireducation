Instance: patient-tolvan
InstanceOf: EducationPatient
Title: "Tolvan Tolvansson"
Description: "Exempelpatient (Skatteverkets klassiska testperson)."
Usage: #example

// Med slicing kan vi peka ut en slice med namn. I den färdiga instansen syns inte slice-namnet!
* identifier[personnummer].value = "191212121212"
* name[0].use = #official
* name[0].family = "Tolvansson"
* name[0].given[0] = "Tolvan"
* gender = #male
* birthDate = "1912-12-12"
* maritalStatus = $v3-MaritalStatus#M "Married"
* extension[tolkbehov].valueBoolean = false
* extension[skyddadIdentitet].valueBoolean = false
