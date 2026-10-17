package se.fhir.education.fasad.legacy;

import java.util.List;
import java.util.Optional;

import org.springframework.stereotype.Component;

import com.fasterxml.jackson.annotation.JsonInclude;

/**
 * Simulerar ett befintligt journalsystem med egna tabeller och egna koder.
 * <p>
 * I verkligheten hade det här varit en databas bakom systemets eget API. Poängen är att datamodellen
 * INTE är FHIR: fältnamnen är svenska, koderna är systemets egna och strukturen är platt.
 */
@Component
public class Journalsystem {

  /** En rad i tabellen PATIENT. Kön lagras som "M"/"K", telefonnummer som fritext. */
  @JsonInclude(JsonInclude.Include.NON_NULL)
  public record PatientRad(
      String personnummer,
      String fornamn,
      String efternamn,
      String kon,
      String fodelsedatum,
      String telefon) {
  }

  /** En rad i tabellen BESOK. Kontakttyp och status använder systemets egna koder. */
  @JsonInclude(JsonInclude.Include.NON_NULL)
  public record BesokRad(
      String besoksId,
      String personnummer,
      String kontakttyp,   // BES = besök, HEM = hembesök, VID = video, TEL = telefon, DIG = digital kontakt
      String status,       // PLAN = planerad, PAGAR = pågår, AVSL = avslutad
      String start,        // ISO 8601 med tidszon
      String slut,
      String diagnoskod,   // ICD-10
      String enhetHsaId) {
  }

  private final List<PatientRad> patienter = List.of(
      new PatientRad("191212121212", "Tolvan", "Tolvansson", "M", "1912-12-12", "070-1234567"),
      new PatientRad("194208106593", "Arne", "Arnesson", "M", "1942-08-10", "08-123 45 67"),
      new PatientRad("195503222340", "Britta", "Björk", "K", "1955-03-22", null));

  private final List<BesokRad> besok = List.of(
      new BesokRad("B1001", "191212121212", "BES", "AVSL",
          "2026-10-01T09:00:00+02:00", "2026-10-01T09:30:00+02:00", "J45.9", "SE2321000016-KURS"),
      new BesokRad("B1002", "191212121212", "VID", "PLAN",
          "2026-11-05T13:00:00+01:00", null, null, "SE2321000016-KURS"),
      new BesokRad("B2001", "194208106593", "HEM", "AVSL",
          "2026-09-15T10:00:00+02:00", "2026-09-15T11:00:00+02:00", "J44.1", "SE2321000016-KURS"),
      // Kontakttypen DIG är ny i journalsystemet och finns inte med i mappningen ännu (övning 5.3)
      new BesokRad("B2002", "194208106593", "DIG", "PLAN",
          "2026-11-20T08:30:00+01:00", null, null, "SE2321000016-KURS"));

  public Optional<PatientRad> hamtaPatient(String personnummer) {
    return patienter.stream().filter(p -> p.personnummer().equals(personnummer)).findFirst();
  }

  public List<PatientRad> allaPatienter() {
    return patienter;
  }

  public Optional<BesokRad> hamtaBesok(String besoksId) {
    return besok.stream().filter(b -> b.besoksId().equals(besoksId)).findFirst();
  }

  public List<BesokRad> besokForPatient(String personnummer) {
    return besok.stream().filter(b -> b.personnummer().equals(personnummer)).toList();
  }

  public List<BesokRad> allaBesok() {
    return besok;
  }
}
