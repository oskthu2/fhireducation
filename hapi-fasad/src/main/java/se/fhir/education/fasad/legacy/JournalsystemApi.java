package se.fhir.education.fasad.legacy;

import java.util.List;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import se.fhir.education.fasad.legacy.Journalsystem.BesokRad;
import se.fhir.education.fasad.legacy.Journalsystem.PatientRad;

/**
 * Journalsystemets eget, proprietära REST-API (inte FHIR).
 * <p>
 * Det här är "det befintliga systemet" som FHIR-fasaden ska fronta. Prova i webbläsaren:
 * <ul>
 *   <li>GET /journalsystem-api/patienter/191212121212</li>
 *   <li>GET /journalsystem-api/patienter/191212121212/besok</li>
 *   <li>GET /journalsystem-api/besok/B1001</li>
 * </ul>
 */
@RestController
@RequestMapping("/journalsystem-api")
public class JournalsystemApi {

  private final Journalsystem journalsystem;

  public JournalsystemApi(Journalsystem journalsystem) {
    this.journalsystem = journalsystem;
  }

  @GetMapping("/patienter")
  public List<PatientRad> patienter() {
    return journalsystem.allaPatienter();
  }

  @GetMapping("/patienter/{personnummer}")
  public ResponseEntity<PatientRad> patient(@PathVariable String personnummer) {
    return ResponseEntity.of(journalsystem.hamtaPatient(personnummer));
  }

  @GetMapping("/patienter/{personnummer}/besok")
  public List<BesokRad> besokForPatient(@PathVariable String personnummer) {
    return journalsystem.besokForPatient(personnummer);
  }

  @GetMapping("/besok")
  public List<BesokRad> besok() {
    return journalsystem.allaBesok();
  }

  @GetMapping("/besok/{besoksId}")
  public ResponseEntity<BesokRad> besok(@PathVariable String besoksId) {
    return ResponseEntity.of(journalsystem.hamtaBesok(besoksId));
  }
}
