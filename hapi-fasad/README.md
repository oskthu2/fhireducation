# HAPI FHIR-fasad (modul 5)

Ett litet exempel på hur man "frontar" ett befintligt system med ett FHIR-API.

```
 Klient ──HTTP/FHIR──▶  FHIR-fasad (HAPI FHIR Plain Server)  ──▶  Befintligt journalsystem
                         • PatientProvider / EncounterProvider        (egna tabeller och koder)
                         • PatientMapper / EncounterMapper
                         • CapabilityStatement genereras automatiskt
```

Fasaden har ingen egen databas. Varje FHIR-anrop översätts till ett anrop mot
journalsystemet (`legacy/Journalsystem.java`) och svaret mappas till FHIR enligt kursens profiler
`EducationPatient` och `EducationEncounter`.

## Filer att titta på

| Fil | Vad den gör |
|-----|-------------|
| `legacy/Journalsystem.java` | Simulerar det befintliga systemet: tabellerna PATIENT och BESOK med egna koder |
| `mapping/PatientMapper.java` | Mappar en patientrad till `Patient` (identifier, namn, kön, födelsedatum) |
| `mapping/EncounterMapper.java` | Mappar en besöksrad till `Encounter` (status, typ, klass, period, diagnos, vårdenhet) |
| `provider/PatientProvider.java` | `GET /Patient/{id}` och `GET /Patient?identifier=` |
| `provider/EncounterProvider.java` | `GET /Encounter/{id}` och `GET /Encounter?patient=&date=` |
| `provider/CapabilityStatementCustomizer.java` | Lägger till IG, profiler och `instantiates` i CapabilityStatement |
| `security/DemoAuthorizationInterceptor.java` | Förenklat exempel på scope-baserad behörighet (SMART on FHIR) |

## Köra fasaden

### Utan lokal installation (GitHub Actions)

Checka in en ändring under `hapi-fasad/`. Arbetsflödet **HAPI-fasad** bygger, kör testerna,
startar servern och visar svaren på några anrop i körningens sammanfattning (fliken *Actions*).

### I GitHub Codespaces eller lokalt (Java 17 + Maven)

```bash
cd hapi-fasad
mvn spring-boot:run
```

Prova sedan i webbläsaren eller med curl:

- <http://localhost:8080/fhir/metadata> – CapabilityStatement
- <http://localhost:8080/fhir/Patient/191212121212>
- <http://localhost:8080/fhir/Patient?identifier=http://electronichealth.se/identifier/personnummer|194208106593>
- <http://localhost:8080/fhir/Encounter?patient=191212121212>
- <http://localhost:8080/fhir/Encounter?patient=191212121212&date=ge2026-10-15>

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
