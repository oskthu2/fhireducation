package se.fhir.education.fasad.mapping;

import java.time.LocalDateTime;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;

import org.hl7.fhir.r4.model.Coding;
import org.hl7.fhir.r4.model.DateTimeType;
import org.hl7.fhir.r4.model.Encounter;
import org.hl7.fhir.r4.model.Encounter.EncounterStatus;
import org.hl7.fhir.r4.model.Reference;

import se.fhir.education.fasad.legacy.Journalsystem.BesokRad;

/** Mappar en rad i journalsystemets BESOK-tabell till en FHIR Encounter enligt profilen EducationEncounter. */
public final class EncounterMapper {

  public static final String PROFIL = "http://example.org/fhir/education/kursig/StructureDefinition/EducationEncounter";
  public static final String KONTAKTTYP = "http://example.org/fhir/education/kursig/CodeSystem/kontakttyp";
  public static final String ACT_CODE = "http://terminology.hl7.org/CodeSystem/v3-ActCode";
  public static final String ICD10 = "http://hl7.org/fhir/sid/icd-10";
  public static final String HSAID = "urn:oid:1.2.752.29.4.19";

  private EncounterMapper() {
  }

  public static Encounter toFhir(BesokRad rad) {
    Encounter encounter = new Encounter();
    encounter.setId(rad.besoksId());
    encounter.getMeta().addProfile(PROFIL);

    // Systemets statuskoder -> FHIR:s (required) statuskoder
    encounter.setStatus(switch (rad.status()) {
      case "PLAN" -> EncounterStatus.PLANNED;
      case "PAGAR" -> EncounterStatus.INPROGRESS;
      case "AVSL" -> EncounterStatus.FINISHED;
      default -> EncounterStatus.UNKNOWN;
    });

    // Systemets kontakttyp -> kursens kodsystem Kontakttyp + Encounter.class
    String typkod = switch (rad.kontakttyp()) {
      case "BES" -> "besok";
      case "HEM" -> "hembesok";
      case "VID" -> "video";
      case "TEL" -> "telefon";
      default -> throw new IllegalArgumentException("Okänd kontakttyp: " + rad.kontakttyp());
    };
    encounter.addType().addCoding(new Coding(KONTAKTTYP, typkod, null));
    encounter.setClass_(switch (typkod) {
      case "hembesok" -> new Coding(ACT_CODE, "HH", "home health");
      case "video", "telefon" -> new Coding(ACT_CODE, "VR", "virtual");
      default -> new Coding(ACT_CODE, "AMB", "ambulatory");
    });

    encounter.setSubject(new Reference("Patient/" + rad.personnummer()));

    encounter.getPeriod().setStartElement(toDateTime(rad.start()));
    if (rad.slut() != null) {
      encounter.getPeriod().setEndElement(toDateTime(rad.slut()));
    }

    if (rad.diagnoskod() != null) {
      encounter.addReasonCode().addCoding(new Coding(ICD10, rad.diagnoskod(), null));
    }

    // Logisk referens: vi känner till vårdenhetens HSA-id men har ingen Organization-resurs att peka på.
    encounter.getServiceProvider().getIdentifier().setSystem(HSAID).setValue(rad.enhetHsaId());

    return encounter;
  }

  /** Journalsystemet lagrar lokal tid. FHIR:s dateTime med klockslag kräver tidszon. */
  private static DateTimeType toDateTime(LocalDateTime time) {
    return new DateTimeType(time.atZone(ZoneId.of("Europe/Stockholm")).format(DateTimeFormatter.ISO_OFFSET_DATE_TIME));
  }
}
