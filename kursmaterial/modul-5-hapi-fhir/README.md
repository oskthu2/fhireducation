# Modul 5 – Utveckling med HAPI FHIR, FHIR-fasader med FML och API-säkerhet

**Tid:** 50 min (≈ 25 min genomgång och demo, 20 min övningar, 5 min summering)

## Mål

Efter modulen kan du

- beskriva olika sätt att erbjuda ett FHIR-API: FHIR-server med egen lagring, eller **fasad** ovanpå ett befintligt system
- förstå hur en HAPI FHIR-server är uppbyggd: *resource providers* och automatiskt CapabilityStatement
- läsa och ändra en mappning i **FHIR Mapping Language (FML)** som översätter ett proprietärt REST-API till FHIR
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
journalsystem som har ett eget, **proprietärt REST-API** med svenska fältnamn och egna koder
(`M`/`K`, `AVSL`, `BES` …). Fasaden hämtar JSON från API:t och översätter det till kursens profiler med
**FHIR Mapping Language**.

## FHIR Mapping Language (FML) i korthet

FML är HL7:s standardspråk för att beskriva hur data från en struktur översätts till en annan. En mappning
kompileras till resursen `StructureMap` och kan köras av en FML-motor, t.ex. HL7:s referensbibliotek,
HAPI FHIR eller Matchbox.

| Del | Exempel | Betydelse |
|-----|---------|-----------|
| `map` | `map "http://…/JournalPatientTillFhir" = "JournalPatientTillFhir"` | Mappningens identitet (canonical URL) |
| `conceptmap` | `s:M == t:male` | Kodöversättning, inbäddad ConceptMap |
| `uses` | `uses "…/JournalPatient" alias JournalPatient as source` | Källans och målets struktur |
| `group` | `group G(source src : JournalPatient, target tgt : Patient)` | En grupp regler med indata och utdata |
| Regel | `src.fodelsedatum as fd -> tgt.birthDate = fd "fodelsedatum";` | *källa* `->` *mål* `"namn";` |
| Översättning | `tgt.gender = translate(kon, '#kon', 'code')` | Slå upp koden i en ConceptMap |
| Nästling | `src -> tgt.name as namn then { … }` | Skapa ett element och fyll det med inre regler |

**Källan är inte FHIR.** Den beskrivs med **logiska modeller** (StructureDefinition med `kind = logical`),
som i kursen skrivs i FSH med nyckelordet `Logical:`, se `hapi-fasad/src/main/resources/fml/logiska-modeller/`.

**Varför FML i stället för kod?** Mappningen blir data som kan läsas, granskas och versionshanteras av
informatiker, inte bara av utvecklare. Den kan publiceras i en IG och köras av olika motorer. Nackdelen är
att FML är ett eget språk att lära sig, och att stödet varierar mellan verktyg och FHIR-versioner.

## Övning 5.1 – Utforska ett FHIR-API (5 min)

Använd den publika HAPI-testservern `https://hapi.fhir.org/baseR4` (testdata, **inga riktiga personuppgifter!**)
i webbläsaren, eller fasaden om du kör den i Codespaces (`http://localhost:8080/fhir`).

1. `GET [bas]/metadata` – Vilka resurstyper stöds? Vilka sökparametrar finns för `Patient`?
2. `GET [bas]/Patient?family=Smith&_count=5` – Hur många träffar fick du? Var står nästa sida (`link`)?
3. `GET [bas]/Patient?_summary=count&family=Smith`
4. `GET [bas]/Encounter?_include=Encounter:subject&_count=3` – Vad gör `_include`?
5. `GET [bas]/Patient/[ett id]/_history` – Hur många versioner finns?

## Övning 5.2 – Lägg till en regel i FML-mappningen (10 min)

Journalsystemet har ett telefonnummer som fasaden inte mappar ännu.

1. Jämför källan och resultatet: öppna senaste körningen av arbetsflödet **HAPI-fasad** under *Actions*.
   Sammanfattningen visar journalsystemets JSON och FHIR-resultatet för Tolvan. Var finns telefonnumret?
2. Öppna `hapi-fasad/src/main/resources/fml/patient.map` i GitHub (pennan ✏️) och leta upp kommentaren
   `ÖVNING 5.2`.
3. Lägg till en regel som mappar `src.telefon` till `Patient.telecom` med `system = phone`:
   ```
   src.telefon as tel -> tgt.telecom as telecom, telecom.system = 'phone', telecom.value = tel "telefon";
   ```
   Läs regeln högt: *för varje telefon i källan, skapa ett telecom i målet och sätt system och värde.*
4. Checka in. Följ arbetsflödet **HAPI-fasad** (≈ 1–2 min). Syns telefonnumret i FHIR-resultatet?
5. Diskutera: Britta saknar telefonnummer. Vad händer med regeln för henne? Varför är det bra?

Fel i FML-filen? Steget *Bygg och kör tester* blir rött. Leta efter `Error @rad, kolumn` i loggen.

Lösning: [`../losningar/modul-5/patient.map`](../losningar/modul-5/patient.map)

## Övning 5.3 (extra) – En ny kod i källsystemet

Journalsystemet har infört kontakttypen `DIG` (digital kontakt). Titta på Arnes besök B2002 i
sammanfattningen: i FHIR-resultatet saknas både `type` och `class`.

1. Varför? (Tips: titta på ConceptMap:arna `kontakttyp` och `klass` i `besok.map`.)
2. Vilken regel i profilen EducationEncounter bryter resultatet nu mot?
3. Lägg till `DIG` i båda ConceptMap:arna (till `video` respektive `VR`) och checka in.
4. Diskutera: hur upptäcker man i drift att källsystemet har fått en ny kod? (Tips: validering, modul 6.)

Lösning: [`../losningar/modul-5/besok.map`](../losningar/modul-5/besok.map)

## Övning 5.4 – Behörighet med scopes (demo eller extra)

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
