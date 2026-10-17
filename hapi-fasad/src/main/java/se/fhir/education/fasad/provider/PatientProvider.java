package se.fhir.education.fasad.provider;

import java.util.List;

import org.hl7.fhir.r4.model.IdType;
import org.hl7.fhir.r4.model.Patient;
import org.springframework.stereotype.Component;

import com.google.gson.JsonObject;

import ca.uhn.fhir.rest.annotation.IdParam;
import ca.uhn.fhir.rest.annotation.OptionalParam;
import ca.uhn.fhir.rest.annotation.Read;
import ca.uhn.fhir.rest.annotation.Search;
import ca.uhn.fhir.rest.param.TokenParam;
import ca.uhn.fhir.rest.server.IResourceProvider;
import ca.uhn.fhir.rest.server.exceptions.ResourceNotFoundException;
import se.fhir.education.fasad.mapping.FmlMotor;
import se.fhir.education.fasad.mapping.JournalsystemKlient;
import se.fhir.education.fasad.mapping.Kanoniska;

/**
 * Hanterar anrop mot /fhir/Patient.
 * <ul>
 *   <li>GET /fhir/Patient/191212121212 (read)</li>
 *   <li>GET /fhir/Patient?identifier=http://electronichealth.se/identifier/personnummer|191212121212 (search)</li>
 * </ul>
 * Flödet: anropa journalsystemets API → JSON → FML-mappningen fml/patient.map → FHIR Patient.
 * Metoderna som annoteras med @Read och @Search syns automatiskt i serverns CapabilityStatement.
 */
@Component
public class PatientProvider implements IResourceProvider {

  private final JournalsystemKlient journalsystem;
  private final FmlMotor fml;

  public PatientProvider(JournalsystemKlient journalsystem, FmlMotor fml) {
    this.journalsystem = journalsystem;
    this.fml = fml;
  }

  @Override
  public Class<Patient> getResourceType() {
    return Patient.class;
  }

  @Read
  public Patient read(@IdParam IdType id) {
    return journalsystem.hamtaPatient(id.getIdPart())
        .map(this::tillFhir)
        .orElseThrow(() -> new ResourceNotFoundException(id));
  }

  @Search
  public List<Patient> search(@OptionalParam(name = Patient.SP_IDENTIFIER) TokenParam identifier) {
    if (identifier == null) {
      return journalsystem.allaPatienter().stream().map(this::tillFhir).toList();
    }
    boolean systemOk = identifier.getSystem() == null || identifier.getSystem().isEmpty()
        || Kanoniska.PERSONNUMMER.equals(identifier.getSystem());
    if (!systemOk) {
      return List.of();
    }
    return journalsystem.hamtaPatient(identifier.getValue()).map(this::tillFhir).stream().toList();
  }

  private Patient tillFhir(JsonObject json) {
    Patient patient = fml.transformera(json, Kanoniska.JOURNAL_PATIENT, new Patient());
    // Det logiska id:t i FHIR-API:t är fasadens ansvar, inte mappningens.
    // Här används personnumret direkt – diskutera om det är lämpligt!
    patient.setId(json.get("personnummer").getAsString());
    return patient;
  }
}
