package se.fhir.education.fasad.mapping;

import org.hl7.fhir.r4.model.DateType;
import org.hl7.fhir.r4.model.Enumerations.AdministrativeGender;
import org.hl7.fhir.r4.model.HumanName.NameUse;
import org.hl7.fhir.r4.model.Patient;

import se.fhir.education.fasad.legacy.Journalsystem.PatientRad;

/** Mappar en rad i journalsystemets PATIENT-tabell till en FHIR Patient enligt profilen EducationPatient. */
public final class PatientMapper {

  public static final String PROFIL = "http://example.org/fhir/education/kursig/StructureDefinition/EducationPatient";
  public static final String PERSONNUMMER = "http://electronichealth.se/identifier/personnummer";

  private PatientMapper() {
  }

  /** Det logiska id:t i FHIR-API:t. Här används personnumret direkt – diskutera om det är lämpligt! */
  public static String fhirId(PatientRad rad) {
    return rad.personnummer();
  }

  public static Patient toFhir(PatientRad rad) {
    Patient patient = new Patient();
    patient.setId(fhirId(rad));
    patient.getMeta().addProfile(PROFIL);

    patient.addIdentifier()
        .setSystem(PERSONNUMMER)
        .setValue(rad.personnummer());

    patient.addName()
        .setUse(NameUse.OFFICIAL)
        .setFamily(rad.efternamn())
        .addGiven(rad.fornamn());

    // Journalsystemets egna koder ("M"/"K") mappas till FHIR:s required-bundna värdemängd.
    patient.setGender(switch (rad.kon()) {
      case "M" -> AdministrativeGender.MALE;
      case "K" -> AdministrativeGender.FEMALE;
      default -> AdministrativeGender.UNKNOWN;
    });

    // FHIR-datatypen date (ÅÅÅÅ-MM-DD) – utan klockslag och tidszon.
    patient.setBirthDateElement(new DateType(rad.fodelsedatum().toString()));

    // ÖVNING 5.2: Journalsystemet har ett telefonnummer (rad.telefon()) som inte mappas ännu.
    // Lägg till det som Patient.telecom (system = phone). Tänk på att värdet kan saknas!

    return patient;
  }
}
