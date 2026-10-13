// Övning 6.2: Ett CapabilityStatement av typen "requirements".
// Det beskriver vad en server SKA kunna för att följa kursens IG – inte vad en viss server faktiskt kan.
Alias: $expectation = http://hl7.org/fhir/StructureDefinition/capabilitystatement-expectation

Instance: EducationServerCapabilities
InstanceOf: CapabilityStatement
Title: "Krav på FHIR-server för Kurs-IG"
Description: "Krav på en FHIR-server som tillhandahåller patienter och vårdkontakter enligt kursens profiler."
Usage: #definition

* name = "EducationServerCapabilities"
* status = #draft
* experimental = true
* date = "2026-10-13"
* kind = #requirements
* fhirVersion = #4.0.1
* format[0] = #json
* implementationGuide = "http://example.org/fhir/education/kursig/ImplementationGuide/fhir.education.kursig"

* rest[0].mode = #server
* rest[0].documentation = "Servern ska stödja läsning och sökning av patienter och vårdkontakter."

// Patient
* rest[0].resource[0].type = #Patient
* rest[0].resource[0].supportedProfile = Canonical(EducationPatient)
* rest[0].resource[0].interaction[0].code = #read
* rest[0].resource[0].interaction[0].extension[$expectation].valueCode = #SHALL
* rest[0].resource[0].interaction[1].code = #search-type
* rest[0].resource[0].interaction[1].extension[$expectation].valueCode = #SHALL
* rest[0].resource[0].searchParam[0].name = "identifier"
* rest[0].resource[0].searchParam[0].definition = "http://hl7.org/fhir/SearchParameter/Patient-identifier"
* rest[0].resource[0].searchParam[0].type = #token
* rest[0].resource[0].searchParam[0].extension[$expectation].valueCode = #SHALL

// Encounter
* rest[0].resource[1].type = #Encounter
* rest[0].resource[1].supportedProfile = Canonical(EducationEncounter)
* rest[0].resource[1].interaction[0].code = #read
* rest[0].resource[1].interaction[0].extension[$expectation].valueCode = #SHALL
* rest[0].resource[1].interaction[1].code = #search-type
* rest[0].resource[1].interaction[1].extension[$expectation].valueCode = #SHALL
* rest[0].resource[1].searchParam[0].name = "patient"
* rest[0].resource[1].searchParam[0].definition = "http://hl7.org/fhir/SearchParameter/clinical-patient"
* rest[0].resource[1].searchParam[0].type = #reference
* rest[0].resource[1].searchParam[0].extension[$expectation].valueCode = #SHALL
* rest[0].resource[1].searchParam[1].name = "date"
* rest[0].resource[1].searchParam[1].definition = "http://hl7.org/fhir/SearchParameter/clinical-date"
* rest[0].resource[1].searchParam[1].type = #date
* rest[0].resource[1].searchParam[1].extension[$expectation].valueCode = #SHOULD
