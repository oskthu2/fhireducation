package se.fhir.education.fasad.provider;

import java.util.Date;
import java.util.List;

import org.hl7.fhir.r4.model.Encounter;
import org.hl7.fhir.r4.model.IdType;
import org.springframework.stereotype.Component;

import ca.uhn.fhir.rest.annotation.IdParam;
import ca.uhn.fhir.rest.annotation.OptionalParam;
import ca.uhn.fhir.rest.annotation.Read;
import ca.uhn.fhir.rest.annotation.Search;
import ca.uhn.fhir.rest.param.DateRangeParam;
import ca.uhn.fhir.rest.param.ReferenceParam;
import ca.uhn.fhir.rest.server.IResourceProvider;
import ca.uhn.fhir.rest.server.exceptions.ResourceNotFoundException;
import se.fhir.education.fasad.legacy.Journalsystem;
import se.fhir.education.fasad.legacy.Journalsystem.BesokRad;
import se.fhir.education.fasad.mapping.EncounterMapper;

/**
 * Hanterar anrop mot /fhir/Encounter.
 * <ul>
 *   <li>GET /fhir/Encounter/B1001 (read)</li>
 *   <li>GET /fhir/Encounter?patient=191212121212 (search)</li>
 *   <li>GET /fhir/Encounter?patient=191212121212&amp;date=ge2026-10-01 (search)</li>
 * </ul>
 */
@Component
public class EncounterProvider implements IResourceProvider {

  private final Journalsystem journalsystem;

  public EncounterProvider(Journalsystem journalsystem) {
    this.journalsystem = journalsystem;
  }

  @Override
  public Class<Encounter> getResourceType() {
    return Encounter.class;
  }

  @Read
  public Encounter read(@IdParam IdType id) {
    return journalsystem.hamtaBesok(id.getIdPart())
        .map(EncounterMapper::toFhir)
        .orElseThrow(() -> new ResourceNotFoundException(id));
  }

  @Search
  public List<Encounter> search(
      @OptionalParam(name = Encounter.SP_PATIENT) ReferenceParam patient,
      @OptionalParam(name = Encounter.SP_DATE) DateRangeParam date) {

    List<BesokRad> rader = patient != null
        ? journalsystem.besokForPatient(patient.getIdPart())
        : journalsystem.allaBesok();

    return rader.stream()
        .map(EncounterMapper::toFhir)
        .filter(encounter -> date == null || inomIntervall(encounter.getPeriod().getStart(), date))
        .toList();
  }

  private static boolean inomIntervall(Date start, DateRangeParam date) {
    Date fran = date.getLowerBoundAsInstant();
    Date till = date.getUpperBoundAsInstant();
    return (fran == null || !start.before(fran)) && (till == null || !start.after(till));
  }
}
