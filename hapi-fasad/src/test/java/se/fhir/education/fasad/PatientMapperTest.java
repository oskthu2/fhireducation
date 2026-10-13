package se.fhir.education.fasad;

import static org.assertj.core.api.Assertions.assertThat;

import java.time.LocalDate;

import org.hl7.fhir.r4.model.Enumerations.AdministrativeGender;
import org.hl7.fhir.r4.model.Patient;
import org.junit.jupiter.api.Test;

import se.fhir.education.fasad.legacy.Journalsystem.PatientRad;
import se.fhir.education.fasad.mapping.PatientMapper;

class PatientMapperTest {

  private final PatientRad britta =
      new PatientRad("195503222340", "Britta", "Björk", "K", LocalDate.of(1955, 3, 22), null);

  @Test
  void mapparPersonnummerTillIdentifier() {
    Patient patient = PatientMapper.toFhir(britta);

    assertThat(patient.getIdentifierFirstRep().getSystem()).isEqualTo(PatientMapper.PERSONNUMMER);
    assertThat(patient.getIdentifierFirstRep().getValue()).isEqualTo("195503222340");
  }

  @Test
  void mapparKonTillFhirKod() {
    assertThat(PatientMapper.toFhir(britta).getGender()).isEqualTo(AdministrativeGender.FEMALE);
  }

  @Test
  void angerProfilIMeta() {
    assertThat(PatientMapper.toFhir(britta).getMeta().hasProfile(PatientMapper.PROFIL)).isTrue();
  }

  @Test
  void mapparFodelsedatumUtanTidszonsforskjutning() {
    assertThat(PatientMapper.toFhir(britta).getBirthDateElement().getValueAsString()).isEqualTo("1955-03-22");
  }
}
