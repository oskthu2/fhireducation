package se.fhir.education.fasad;

import static org.assertj.core.api.Assertions.assertThat;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

import org.hl7.fhir.r4.model.ContactPoint.ContactPointSystem;
import org.hl7.fhir.r4.model.Encounter;
import org.hl7.fhir.r4.model.Encounter.EncounterStatus;
import org.hl7.fhir.r4.model.Enumerations.AdministrativeGender;
import org.hl7.fhir.r4.model.Patient;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

import se.fhir.education.fasad.mapping.FmlMotor;
import se.fhir.education.fasad.mapping.Kanoniska;

/** Testar FML-mappningarna i src/main/resources/fml utan att starta servern. */
class FmlMotorTest {

  private static FmlMotor motor;

  private static final JsonObject BRITTA = json("""
      { "personnummer": "195503222340", "fornamn": "Britta", "efternamn": "Björk",
        "kon": "K", "fodelsedatum": "1955-03-22", "telefon": "070-111 22 33" }
      """);

  private static final JsonObject BESOK = json("""
      { "besoksId": "B1001", "personnummer": "191212121212", "kontakttyp": "BES", "status": "AVSL",
        "start": "2026-10-01T09:00:00+02:00", "slut": "2026-10-01T09:30:00+02:00",
        "diagnoskod": "J45.9", "enhetHsaId": "SE2321000016-KURS" }
      """);

  private static final JsonObject DIGITALT_BESOK = json("""
      { "besoksId": "B2002", "personnummer": "194208106593", "kontakttyp": "DIG", "status": "PLAN",
        "start": "2026-11-20T08:30:00+01:00", "enhetHsaId": "SE2321000016-KURS" }
      """);

  @BeforeAll
  static void setUp() throws Exception {
    motor = new FmlMotor();
  }

  @Test
  void mapparPatient() {
    Patient patient = motor.transformera(BRITTA, Kanoniska.JOURNAL_PATIENT, new Patient());

    assertThat(patient.getMeta().hasProfile(Kanoniska.EDUCATION_PATIENT)).isTrue();
    assertThat(patient.getIdentifierFirstRep().getSystem()).isEqualTo(Kanoniska.PERSONNUMMER);
    assertThat(patient.getIdentifierFirstRep().getValue()).isEqualTo("195503222340");
    assertThat(patient.getNameFirstRep().getFamily()).isEqualTo("Björk");
    assertThat(patient.getNameFirstRep().getGivenAsSingleString()).isEqualTo("Britta");
    assertThat(patient.getBirthDateElement().getValueAsString()).isEqualTo("1955-03-22");
  }

  @Test
  void oversatterKonMedConceptMap() {
    Patient patient = motor.transformera(BRITTA, Kanoniska.JOURNAL_PATIENT, new Patient());

    assertThat(patient.getGender()).isEqualTo(AdministrativeGender.FEMALE);
  }

  @Test
  void mapparBesok() {
    Encounter encounter = motor.transformera(BESOK, Kanoniska.JOURNAL_BESOK, new Encounter());

    assertThat(encounter.getMeta().hasProfile(Kanoniska.EDUCATION_ENCOUNTER)).isTrue();
    assertThat(encounter.getStatus()).isEqualTo(EncounterStatus.FINISHED);
    assertThat(encounter.getClass_().getCode()).isEqualTo("AMB");
    assertThat(encounter.getTypeFirstRep().getCodingFirstRep().getCode()).isEqualTo("besok");
    assertThat(encounter.getSubject().getReference()).isEqualTo("Patient/191212121212");
    assertThat(encounter.getPeriod().getStartElement().getValueAsString()).isEqualTo("2026-10-01T09:00:00+02:00");
    assertThat(encounter.getReasonCodeFirstRep().getCodingFirstRep().getCode()).isEqualTo("J45.9");
    assertThat(encounter.getServiceProvider().getIdentifier().getValue()).isEqualTo("SE2321000016-KURS");
  }

  @Test
  void losningarnaPaOvning52och53Fungerar() throws Exception {
    Path losningar = Path.of("..", "kursmaterial", "losningar", "modul-5");
    FmlMotor losning = new FmlMotor(List.of(
        Files.readString(losningar.resolve("patient.map")),
        Files.readString(losningar.resolve("besok.map"))));

    Patient patient = losning.transformera(BRITTA, Kanoniska.JOURNAL_PATIENT, new Patient());
    assertThat(patient.getTelecomFirstRep().getSystem()).isEqualTo(ContactPointSystem.PHONE);
    assertThat(patient.getTelecomFirstRep().getValue()).isEqualTo("070-111 22 33");

    Encounter encounter = losning.transformera(DIGITALT_BESOK, Kanoniska.JOURNAL_BESOK, new Encounter());
    assertThat(encounter.getTypeFirstRep().getCodingFirstRep().getCode()).isEqualTo("video");
    assertThat(encounter.getClass_().getCode()).isEqualTo("VR");
  }

  private static JsonObject json(String text) {
    return JsonParser.parseString(text).getAsJsonObject();
  }
}
