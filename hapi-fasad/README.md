# FHIR-fasad med FHIR Mapping Language (modul 5)

Ett exempel på hur man "frontar" ett befintligt system med ett FHIR-API. Journalsystemet har ett eget,
proprietärt REST-API. Fasaden hämtar data därifrån och översätter den till FHIR med mappningar skrivna i
**FHIR Mapping Language (FML)**.

```
 Klient ──FHIR──▶  FHIR-fasad (HAPI FHIR Plain Server)  ──JSON──▶  Journalsystemets REST-API
                    1. PatientProvider / EncounterProvider          /journalsystem-api/patienter/{pnr}
                    2. JournalsystemKlient hämtar JSON              /journalsystem-api/patienter/{pnr}/besok
                    3. FmlMotor kör fml/patient.map, fml/besok.map
                    4. CapabilityStatement genereras automatiskt
```

Mappningen är **data, inte kod**: för att ändra hur ett fält översätts ändrar du en regel i en `.map`-fil
och behöver inte röra Java-koden.

## Filer att titta på

| Fil | Vad den gör |
|-----|-------------|
| `src/main/resources/fml/patient.map` | FML: journalsystemets patient → `Patient`. **Här görs övning 5.2** |
| `src/main/resources/fml/besok.map` | FML: journalsystemets besök → `Encounter`, med ConceptMaps för koder. **Övning 5.3** |
| `src/main/resources/fml/logiska-modeller/` | Logiska modeller (FSH + JSON) som beskriver källans JSON |
| `legacy/JournalsystemApi.java` | Journalsystemets proprietära REST-API (svenska fältnamn, egna koder) |
| `mapping/JournalsystemKlient.java` | Anropar journalsystemets API |
| `mapping/FmlMotor.java` | Läser in mappningarna och kör dem med HL7:s FML-motor |
| `provider/PatientProvider.java` | `GET /Patient/{id}` och `GET /Patient?identifier=` |
| `provider/EncounterProvider.java` | `GET /Encounter/{id}` och `GET /Encounter?patient=&date=` |
| `provider/CapabilityStatementCustomizer.java` | Lägger till IG, profiler och `instantiates` i CapabilityStatement |
| `security/DemoAuthorizationInterceptor.java` | Förenklat exempel på scope-baserad behörighet (SMART on FHIR) |

Mer om FML och de logiska modellerna: [`src/main/resources/fml/README.md`](src/main/resources/fml/README.md).

## Köra fasaden

### Utan lokal installation (GitHub Actions)

Checka in en ändring under `hapi-fasad/`, till exempel i `patient.map`. Arbetsflödet **HAPI-fasad** bygger,
kör testerna, startar servern och visar journalsystemets JSON och FHIR-resultatet sida vid sida i
körningens sammanfattning (fliken *Actions*).

### I GitHub Codespaces eller lokalt (Java 17 + Maven)

```bash
cd hapi-fasad
mvn spring-boot:run
```

Jämför källan och resultatet i webbläsaren:

| Journalsystemets API (källa) | FHIR-fasaden (resultat) |
|------------------------------|-------------------------|
| <http://localhost:8080/journalsystem-api/patienter/191212121212> | <http://localhost:8080/fhir/Patient/191212121212> |
| <http://localhost:8080/journalsystem-api/patienter/191212121212/besok> | <http://localhost:8080/fhir/Encounter?patient=191212121212> |
| <http://localhost:8080/journalsystem-api/besok/B1001> | <http://localhost:8080/fhir/Encounter/B1001> |

Övrigt:

- <http://localhost:8080/fhir/metadata> – CapabilityStatement
- <http://localhost:8080/fhir/Patient?identifier=http://electronichealth.se/identifier/personnummer|194208106593>
- <http://localhost:8080/fhir/Encounter?patient=191212121212&date=ge2026-10-15>

Vill du följa en transformering regel för regel: starta med
`mvn spring-boot:run -Dspring-boot.run.arguments=--logging.level.org.hl7.fhir.r4.utils.StructureMapUtilities=INFO`.

### Med behörighetskontroll påslagen

```bash
mvn spring-boot:run -Dspring-boot.run.arguments=--fasad.sakerhet.aktiv=true

curl -i http://localhost:8080/fhir/Patient/191212121212                                              # 401
curl -i -H "Authorization: Bearer demo-token-patient" http://localhost:8080/fhir/Patient/191212121212 # 200
curl -i -H "Authorization: Bearer demo-token-patient" "http://localhost:8080/fhir/Encounter?patient=191212121212" # 403
curl -i -H "Authorization: Bearer demo-token-alla" "http://localhost:8080/fhir/Encounter?patient=191212121212"    # 200
```

## Övningar

Se [kursmaterial/modul-5-hapi-fhir](../kursmaterial/modul-5-hapi-fhir/README.md).
