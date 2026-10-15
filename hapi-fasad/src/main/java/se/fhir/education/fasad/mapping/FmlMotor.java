package se.fhir.education.fasad.mapping;

import java.io.IOException;
import java.io.InputStream;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Proxy;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.hl7.fhir.instance.model.api.IBaseResource;
import org.hl7.fhir.r4.context.IWorkerContext;
import org.hl7.fhir.r4.elementmodel.Element;
import org.hl7.fhir.r4.elementmodel.JsonParser;
import org.hl7.fhir.r4.hapi.ctx.HapiWorkerContext;
import org.hl7.fhir.r4.model.Resource;
import org.hl7.fhir.r4.model.StructureDefinition;
import org.hl7.fhir.r4.model.StructureMap;
import org.hl7.fhir.r4.utils.StructureMapUtilities;
import org.springframework.core.io.ClassPathResource;
import org.springframework.stereotype.Component;

import com.google.gson.JsonObject;

import ca.uhn.fhir.context.FhirContext;
import ca.uhn.fhir.context.support.DefaultProfileValidationSupport;
import ca.uhn.fhir.context.support.IValidationSupport;

/**
 * Kör mappningar skrivna i FHIR Mapping Language (FML).
 * <p>
 * Mappningarna ligger i {@code src/main/resources/fml/*.map} och läses in när fasaden startar.
 * Källdatan (journalsystemets JSON) beskrivs av logiska modeller i {@code fml/logiska-modeller/}.
 * Själva transformeringen görs av StructureMapUtilities från HL7:s referensbibliotek.
 */
@Component
public class FmlMotor {

  /** Mappningsfiler som läses in. Varje mappning väljs utifrån källans logiska modell (canonical URL). */
  private static final List<String> MAPPNINGAR = List.of("fml/patient.map", "fml/besok.map");
  private static final List<String> LOGISKA_MODELLER = List.of(
      "fml/logiska-modeller/StructureDefinition-JournalPatient.json",
      "fml/logiska-modeller/StructureDefinition-JournalBesok.json");

  private final FhirContext fhirContext = FhirContext.forR4Cached();
  private final IWorkerContext worker;
  private final StructureMapUtilities fml;
  private final Map<String, StructureMap> mappningPerKalla = new HashMap<>();
  private final Map<String, StructureDefinition> logiskaModeller = new HashMap<>();

  public FmlMotor() throws IOException {
    this(lasAlla(MAPPNINGAR));
  }

  /** Används i testerna för att prova andra mappningar, t.ex. lösningen på övning 5.2. */
  public FmlMotor(List<String> fmlTexter) throws IOException {
    for (String fil : LOGISKA_MODELLER) {
      StructureDefinition sd = fhirContext.newJsonParser().parseResource(StructureDefinition.class, las(fil));
      logiskaModeller.put(sd.getUrl(), sd);
    }
    worker = utanSnapshotGenerering(new HapiWorkerContext(fhirContext, new KursValidationSupport()));
    fml = new StructureMapUtilities(worker);
    for (String text : fmlTexter) {
      StructureMap map = fml.parse(text, "fml");
      String kalla = map.getStructure().stream()
          .filter(s -> s.getMode() == StructureMap.StructureMapModelMode.SOURCE)
          .findFirst().orElseThrow().getUrl();
      mappningPerKalla.put(kalla, map);
    }
  }

  /**
   * Transformerar JSON från journalsystemet till en FHIR-resurs.
   *
   * @param json         svaret från journalsystemets API
   * @param logiskModell canonical URL för den logiska modell som beskriver JSON-strukturen
   * @param mal          en tom resurs som fylls i av mappningen, t.ex. {@code new Patient()}
   */
  public <T extends Resource> T transformera(JsonObject json, String logiskModell, T mal) {
    StructureDefinition sd = logiskaModeller.get(logiskModell);
    StructureMap map = mappningPerKalla.get(logiskModell);
    if (sd == null || map == null) {
      throw new IllegalArgumentException("Ingen logisk modell eller mappning för " + logiskModell);
    }
    // Journalsystemets JSON saknar "resourceType". Vi talar om för parsern vilken logisk modell den följer.
    JsonObject kopia = json.deepCopy();
    kopia.addProperty("resourceType", sd.getType());
    Element kalla = new JsonParser(worker).parse(kopia);
    fml.transform(null, kalla, map, mal);
    return mal;
  }

  /**
   * HAPI:s IWorkerContext kan inte generera snapshots, men JSON-parsern ber om det för logiska modeller.
   * Våra logiska modeller har redan en snapshot (genererad av SUSHI), så anropet kan ignoreras.
   */
  private static IWorkerContext utanSnapshotGenerering(IWorkerContext ctx) {
    return (IWorkerContext) Proxy.newProxyInstance(IWorkerContext.class.getClassLoader(),
        new Class<?>[] { IWorkerContext.class },
        (proxy, method, args) -> {
          if (method.getName().equals("generateSnapshot")) {
            return null;
          }
          try {
            return method.invoke(ctx, args);
          } catch (InvocationTargetException e) {
            throw e.getCause();
          }
        });
  }

  private static List<String> lasAlla(List<String> filer) throws IOException {
    List<String> texter = new ArrayList<>();
    for (String fil : filer) {
      texter.add(las(fil));
    }
    return texter;
  }

  private static String las(String fil) throws IOException {
    try (InputStream in = new ClassPathResource(fil).getInputStream()) {
      return new String(in.readAllBytes(), StandardCharsets.UTF_8);
    }
  }

  /** FHIR:s egna definitioner plus kursens logiska modeller. */
  private class KursValidationSupport implements IValidationSupport {
    private final DefaultProfileValidationSupport fhir = new DefaultProfileValidationSupport(fhirContext);

    @Override
    public FhirContext getFhirContext() {
      return fhirContext;
    }

    @Override
    public IBaseResource fetchStructureDefinition(String url) {
      StructureDefinition egen = logiskaModeller.get(url);
      return egen != null ? egen : fhir.fetchStructureDefinition(url);
    }

    @Override
    @SuppressWarnings("unchecked")
    public <T extends IBaseResource> List<T> fetchAllStructureDefinitions() {
      List<T> alla = new ArrayList<>();
      List<T> fhirs = fhir.fetchAllStructureDefinitions();
      if (fhirs != null) {
        alla.addAll(fhirs);
      }
      logiskaModeller.values().forEach(sd -> alla.add((T) sd));
      return alla;
    }
  }
}
