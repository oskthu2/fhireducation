package se.fhir.education.fasad.provider;

import java.util.List;

import org.hl7.fhir.r4.model.IdType;
import org.hl7.fhir.r4.model.Patient;
import org.springframework.stereotype.Component;

import ca.uhn.fhir.rest.annotation.IdParam;
import ca.uhn.fhir.rest.annotation.OptionalParam;
import ca.uhn.fhir.rest.annotation.Read;
import ca.uhn.fhir.rest.annotation.Search;
import ca.uhn.fhir.rest.param.TokenParam;
import ca.uhn.fhir.rest.server.IResourceProvider;
import ca.uhn.fhir.rest.server.exceptions.ResourceNotFoundException;
import se.fhir.education.fasad.legacy.Journalsystem;
import se.fhir.education.fasad.mapping.PatientMapper;

/**
 * Hanterar anrop mot /fhir/Patient.
 * <ul>
 *   <li>GET /fhir/Patient/191212121212 (read)</li>
 *   <li>GET /fhir/Patient?identifier=http://electronichealth.se/identifier/personnummer|191212121212 (search)</li>
 * </ul>
 * Metoderna som annoteras med @Read och @Search syns automatiskt i serverns CapabilityStatement.
 */
@Component
public class PatientProvider implements IResourceProvider {

  private final Journalsystem journalsystem;

  public PatientProvider(Journalsystem journalsystem) {
    this.journalsystem = journalsystem;
  }

  @Override
  public Class<Patient> getResourceType() {
    return Patient.class;
  }

  @Read
  public Patient read(@IdParam IdType id) {
    return journalsystem.hamtaPatient(id.getIdPart())
        .map(PatientMapper::toFhir)
        .orElseThrow(() -> new ResourceNotFoundException(id));
  }

  @Search
  public List<Patient> search(@OptionalParam(name = Patient.SP_IDENTIFIER) TokenParam identifier) {
    return journalsystem.allaPatienter().stream()
        .filter(rad -> identifier == null || matchar(identifier, rad.personnummer()))
        .map(PatientMapper::toFhir)
        .toList();
  }

  private static boolean matchar(TokenParam identifier, String personnummer) {
    boolean systemOk = identifier.getSystem() == null || identifier.getSystem().isEmpty()
        || PatientMapper.PERSONNUMMER.equals(identifier.getSystem());
    return systemOk && personnummer.equals(identifier.getValue());
  }
}
