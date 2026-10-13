# Modul 5 – Utveckling med HAPI FHIR, FHIR-fasader och API-säkerhet

**Tid:** 50 min (≈ 25 min genomgång och demo, 20 min övningar, 5 min summering)

## Mål

Efter modulen kan du

- beskriva olika sätt att erbjuda ett FHIR-API: FHIR-server med egen lagring, eller **fasad** ovanpå ett befintligt system
- förstå hur en HAPI FHIR-server är uppbyggd: *resource providers*, mappning och automatiskt CapabilityStatement
- göra REST-anrop mot ett FHIR-API: read, search, `_include`, `_summary` och `_count`
- känna till grunderna i API-säkerhet: TLS, OAuth 2.0, **SMART on FHIR** (scopes, launch, backend services) och relevanta **IHE-profiler**

## Arkitektur: FHIR-server eller FHIR-fasad?

| | FHIR-server med egen lagring (t.ex. HAPI JPA Server) | FHIR-fasad (t.ex. HAPI Plain Server) |
|---|---|---|
| Data | Lagras som FHIR-resurser i serverns databas | Ligger kvar i källsystemet och mappas vid varje anrop |
| Sökning | Alla standardsökparametrar "på köpet" | Bara det du implementerar |
| Skrivning | Full CRUD, versionshistorik | Ofta bara läsning, eller kontrollerad skrivning |
| Passar för | Nya tjänster, datadelning, test och utbildning | Befintliga journalsystem och verksamhetssystem |

Kursens exempel finns i [`hapi-fasad/`](../../hapi-fasad/README.md). Det är en fasad ovanpå ett simulerat
journalsystem med egna koder (`M`/`K`, `AVSL`, `BES` …) som mappas till kursens profiler.

## Övning 5.1 – Utforska ett FHIR-API (10 min)

Använd den publika HAPI-testservern `https://hapi.fhir.org/baseR4` (testdata, **inga riktiga personuppgifter!**)
i webbläsaren, eller fasaden om du kör den i Codespaces (`http://localhost:8080/fhir`).

1. `GET [bas]/metadata` – Vilka resurstyper stöds? Vilka sökparametrar finns för `Patient`?
2. `GET [bas]/Patient?family=Smith&_count=5` – Hur många träffar fick du? Var står nästa sida (`link`)?
3. `GET [bas]/Patient?_summary=count&family=Smith`
4. `GET [bas]/Encounter?_include=Encounter:subject&_count=3` – Vad gör `_include`?
5. `GET [bas]/Patient/[ett id]/_history` – Hur många versioner finns?

## Övning 5.2 – Mappa ett nytt fält i fasaden (10 min)

Journalsystemet har ett telefonnummer som fasaden inte mappar ännu.

1. Öppna `hapi-fasad/src/main/java/se/fhir/education/fasad/mapping/PatientMapper.java` i GitHub (pennan ✏️).
2. Leta upp kommentaren `ÖVNING 5.2` och lägg till mappningen till `Patient.telecom`:
   ```java
   if (rad.telefon() != null && !rad.telefon().isBlank()) {
     patient.addTelecom()
         .setSystem(ContactPointSystem.PHONE)
         .setValue(rad.telefon());
   }
   ```
   och importera `org.hl7.fhir.r4.model.ContactPoint.ContactPointSystem`.
3. Checka in. Följ arbetsflödet **HAPI-fasad** under *Actions*. Det bygger, kör testerna, startar servern och visar
   svaret på `GET Patient/191212121212` i sammanfattningen. Syns telefonnumret?
4. Diskutera: Britta saknar telefonnummer. Varför ska elementet då utelämnas helt i stället för att skickas tomt?

Lösning: [`../losningar/modul-5/PatientMapper.java`](../losningar/modul-5/PatientMapper.java)

## Övning 5.3 – Behörighet med scopes (demo eller extra)

Starta fasaden med `--fasad.sakerhet.aktiv=true` (se [hapi-fasad/README.md](../../hapi-fasad/README.md)) och prova
anropen med de olika demo-tokens. Läs `DemoAuthorizationInterceptor.java`:

- Vilket scope krävs för att söka vårdkontakter?
- Vad saknas jämfört med en riktig lösning? (Tips: vem utfärdar token, och hur valideras den?)

## Säkerhet i korthet

| Begrepp | Vad det är |
|---------|-----------|
| **TLS** | All FHIR-trafik ska gå över HTTPS. I vissa fall används ömsesidig TLS (mTLS) med t.ex. SITHS-certifikat |
| **OAuth 2.0** | Ramverk för att ge en klient en *access token* med begränsad behörighet |
| **SMART on FHIR – App Launch** | Standard för att starta en app från journalen (EHR launch) eller fristående, med kontext (patient, användare) och OpenID Connect |
| **SMART Backend Services** | System-till-system utan användare. Klienten autentiserar sig med en signerad JWT (client credentials) |
| **Scopes** | Vad token ger rätt till, t.ex. `patient/Observation.rs` eller `system/Patient.rs` (SMART v2) |
| **Capability discovery** | `GET [bas]/.well-known/smart-configuration` visar var auktorisationsservern finns och vad den stöder |
| **IHE IUA** | Internet User Authorization – IHE:s profil för OAuth-token i vårdintegrationer |
| **IHE ATNA / BALP** | Loggning av åtkomst (audit), BALP = Basic Audit Log Patterns med `AuditEvent` |
| **IHE PDQm / PIXm** | Patientsökning och identitetsmatchning över FHIR |
| **IHE MHD** | Dokumentdelning över FHIR (`DocumentReference`) |
| **IHE mCSD** | Katalog över vårdgivare, enheter och personal (`Organization`, `Location`, `PractitionerRole`) |

> Behörighet i vården handlar om mer än scopes: vårdrelation, samtycke, spärrar och sammanhållen journalföring
> måste också hanteras. FHIR och SMART ger byggstenarna men inte hela lösningen.
