package se.fhir.education.fasad.mapping;

import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.env.Environment;
import org.springframework.stereotype.Component;

import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

/**
 * Anropar journalsystemets proprietära REST-API och returnerar svaren som JSON.
 * <p>
 * Som standard anropas API:t i samma applikation (se legacy/JournalsystemApi.java). Sätt
 * {@code journalsystem.url} för att peka på ett annat system.
 */
@Component
public class JournalsystemKlient {

  private final HttpClient http = HttpClient.newHttpClient();
  private final Environment environment;
  private final String konfigureradUrl;

  public JournalsystemKlient(Environment environment, @Value("${journalsystem.url:}") String konfigureradUrl) {
    this.environment = environment;
    this.konfigureradUrl = konfigureradUrl;
  }

  public Optional<JsonObject> hamtaPatient(String personnummer) {
    return hamtaObjekt("/patienter/" + personnummer);
  }

  public List<JsonObject> allaPatienter() {
    return hamtaLista("/patienter");
  }

  public Optional<JsonObject> hamtaBesok(String besoksId) {
    return hamtaObjekt("/besok/" + besoksId);
  }

  public List<JsonObject> besokForPatient(String personnummer) {
    return hamtaLista("/patienter/" + personnummer + "/besok");
  }

  public List<JsonObject> allaBesok() {
    return hamtaLista("/besok");
  }

  private Optional<JsonObject> hamtaObjekt(String sokvag) {
    HttpResponse<String> svar = get(sokvag);
    if (svar.statusCode() == 404) {
      return Optional.empty();
    }
    return Optional.of(JsonParser.parseString(svar.body()).getAsJsonObject());
  }

  private List<JsonObject> hamtaLista(String sokvag) {
    List<JsonObject> lista = new ArrayList<>();
    for (JsonElement e : JsonParser.parseString(get(sokvag).body()).getAsJsonArray()) {
      lista.add(e.getAsJsonObject());
    }
    return lista;
  }

  private HttpResponse<String> get(String sokvag) {
    try {
      HttpRequest request = HttpRequest.newBuilder(URI.create(basUrl() + sokvag))
          .header("Accept", "application/json")
          .GET()
          .build();
      HttpResponse<String> svar = http.send(request, HttpResponse.BodyHandlers.ofString());
      if (svar.statusCode() != 200 && svar.statusCode() != 404) {
        throw new IllegalStateException("Journalsystemet svarade " + svar.statusCode() + " på " + sokvag);
      }
      return svar;
    } catch (IOException e) {
      throw new IllegalStateException("Kunde inte nå journalsystemet", e);
    } catch (InterruptedException e) {
      Thread.currentThread().interrupt();
      throw new IllegalStateException("Avbruten", e);
    }
  }

  private String basUrl() {
    if (!konfigureradUrl.isBlank()) {
      return konfigureradUrl;
    }
    return "http://localhost:" + environment.getProperty("local.server.port", "8080") + "/journalsystem-api";
  }
}
