package se.fhir.education.fasad.mapping;

/** Kanoniska URL:er som fasaden använder. */
public final class Kanoniska {

  public static final String KURS_IG = "http://example.org/fhir/education/kursig";
  public static final String EDUCATION_PATIENT = KURS_IG + "/StructureDefinition/EducationPatient";
  public static final String EDUCATION_ENCOUNTER = KURS_IG + "/StructureDefinition/EducationEncounter";
  public static final String PERSONNUMMER = "http://electronichealth.se/identifier/personnummer";

  /** Logiska modeller som beskriver journalsystemets JSON (se resources/fml/logiska-modeller). */
  public static final String JOURNAL_PATIENT =
      "http://example.org/fhir/education/journalsystem/StructureDefinition/JournalPatient";
  public static final String JOURNAL_BESOK =
      "http://example.org/fhir/education/journalsystem/StructureDefinition/JournalBesok";

  private Kanoniska() {
  }
}
