package se.fhir.education.fasad.provider;

import java.util.Date;
import java.util.List;

import org.hl7.fhir.r4.model.Encounter;
import org.hl7.fhir.r4.model.IdType;
import org.springframework.stereotype.Component;

import com.google.gson.JsonObject;

import ca.uhn.fhir.rest.annotation.IdParam;
import ca.uhn.fhir.rest.annotation.OptionalParam;
import ca.uhn.fhir.rest.annotation.Read;
import ca.uhn.fhir.rest.annotation.Search;
import ca.uhn.fhir.rest.param.DateRangeParam;
import ca.uhn.fhir.rest.param.ReferenceParam;
import ca.uhn.fhir.rest.server.IResourceProvider;
import ca.uhn.fhir.rest.server.exceptions.ResourceNotFoundException;
import se.fhir.education.fasad.mapping.FmlMotor;
import se.fhir.education.fasad.mapping.JournalsystemKlient;
import se.fhir.education.fasad.mapping.Kanoniska;

/**
 * Hanterar anrop mot /fhir/Encounter.
 * <ul>
 *   <li>GET /fhir/Encounter/B1001 (read)</li>
 *   <li>GET /fhir/Encounter?patient=191212121212 (search)</li>
 *   <li>GET /fhir/Encounter?patient=191212121212&amp;date=ge2026-10-15 (search)</li>
 * </ul>
 * Flödet: anropa journalsystemets API → JSON → FML-mappningen fml/besok.map → FHIR Encounter.
 */
@Component
public class EncounterProvider implements IResourceProvider {

  private final JournalsystemKlient journalsystem;
  private final FmlMotor fml;

  public EncounterProvider(JournalsystemKlient journalsystem, FmlMotor fml) {
    this.journalsystem = journalsystem;
    this.fml = fml;
  }

  @Override
  public Class<Encounter> getResourceType() {
    return Encounter.class;
  }

  @Read
  public Encounter read(@IdParam IdType id) {
    return journalsystem.hamtaBesok(id.getIdPart())
        .map(this::tillFhir)
        .orElseThrow(() -> new ResourceNotFoundException(id));
  }

  @Search
  public List<Encounter> search(
      @OptionalParam(name = Encounter.SP_PATIENT) ReferenceParam patient,
      @OptionalParam(name = Encounter.SP_DATE) DateRangeParam date) {

    List<JsonObject> rader = patient != null
        ? journalsystem.besokForPatient(patient.getIdPart())
        : journalsystem.allaBesok();

    return rader.stream()
        .map(this::tillFhir)
        .filter(encounter -> date == null || inomIntervall(encounter.getPeriod().getStart(), date))
        .toList();
  }

  private Encounter tillFhir(JsonObject json) {
    Encounter encounter = fml.transformera(json, Kanoniska.JOURNAL_BESOK, new Encounter());
    encounter.setId(json.get("besoksId").getAsString());
    return encounter;
  }

  private static boolean inomIntervall(Date start, DateRangeParam date) {
    Date fran = date.getLowerBoundAsInstant();
    Date till = date.getUpperBoundAsInstant();
    return start != null && (fran == null || !start.before(fran)) && (till == null || !start.after(till));
  }
}
