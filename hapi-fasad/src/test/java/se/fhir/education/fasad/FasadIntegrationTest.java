package se.fhir.education.fasad;

import static org.assertj.core.api.Assertions.assertThat;

import org.hl7.fhir.r4.model.Bundle;
import org.hl7.fhir.r4.model.CapabilityStatement;
import org.hl7.fhir.r4.model.Encounter;
import org.hl7.fhir.r4.model.Patient;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.server.LocalServerPort;

import ca.uhn.fhir.context.FhirContext;
import ca.uhn.fhir.rest.client.api.IGenericClient;

/** Startar fasaden och anropar den med HAPI:s FHIR-klient – precis som ett annat system skulle göra. */
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class FasadIntegrationTest {

  @LocalServerPort
  private int port;

  private IGenericClient client;

  @BeforeEach
  void setUp() {
    client = FhirContext.forR4Cached().newRestfulGenericClient("http://localhost:" + port + "/fhir");
  }

  @Test
  void lasPatient() {
    Patient patient = client.read().resource(Patient.class).withId("191212121212").execute();

    assertThat(patient.getNameFirstRep().getFamily()).isEqualTo("Tolvansson");
  }

  @Test
  void sokPatientMedPersonnummer() {
    Bundle result = client.search().forResource(Patient.class)
        .where(Patient.IDENTIFIER.exactly()
            .systemAndIdentifier("http://electronichealth.se/identifier/personnummer", "194208106593"))
        .returnBundle(Bundle.class)
        .execute();

    assertThat(result.getEntry()).hasSize(1);
  }

  @Test
  void sokVardkontakterForPatient() {
    Bundle result = client.search().forResource(Encounter.class)
        .where(Encounter.PATIENT.hasId("191212121212"))
        .returnBundle(Bundle.class)
        .execute();

    assertThat(result.getEntry()).hasSize(2);
  }

  @Test
  void journalsystemetsApiArInteFhir() {
    String json = new org.springframework.web.client.RestTemplate()
        .getForObject("http://localhost:" + port + "/journalsystem-api/patienter/191212121212", String.class);

    assertThat(json).contains("\"efternamn\":\"Tolvansson\"").doesNotContain("resourceType");
  }

  @Test
  void lasVardkontakt() {
    Encounter encounter = client.read().resource(Encounter.class).withId("B1001").execute();

    assertThat(encounter.getStatus()).isEqualTo(Encounter.EncounterStatus.FINISHED);
    assertThat(encounter.getSubject().getReference()).isEqualTo("Patient/191212121212");
  }

  @Test
  void capabilityStatementBeskriverApiet() {
    CapabilityStatement cs = client.capabilities().ofType(CapabilityStatement.class).execute();

    assertThat(cs.getRestFirstRep().getResource())
        .extracting(CapabilityStatement.CapabilityStatementRestResourceComponent::getType)
        .contains("Patient", "Encounter");
    assertThat(cs.getInstantiates()).isNotEmpty();
  }
}
