package se.fhir.education.fasad.legacy;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

import org.springframework.stereotype.Component;

/**
 * Simulerar ett befintligt journalsystem med egna tabeller och egna koder.
 * <p>
 * I verkligheten hade det här varit en databas, ett SOAP-API eller liknande.
 * Poängen är att datamodellen INTE är FHIR – fasaden måste mappa.
 */
@Component
public class Journalsystem {

  /** En rad i tabellen PATIENT. Kön lagras som "M"/"K", telefonnummer som fritext. */
  public record PatientRad(
      String personnummer,
      String fornamn,
      String efternamn,
      String kon,
      LocalDate fodelsedatum,
      String telefon) {
  }

  /** En rad i tabellen BESOK. Kontakttyp och status använder systemets egna koder. */
  public record BesokRad(
      String besoksId,
      String personnummer,
      String kontakttyp,   // BES = besök, HEM = hembesök, VID = video, TEL = telefon
      String status,       // PLAN = planerad, PAGAR = pågår, AVSL = avslutad
      LocalDateTime start,
      LocalDateTime slut,
      String diagnoskod,   // ICD-10
      String enhetHsaId) {
  }

  private final List<PatientRad> patienter = List.of(
      new PatientRad("191212121212", "Tolvan", "Tolvansson", "M", LocalDate.of(1912, 12, 12), "070-1234567"),
      new PatientRad("194208106593", "Arne", "Arnesson", "M", LocalDate.of(1942, 8, 10), "08-123 45 67"),
      new PatientRad("195503222340", "Britta", "Björk", "K", LocalDate.of(1955, 3, 22), null));

  private final List<BesokRad> besok = List.of(
      new BesokRad("B1001", "191212121212", "BES", "AVSL",
          LocalDateTime.of(2026, 10, 1, 9, 0), LocalDateTime.of(2026, 10, 1, 9, 30), "J45.9", "SE2321000016-KURS"),
      new BesokRad("B1002", "191212121212", "VID", "PLAN",
          LocalDateTime.of(2026, 11, 5, 13, 0), null, null, "SE2321000016-KURS"),
      new BesokRad("B2001", "194208106593", "HEM", "AVSL",
          LocalDateTime.of(2026, 9, 15, 10, 0), LocalDateTime.of(2026, 9, 15, 11, 0), "J44.1", "SE2321000016-KURS"));

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
