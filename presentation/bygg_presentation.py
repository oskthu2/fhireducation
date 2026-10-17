"""Bygger kursens presentation: presentation/FHIR-utbildning.pptx

    pip install python-pptx
    python presentation/bygg_presentation.py

Varje bild har talarmanus (anteckningar). Kursens upplägg: 6 moduler à 50 minuter.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pptx.util import Inches  # noqa: E402

from pptx_helpers import (  # noqa: E402
    CONTENT_TOP, CONTENT_W, DARK, GREEN, GREEN_LIGHT, GREY, GREY_LIGHT, LIGHT, MARGIN, NAVY, ORANGE,
    ORANGE_LIGHT, RED, RED_LIGHT, TEAL, TEAL_LIGHT, WHITE, Deck,
)
from pptx.enum.shapes import MSO_SHAPE  # noqa: E402
from pptx.enum.text import PP_ALIGN  # noqa: E402
from pptx.dml.color import RGBColor  # noqa: E402

I = Inches
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "FHIR-utbildning.pptx")

d = Deck("FHIR i praktiken")


def two_col_bullets(title, left_items, right_items, notes, left_title=None, right_title=None, subtitle=None):
    s = d.content_slide(title, notes, subtitle=subtitle)
    w = (CONTENT_W - I(0.4)) / 2
    top = CONTENT_TOP
    if left_title:
        d.text(s, left_title, MARGIN, top, w, I(0.4), size=18, bold=True, color=TEAL)
        d.text(s, right_title, MARGIN + w + I(0.4), top, w, I(0.4), size=18, bold=True, color=TEAL)
        top += I(0.45)
    d.bullets(s, left_items, MARGIN, top, w, I(6.8) - top, size=18)
    d.bullets(s, right_items, MARGIN + w + I(0.4), top, w, I(6.8) - top, size=18)
    return s


def summary_slide(points, next_up, notes):
    s = d.content_slide("Sammanfattning", notes)
    d.bullets(s, points, MARGIN, CONTENT_TOP, I(8.2), I(5.2), size=19)
    d.box(s, "Härnäst\n\n" + next_up, I(9.3), CONTENT_TOP + I(0.2), I(3.4), I(2.6), fill=NAVY, color=WHITE,
          size=16)
    return s


# =====================================================================================
# INLEDNING
# =====================================================================================
d.title_slide(
    "FHIR i praktiken",
    "Profilering, Implementation Guides, terminologi och validering",
    "Utbildningsdag · 6 moduler à 50 minuter\nÖvningarna görs i ett eget repo på GitHub – ingen installation krävs",
    notes="""
Välkomna! Presentera dig själv kort.

Dagen är praktisk: vi varvar korta genomgångar med övningar. Alla övningar görs i deltagarnas egna repon på
GitHub, som byggs automatiskt med SUSHI och IG Publisher i GitHub Actions. Ingen lokal installation behövs.

Kontrollera att alla har skapat sitt repo från mallen och har en grön bock under Actions (förberedelseuppgift).
""",
)

s = d.content_slide("Dagens upplägg", notes="""
Sex moduler à 50 minuter med 10 minuters paus mellan varje, plus en kort inledning och en avslutning.
Tiderna är ett förslag, anpassa efter lokal och lunch.

Varje modul har samma rytm: genomgång, övning och en kort summering. Övningarna bygger på varandra.
Den som hamnar efter kan när som helst köra arbetsflödet "Kom ikapp" och få lösningen till sitt repo.
""")
d.table(s, [
    ["Tid", "Modul", "Innehåll"],
    ["09.00 – 09.15", "Inledning", "Upplägg, röd tråd, kontroll av allas repon"],
    ["09.15 – 10.05", "1  Läsa en FHIR-resurs", "Datatyper, terminologibindning, extensions, meta"],
    ["10.15 – 11.05", "2  Profiler och IG:er", "StructureDefinition, terminologi i praktiken, slicing, verktyg"],
    ["11.15 – 12.05", "3  FHIR Shorthand (FSH)", "Profil, terminologi, extension och slicing i FSH"],
    ["12.05 – 13.00", "Lunch", ""],
    ["13.00 – 13.50", "4  FHIRPath", "Uttryck, invarianter och constraints"],
    ["14.00 – 14.50", "5  Utveckling med HAPI FHIR", "FHIR-fasad med FML, REST, API-säkerhet, SMART, IHE"],
    ["15.00 – 15.50", "6  Följsamhet, krav och validering", "Kravställning, CapabilityStatement, discovery, validering"],
    ["15.50 – 16.05", "Avslutning", "Ta hem miljön: lokal installation och egen IG"],
], MARGIN, CONTENT_TOP + I(0.05), CONTENT_W, col_widths=[2.2, 4.2, 6.6], size=15, row_height=I(0.5))

s = d.content_slide("Mål med dagen", notes="""
Målet är praktisk tillämpning: efter dagen ska deltagarna kunna läsa och kravställa profiler, förstå vad en IG
innehåller, och ha en fungerande miljö för att fortsätta på egen hand.

Fråga gärna gruppen vilka roller som finns i rummet: kravställare, utvecklare, testare, arkitekter, informatiker.
Anpassa djupet efter det.
""")
d.bullets(s, [
    "**Läsa** FHIR-resurser, profiler och Implementation Guides med säkerhet",
    "**Förstå** terminologibindningar, extensions, slicing och invarianter, som är centrala begrepp vid kravställning",
    "**Skriva** egna profiler i FSH och bygga en IG med SUSHI och IG Publisher",
    "**Uttrycka** regler med FHIRPath",
    "**Känna till** hur man bygger ett FHIR-API ovanpå ett befintligt system, och hur det säkras",
    "**Kvalitetssäkra** med CapabilityStatement och validering mot profiler",
    "**Ta med dig** en fungerande miljö för eget arbete",
], MARGIN, CONTENT_TOP, I(12), I(5.3), size=20)

s = d.content_slide("Den röda tråden: Tolvan och hans vårdkontakt", notes="""
I stället för nya exempel i varje modul följer vi samma två resurser hela dagen: Patient och Encounter.
Testpersonen är Tolvan Tolvansson (191212121212), Skatteverkets klassiska testperson.

Modul 1: vi läser resurserna. Modul 2: vi tolkar profilerna. Modul 3: vi skriver profilerna i FSH.
Modul 4: vi lägger till regler med FHIRPath. Modul 5: vi exponerar data från ett "journalsystem" via ett FHIR-API, med mappningar i FHIR Mapping Language.
Modul 6: vi beskriver kraven i ett CapabilityStatement och validerar instanser.
""")
steps = [
    ("1", "Läsa", "Patient- och\nEncounter-resurs"),
    ("2", "Tolka", "Profilen\nEducationPatient"),
    ("3", "Skriva", "Profiler, terminologi,\nextension, slicing"),
    ("4", "Regler", "Invarianter\ni FHIRPath"),
    ("5", "Exponera", "FHIR-fasad\nmed FML"),
    ("6", "Kvalitetssäkra", "Capability-\nStatement och\nvalidering"),
]
w, gap = I(1.85), I(0.18)
for i, (n, head, body) in enumerate(steps):
    x = MARGIN + i * (w + gap)
    d.box(s, n, x, CONTENT_TOP + I(0.3), I(0.6), I(0.6), fill=ORANGE, color=WHITE, size=20, bold=True,
          shape=MSO_SHAPE.OVAL)
    d.box(s, f"**{head}**\n{body}", x, CONTENT_TOP + I(1.05), w, I(1.7), fill=TEAL_LIGHT, size=15)
    if i < len(steps) - 1:
        d.arrow(s, x + w + I(0.01), CONTENT_TOP + I(1.9), x + w + gap - I(0.01), CONTENT_TOP + I(1.9))
d.box(s, "👤  **Tolvan Tolvansson**  ·  personnummer 191212121212  ·  född 1912-12-12",
      MARGIN, CONTENT_TOP + I(3.15), CONTENT_W, I(0.6), fill=LIGHT, size=17)
d.box(s, "🏥  **Besök på Vårdcentralen Kursköping**  ·  2026-10-01 09.00–09.30  ·  astma (J45.9)",
      MARGIN, CONTENT_TOP + I(3.9), CONTENT_W, I(0.6), fill=LIGHT, size=17)

s = d.content_slide("Utbildningsmiljön: allt sker i GitHub", notes="""
Varje deltagare har ett eget repo skapat från kursens mall-repo (GitHub template).
Man ändrar filer direkt i webbläsaren (pennan, eller tryck punkt för github.dev) och checkar in.
Varje incheckning startar GitHub Actions, som kör SUSHI och IG Publisher och publicerar IG:n på GitHub Pages.
Det är samma upplägg som Ineras mall-repo för IG:er.

Det finns också ett Docker-spår för den som vill bygga lokalt, och GitHub Codespaces om man vill ha en
fullständig utvecklingsmiljö i webbläsaren.
""")
flow = [
    ("✏️", "Ändra fil", "i webbläsaren\n(pennan eller  .)"),
    ("✅", "Commit", "checka in\nändringen"),
    ("⚙️", "GitHub Actions", "SUSHI +\nIG Publisher"),
    ("🌐", "GitHub Pages", "din IG\npubliceras"),
    ("🔎", "qa.html", "läs fel och\nvarningar"),
]
w, gap = I(2.1), I(0.38)
for i, (icon, head, body) in enumerate(flow):
    x = MARGIN + i * (w + gap)
    d.box(s, f"{icon}\n**{head}**\n{body}", x, CONTENT_TOP + I(0.3), w, I(2.0),
          fill=TEAL_LIGHT if i != 2 else NAVY, color=DARK if i != 2 else WHITE, size=16)
    if i < len(flow) - 1:
        d.arrow(s, x + w + I(0.02), CONTENT_TOP + I(1.3), x + w + gap - I(0.02), CONTENT_TOP + I(1.3))
d.table(s, [
    ["Arbetsflöde (Actions)", "Startar när …", "Gör"],
    ["Bygg IG", "något ändras i test-ig/", "SUSHI + IG Publisher, publicerar på GitHub Pages"],
    ["Validera instanser", "något ändras i validering/ eller FSH", "FHIR Validator mot dina profiler"],
    ["HAPI-fasad", "något ändras i hapi-fasad/", "Bygger, testar och provkör FHIR-API:t"],
    ["Kom ikapp", "du startar det manuellt", "Hämtar lösningen efter vald modul"],
], MARGIN, CONTENT_TOP + I(2.65), CONTENT_W, col_widths=[2.6, 3.8, 5.6], size=14, row_height=I(0.45))

s = d.content_slide("Kom igång (förberedelse)", notes="""
Det här bör deltagarna ha gjort före kursen. Gå igenom det snabbt och hjälp den som fastnat under första övningen.

Vanliga problem:
- Repot skapades som privat på ett gratiskonto. Då fungerar inte GitHub Pages. Gör repot publikt.
- GitHub Pages är inte aktiverat. Settings, Pages, Deploy from a branch, gh-pages, root.
- Actions är avstängt i organisationen. Använd ett personligt konto.
""")
d.bullets(s, [
    "**1.** Öppna kursens mall-repo och klicka **Use this template → Create a new repository**",
    (1, "Välj ditt personliga konto och **Public** (krävs för GitHub Pages på gratiskonton)"),
    "**2.** Vänta tills arbetsflödet **Bygg IG** blivit grönt under fliken **Actions** (2–4 min)",
    "**3.** Aktivera GitHub Pages: **Settings → Pages → Deploy from a branch → gh-pages / (root)**",
    "**4.** Öppna `https://<ditt-konto>.github.io/<repo>/` – där finns din IG",
    "**5.** Testa: ändra titeln i `test-ig/sushi-config.yaml`, checka in och se den nya titeln efter bygget",
], MARGIN, CONTENT_TOP, I(8.4), I(5.3), size=18)
d.callout(s, "**Alternativ**\n\n• Lokalt med Docker (README)\n• GitHub Codespaces: Code → Codespaces → Create\n• Lokalt utan Docker: scripts/build-ig.sh",
          I(9.4), CONTENT_TOP + I(0.1), I(3.3), I(2.4), kind="info", size=15)
d.callout(s, "**Hamnat efter?**\n\nActions → **Kom ikapp** → Run workflow → välj modul",
          I(9.4), CONTENT_TOP + I(2.75), I(3.3), I(1.7), kind="warn", size=15)

# =====================================================================================
# MODUL 1
# =====================================================================================
d.module_slide(1, "Läsa en FHIR-resurs", [
    "känna igen strukturen i en resurs: id, meta, text, extensions och data",
    "skilja på primitiva och komplexa datatyper",
    "förklara terminologibindning och bindningsstyrkor",
    "hitta och tolka extensions, även på primitiva värden",
], [(25, "Genomgång"), (20, "Övning 1.1 och 1.2"), (5, "Summering")], notes="""
Modul 1 lägger grunden. Många har sett FHIR-JSON men inte läst den systematiskt.
Fokus: att kunna slå upp och tolka varje del av en resurs med hjälp av specifikationen.
""")

s = d.content_slide("FHIR på en minut", notes="""
FHIR = Fast Healthcare Interoperability Resources, en standard från HL7.
Bygger på webbteknik: REST, JSON/XML, OAuth.

Grundidén: information delas upp i små återanvändbara byggstenar (resurser) som kan refereras till varandra.
Basresurserna täcker det vanliga (80/20-regeln). Resten hanteras med profiler och extensions, och det är det dagen
handlar om.

Versioner: R4 (2019) är fortfarande den mest använda, även i Sverige (HL7 Sverige-basprofiler, Inera).
R5 kom 2023, och R6 är på väg. Kursen använder R4.
""")
d.bullets(s, [
    "**Resurser**: ~150 byggstenar som `Patient`, `Encounter`, `Observation`, `Condition`, `MedicationRequest`",
    "**Format**: JSON, XML (och RDF): samma innehåll, olika syntax",
    "**API**: RESTful – `GET [bas]/Patient/123`, sökning, transaktioner, operationer",
    "**80/20**: basresurserna täcker det gemensamma, och **profiler** och **extensions** anpassar dem",
    "**Versioner**: R4 (4.0.1) är vanligast i Sverige idag. R5 och R6 finns",
    "**Specifikationen** är det viktigaste verktyget: https://hl7.org/fhir/R4/",
], MARGIN, CONTENT_TOP, I(7.4), I(5.3), size=18)
d.code(s, """GET [bas]/Patient/patient-tolvan
Accept: application/fhir+json

200 OK
{
  "resourceType": "Patient",
  "id": "patient-tolvan",
  ...
}""", I(8.3), CONTENT_TOP + I(0.15), I(4.4), I(3.2), lang="http", size=13)

s = d.content_slide("Anatomin hos en resurs", notes="""
Gå igenom delarna uppifrån och ned. Alla resurser (DomainResource) har samma "ram":
- resourceType och id (logiskt id på servern)
- meta: metadata som servern ofta sätter (versionId, lastUpdated) och profiler/taggar
- text: narrativ, en människoläsbar XHTML-sammanfattning
- extension och modifierExtension
- därefter resursens egna element, i den ordning specifikationen anger (i XML är ordningen viktig)
""")
d.code(s, """{
  "resourceType": "Patient",
  "id": "patient-tolvan",
  "meta": {
    "versionId": "3",
    "lastUpdated": "2026-10-01T08:15:00+02:00",
    "profile": [ "http://example.org/.../EducationPatient" ]
  },
  "text": { "status": "generated", "div": "<div ...>...</div>" },
  "extension": [ { "url": "http://hl7.org/.../patient-interpreterRequired",
                   "valueBoolean": true } ],
  "identifier": [ { "system": "http://electronichealth.se/.../personnummer",
                    "value": "191212121212" } ],
  "name": [ { "use": "official", "family": "Tolvansson",
              "given": [ "Tolvan" ] } ],
  "gender": "male",
  "birthDate": "1912-12-12"
}""", MARGIN, CONTENT_TOP, I(8.1), I(5.4), lang="json", size=13)
labels = [
    ("resourceType + id", "Typ och logiskt id", NAVY),
    ("meta", "Version, profiler, taggar", TEAL),
    ("text", "Narrativ i XHTML", TEAL),
    ("extension", "Tillägg utöver basresursen", ORANGE),
    ("identifier, name …", "Resursens egna element", GREEN),
]
for i, (key, label, color) in enumerate(labels):
    y = CONTENT_TOP + I(0.1) + i * I(1.0)
    d.box(s, f"**{key}**\n{label}", I(8.95), y, I(3.75), I(0.85), fill=color, color=WHITE, size=15)

s = d.content_slide("Datatyper", notes="""
Primitiva datatyper har ett enkelt värde. Observera skillnaden mellan date och dateTime, och att en dateTime med
klockslag kräver tidszon.

Komplexa datatyper är återanvändbara strukturer. De viktigaste att kunna: Identifier, HumanName, CodeableConcept,
Coding, Reference, Period, Quantity.

Tips: klicka på datatypen i specifikationens tabell för att se dess delar.
""")
d.table(s, [
    ["Primitiv", "Exempel"],
    ["`string`", "\"Tolvansson\""],
    ["`boolean`", "true"],
    ["`date`", "\"1912-12-12\", \"1912-12\", \"1912\""],
    ["`dateTime`", "\"2026-10-01T09:00:00+02:00\""],
    ["`code`", "\"male\" (från en värdemängd)"],
    ["`uri` / `canonical`", "\"http://electronichealth.se/...\""],
    ["`decimal` / `integer`", "72.5 / 3"],
], MARGIN, CONTENT_TOP, I(5.6), col_widths=[2, 3.2], size=15, row_height=I(0.5))
d.table(s, [
    ["Komplex", "Innehåller"],
    ["`Identifier`", "system + value (+ use, type, period)"],
    ["`HumanName`", "family, given, use, prefix …"],
    ["`Coding`", "system + code + display"],
    ["`CodeableConcept`", "en eller flera Coding + text"],
    ["`Reference`", "reference, identifier, display"],
    ["`Period`", "start + end"],
    ["`Quantity`", "value + unit + system + code (UCUM)"],
], I(6.5), CONTENT_TOP, I(6.2), col_widths=[2.2, 4], size=15, row_height=I(0.5))

s = d.content_slide("Läsa specifikationen: elementtabellen", notes="""
Visa gärna live: https://hl7.org/fhir/R4/patient.html

Förklara kolumnerna: Name, Flags, Card. (kardinalitet), Type, Description & Constraints.
Flaggor: Σ = ingår i _summary, ?! = modifierande element (kan ändra betydelsen av resursen, t.ex. active,
deceased), I = har invarianter, N = normativ.

Kardinalitet: 0..1 valfri, 1..1 obligatorisk, 0..* lista, 1..* minst en.
""")
d.table(s, [
    ["Name", "Flags", "Card.", "Type", "Description & Constraints"],
    ["Patient", "I N", "", "DomainResource", "Information about an individual …"],
    ["  identifier", "Σ", "0..*", "Identifier", "An identifier for this patient"],
    ["  active", "?! Σ", "0..1", "boolean", "Whether this patient's record is in active use"],
    ["  name", "Σ", "0..*", "HumanName", "A name associated with the patient"],
    ["  gender", "Σ", "0..1", "code", "male | female | other | unknown\nAdministrativeGender (Required)"],
    ["  birthDate", "Σ", "0..1", "date", "The date of birth for the individual"],
    ["  maritalStatus", "", "0..1", "CodeableConcept", "Marital (civil) status\nMarital Status Codes (Extensible)"],
    ["  generalPractitioner", "", "0..*", "Reference(Organization |\nPractitioner | PractitionerRole)", "Patient's nominated primary care provider"],
], MARGIN, CONTENT_TOP, CONTENT_W, col_widths=[2.6, 0.9, 0.8, 3.0, 4.8], size=13, row_height=I(0.48))
d.text(s, "**Σ** ingår i sammanfattning   **?!** modifierande element   **I** har invarianter   **Card.** kardinalitet (min..max)",
       MARGIN, I(6.45), CONTENT_W, I(0.4), size=14, color=GREY)

s = d.content_slide("Referenser mellan resurser", notes="""
Reference är navet i FHIR: resurser pekar på varandra.

- Bokstavlig referens: "Patient/123" (relativ) eller en absolut URL. Mottagaren kan hämta resursen.
- Logisk referens: identifier, t.ex. HSA-id för en organisation, när man inte har (eller vill ha) en resurs att peka på.
  Vanligt i Sverige.
- display: bara text till människor. Den får aldrig användas för maskinell tolkning.
- contained: resursen bäddas in i den refererande resursen. Använd sparsamt.
""")
d.code(s, """"subject": {
  "reference": "Patient/patient-tolvan",
  "display": "Tolvan Tolvansson"
}""", MARGIN, CONTENT_TOP + I(0.1), I(5.8), I(1.6), lang="json", size=14, title="Bokstavlig (literal) referens")
d.code(s, """"serviceProvider": {
  "identifier": {
    "system": "urn:oid:1.2.752.29.4.19",
    "value": "SE2321000016-KURS"
  },
  "display": "Vårdcentralen Kursköping"
}""", MARGIN, CONTENT_TOP + I(2.05), I(5.8), I(2.6), lang="json", size=14, title="Logisk referens (identifier)")
d.bullets(s, [
    "**reference**: relativ (`Patient/123`) eller absolut URL. Kan hämtas",
    "**identifier**: pekar ut vad som avses utan att peka på en resurs, t.ex. HSA-id",
    "**display**: endast för människor",
    "**contained**: inbäddad resurs (`#id`). Används när resursen inte kan stå för sig själv",
    "Profilen avgör vilka **måltyper** som är tillåtna: `Reference(EducationPatient)`",
], I(6.9), CONTENT_TOP + I(0.1), I(5.8), I(5), size=17)

s = d.content_slide("Kodade värden och terminologi", notes="""
Tre centrala resurser: CodeSystem definierar koder (t.ex. SNOMED CT, ICD-10, eller ett lokalt kodverk).
ValueSet väljer ut koder ur ett eller flera kodsystem för ett visst syfte.
Bindningen kopplar ett element i en resurs till ett ValueSet.

I instansen: code (bara koden, system underförstått), Coding (system + code + display),
CodeableConcept (flera Coding för samma begrepp + fritext).

Exempel: samma diagnos kan kodas både i ICD-10 och SNOMED CT i samma CodeableConcept.
""")
d.box(s, "**CodeSystem**\nDefinierar koder\nSNOMED CT, ICD-10, LOINC,\nlokala kodverk", MARGIN, CONTENT_TOP + I(0.2), I(3.3), I(1.6), size=15)
d.box(s, "**ValueSet**\nVäljer ut koder för\nett syfte", I(4.5), CONTENT_TOP + I(0.2), I(3.3), I(1.6), size=15)
d.box(s, "**Element i resurs**\n`Encounter.type`\nbinds till ett ValueSet", I(8.4), CONTENT_TOP + I(0.2), I(4.3), I(1.6), size=15, fill=ORANGE_LIGHT)
d.arrow(s, I(3.95), CONTENT_TOP + I(1.0), I(4.45), CONTENT_TOP + I(1.0))
d.arrow(s, I(7.85), CONTENT_TOP + I(1.0), I(8.35), CONTENT_TOP + I(1.0))
d.text(s, "include", I(3.75), CONTENT_TOP + I(0.6), I(0.9), I(0.35), size=12, color=GREY, align=PP_ALIGN.CENTER)
d.text(s, "binding", I(7.65), CONTENT_TOP + I(0.6), I(0.9), I(0.35), size=12, color=GREY, align=PP_ALIGN.CENTER)
d.code(s, """"gender": "male",                          // code

"class": {                                 // Coding
  "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
  "code": "AMB", "display": "ambulatory" },

"maritalStatus": {                          // CodeableConcept
  "coding": [ { "system": "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus",
                "code": "W", "display": "Widowed" } ],
  "text": "Änkling" }""", MARGIN, CONTENT_TOP + I(2.2), CONTENT_W, I(3.1), lang="java", size=14)

s = d.content_slide("Bindningsstyrkor", notes="""
Det här är en av de viktigaste sakerna vid kravställning.

required: endast koder från värdemängden. Exempel: Patient.gender, Encounter.status.
extensible: använd värdemängdens kod om den finns, annars får en annan kod användas. Exempel: maritalStatus.
preferred: rekommendation.
example: bara illustration. Exempel: Encounter.type i R4.

I en profil får man skärpa (example till extensible till required) men aldrig lätta på en bindning.

Diskutera: vad händer i Sverige när ett internationellt ValueSet är extensible men saknar svenska begrepp?
""")
d.table(s, [
    ["Styrka", "Betydelse", "Exempel i R4"],
    ["**required**", "Koden MÅSTE komma från värdemängden", "`Patient.gender`, `Encounter.status`"],
    ["**extensible**", "Använd en kod härifrån om det finns en som passar, annars får annan kod användas", "`Patient.maritalStatus`, `Encounter.class`"],
    ["**preferred**", "Rekommenderad värdemängd", "`Patient.communication.language`"],
    ["**example**", "Bara ett exempel på möjliga koder", "`Encounter.type`, `Encounter.reasonCode`"],
], MARGIN, CONTENT_TOP + I(0.1), CONTENT_W, col_widths=[1.8, 6.2, 4], size=16, row_height=I(0.7))
d.callout(s, "I en profil får en bindning **skärpas** (example → extensible → required) men **aldrig** lättas upp.",
          MARGIN, I(5.35), CONTENT_W, I(0.7), kind="info", size=17)

s = d.content_slide("Extensions", notes="""
Extensions är FHIR:s inbyggda sätt att lägga till information som inte finns i basresursen. Alla får använda dem,
men de måste definieras (StructureDefinition) och identifieras med en url.

Enkel extension: url + ett value[x].
Komplex extension: url + nästlade extensions (ingen egen value).
Extension på primitivt värde: i JSON skrivs den i ett syskonelement med understreck, t.ex. _birthDate.

modifierExtension: ändrar betydelsen av resursen, t.ex. "denna ordination gäller INTE". En mottagare som inte
förstår en modifierExtension får inte bearbeta resursen. Används mycket sparsamt.
""")
d.code(s, """"extension": [
  {
    "url": "http://hl7.org/fhir/StructureDefinition/patient-interpreterRequired",
    "valueBoolean": true
  },
  {
    "url": "http://hl7.org/fhir/StructureDefinition/patient-nationality",
    "extension": [
      { "url": "code",
        "valueCodeableConcept": { "coding": [ { "code": "SE", ... } ] } }
    ]
  }
],
"birthDate": "1912-12-12",
"_birthDate": {
  "extension": [ {
    "url": "http://hl7.org/fhir/StructureDefinition/patient-birthTime",
    "valueDateTime": "1912-12-12T04:30:00+01:00" } ]
}""",
       MARGIN, CONTENT_TOP, I(8.0), I(4.45), lang="json", size=13)
d.box(s, "**Enkel**\nurl + value[x]", I(8.9), CONTENT_TOP + I(0.05), I(3.8), I(0.85), size=15)
d.box(s, "**Komplex**\nurl + nästlade extensions", I(8.9), CONTENT_TOP + I(1.25), I(3.8), I(0.85), size=15)
d.box(s, "**På primitivt värde**\n`_birthDate` i JSON", I(8.9), CONTENT_TOP + I(3.35), I(3.8), I(0.85), size=15)
d.callout(s, "**modifierExtension** ändrar betydelsen av resursen och får **inte** ignoreras av mottagaren.",
          MARGIN, I(6.0), CONTENT_W, I(0.7), kind="warn", size=16)

s = d.content_slide("meta och text", notes="""
meta.profile är ett påstående: "jag gör anspråk på att följa den här profilen". Det är inte en garanti.
Mottagaren måste validera. Och en resurs kan följa en profil utan att den står i meta.profile.

meta.security används för säkerhetsmärkning, t.ex. konfidentialitet. Den kan styra behörighet.
meta.tag är fria etiketter för arbetsflöden. De påverkar inte tolkningen.

text: narrativen ska spegla den strukturerade datan. status=generated betyder att den är genererad från datan.
""")
d.table(s, [
    ["Element", "Betydelse"],
    ["`meta.versionId`", "Versionen av resursen på servern (ändras vid varje uppdatering)"],
    ["`meta.lastUpdated`", "När resursen senast ändrades"],
    ["`meta.source`", "Varifrån resursen kommer"],
    ["`meta.profile`", "Profiler som resursen **gör anspråk** på att följa"],
    ["`meta.security`", "Säkerhetsmärkning, t.ex. konfidentialitet (`N` = normal)"],
    ["`meta.tag`", "Fria etiketter för arbetsflöden, som inte ändrar betydelsen"],
    ["`text`", "Människoläsbar narrativ (XHTML) med `status` generated / extensions / additional"],
], MARGIN, CONTENT_TOP, I(8.4), col_widths=[2.3, 6.1], size=15, row_height=I(0.55))
d.callout(s, "**meta.profile är ett påstående, inte en garanti.**\n\nMottagaren måste validera för att veta. En resurs kan också följa en profil utan att den står i meta.profile.",
          I(9.3), CONTENT_TOP + I(0.1), I(3.4), I(3.0), kind="warn", size=15)

d.exercise_slide("1.1 Tolka en Patient  ·  1.2 Hitta felet i en Encounter", [
    "**1.1** Öppna `Patient-tolvan.json`. Använd https://hl7.org/fhir/R4/patient.html",
    (1, "Vilka datatyper har identifier, name, gender, birthDate, maritalStatus, generalPractitioner?"),
    (1, "Hitta alla extensions. Vilken är enkel och vilken är komplex? Vad betyder `_birthDate`?"),
    (1, "Vad är skillnaden mellan referenserna i generalPractitioner och managingOrganization?"),
    (1, "Vad säger – och vad säger inte – `meta.profile`?"),
    "**1.2** Öppna `Encounter-tolvan-1.json`. Använd https://hl7.org/fhir/R4/encounter.html",
    (1, "Resursen har **ett fel** som gör den ogiltig. Hitta det! (Tips: bindningsstyrkor)"),
    (1, "Vilka kodsystem används? Vilka är internationella och vilka nationella?"),
    "Facit: `kursmaterial/modul-1-lasa-en-resurs/facit.md`",
], where="kursmaterial/modul-1-lasa-en-resurs/  (frågorna finns i README.md)", minutes=20, notes="""
Låt deltagarna arbeta i par. Gå runt och lyssna.

Vanliga frågor: skillnaden mellan Coding och CodeableConcept, vad _birthDate är, varför class är en Coding i R4.

Felet i Encounter: status "avslutad" i stället för "finished" (required-bindning).
Ta upp svaren gemensamt de sista 5 minuterna.
""")

summary_slide([
    "En resurs = **ram** (id, meta, text, extensions) + **egna element**",
    "Datatyper: **primitiva** och **komplexa**. Lär dig Identifier, CodeableConcept och Reference",
    "**Bindningsstyrkan** avgör hur strikt koderna styrs. required går aldrig att runda",
    "**Extensions** identifieras med url. modifierExtension får inte ignoreras",
    "**meta.profile** är ett påstående, och validering avgör",
    "Specifikationen (elementtabellen) är ditt viktigaste verktyg",
], "Modul 2\nProfiler och Implementation Guides", notes="""
Summera och koppla vidare: i modul 2 tittar vi på hur man beskriver krav på resurser, alltså profiler,
och hur de paketeras i en IG.
""")


# =====================================================================================
# MODUL 2
# =====================================================================================
d.module_slide(2, "Profiler och Implementation Guides", [
    "förklara vad en profil och en Implementation Guide är",
    "läsa en profil: differential, snapshot och Must Support",
    "förstå extensions och slicing i en profil",
    "känna till verktygen för profilering och validering",
], [(30, "Genomgång"), (15, "Övning 2.1 och 2.2"), (5, "Diskussion")], notes="""
Modul 2 handlar om att tolka krav. Det är här kravställare och utvecklare möts: profilen är kontraktet.
""")

s = d.content_slide("Varför profilera?", notes="""
Basresurserna är medvetet generella för att fungera i hela världen. Nästan allt är valfritt (0..1, 0..*), och
många bindningar är bara exempel.

I ett konkret sammanhang (en region, en tjänst, ett land) behöver vi säga mer: vilka element som krävs, vilka
kodverk som gäller, hur personnummer ska anges osv. Det gör vi med profiler.

Profilen är kontraktet mellan parterna och kan valideras maskinellt.
""")
d.bullets(s, [
    "Basresurserna är **generella**: nästan allt är valfritt, och många bindningar är bara exempel",
    "I ett **sammanhang** (land, region, tjänst) behöver vi precisera:",
    (1, "Vilka element **krävs**? Vilka ska kunna hanteras (**Must Support**)?"),
    (1, "Vilka **kodverk** gäller? (ICD-10-SE, SNOMED CT, KV …)"),
    (1, "Hur anges **personnummer**, **HSA-id** och samordningsnummer?"),
    (1, "Vilken svensk information saknas i basen (**extensions**)?"),
    "Profilen blir ett **maskinläsbart kontrakt** som kan valideras automatiskt",
    "Profiler bygger på varandra: bas → nationellt → regionalt → tjänst",
], MARGIN, CONTENT_TOP, I(7.2), I(5.3), size=19)
layers = [
    ("FHIR R4 – basresurser", NAVY, WHITE),
    ("HL7 Sverige – basprofiler", TEAL, WHITE),
    ("Nationella IG:er (t.ex. Inera)", RGBColor(0x3B, 0x9A, 0xA2), WHITE),
    ("Regional / tjänstespecifik IG", TEAL_LIGHT, DARK),
    ("Kursens IG – EducationPatient", ORANGE_LIGHT, DARK),
]
for i, (label, fill, color) in enumerate(layers):
    inset = I(0.25) * i
    d.box(s, label, I(8.1) + inset, CONTENT_TOP + I(0.2) + i * I(0.95), I(4.6) - 2 * inset, I(0.8),
          fill=fill, color=color, size=15, bold=True)

s = d.content_slide("Vad kan en profil göra?", notes="""
En profil kan bara begränsa, inte utöka. Allt som är giltigt mot profilen måste också vara giltigt mot basen.
Det är grunden för att system som inte känner till profilen ändå kan läsa datan.

Det enda sättet att lägga till är extensions, och de är en del av basens regelverk.
""")
d.table(s, [
    ["Mekanism", "Exempel", "FSH (modul 3)"],
    ["Kardinalitet", "name 0..* → 1..*", "`* name 1..*`"],
    ["Must Support", "birthDate ska kunna hanteras", "`* birthDate MS`"],
    ["Begränsa typer", "subject bara till EducationPatient", "`* subject only Reference(EducationPatient)`"],
    ["Terminologibindning", "Encounter.type från Kontakttyp", "`* type from KontakttypVS (extensible)`"],
    ["Fast värde / mönster", "identifier.system = personnummer", "`* identifier.system = $personnummer`"],
    ["Extensions", "tolkbehov, skyddad identitet", "`* extension contains …`"],
    ["Slicing", "identifier: personnummer + samordningsnummer", "`* identifier contains …`"],
    ["Invarianter", "personnummer = 12 siffror", "`* obeys edu-pat-1`"],
], MARGIN, CONTENT_TOP, CONTENT_W, col_widths=[2.4, 4.4, 5.2], size=15, row_height=I(0.5))
d.callout(s, "En profil får bara **begränsa** basen. Allt som är giltigt mot profilen är också giltigt mot basresursen. Det enda sättet att lägga till är **extensions**.",
          MARGIN, I(6.15), CONTENT_W, I(0.7), kind="info", size=16)

s = d.content_slide("StructureDefinition: differential och snapshot", notes="""
En profil är en StructureDefinition med derivation = constraint och en baseDefinition.

Differential: bara ändringarna. Det är det man skriver (i FSH eller Forge).
Snapshot: hela den resulterande definitionen, beräknad från basen + differential. Det är vad validatorn använder.

I IG:n finns flikar för båda, och dessutom Key Elements (de viktigaste) och Must Support-vyn.
""")
d.code(s, """{
  "resourceType": "StructureDefinition",
  "url": "http://example.org/.../StructureDefinition/EducationPatient",
  "name": "EducationPatient",
  "type": "Patient",
  "baseDefinition": "http://hl7.org/fhir/StructureDefinition/Patient",
  "derivation": "constraint",
  "differential": {
    "element": [
      { "id": "Patient.identifier", "path": "Patient.identifier",
        "min": 1, "mustSupport": true },
      { "id": "Patient.birthDate", "path": "Patient.birthDate",
        "min": 1, "mustSupport": true }
    ]
  }
}""", MARGIN, CONTENT_TOP, I(7.4), I(5.2), lang="json", size=13)
d.box(s, "**Differential**\nBara det profilen ändrar\n(det man skriver)", I(8.4), CONTENT_TOP + I(0.2), I(4.3), I(1.3), size=16)
d.box(s, "**+ Basresurs**", I(8.4), CONTENT_TOP + I(1.7), I(4.3), I(0.6), size=16, fill=LIGHT)
d.box(s, "**= Snapshot**\nHela den resulterande strukturen\n(det validatorn använder)", I(8.4), CONTENT_TOP + I(2.5), I(4.3), I(1.3), size=16, fill=NAVY, color=WHITE)
d.text(s, "Canonical URL = globalt unik identifierare för profilen", I(8.4), CONTENT_TOP + I(4.1), I(4.3), I(0.8), size=15, color=GREY)

s = d.content_slide("Must Support – vad betyder det?", notes="""
Must Support (MS) är en flagga i profilen. FHIR-specifikationen definierar inte exakt vad den betyder.
Det måste varje IG göra själv, och det är en vanlig källa till missförstånd.

Typiska definitioner: avsändaren SKA skicka elementet om informationen finns. Mottagaren SKA kunna ta emot,
lagra och/eller visa det, och får inte avvisa meddelandet för att elementet finns.

MS är inte samma sak som obligatoriskt (min = 1). Ett element kan vara 0..1 MS.
""")
d.bullets(s, [
    "Flaggan **MS** säger att elementet är viktigt i det här sammanhanget",
    "**Exakt vad det innebär definieras i varje IG**, inte i FHIR-specifikationen",
    "Vanlig definition:",
    (1, "**Avsändare** SKA skicka elementet om informationen finns"),
    (1, "**Mottagare** SKA kunna ta emot och hantera (lagra, visa) elementet"),
    "MS är **inte** samma sak som obligatoriskt: `0..1 MS` är vanligt",
    "Vid kravställning: **definiera MS tydligt** i IG:ns inledning",
], MARGIN, CONTENT_TOP, I(7.6), I(5.2), size=19)
d.table(s, [
    ["Kardinalitet", "MS", "Betydelse"],
    ["0..1", "", "Får skickas"],
    ["0..1", "MS", "Ska skickas om det finns"],
    ["1..1", "MS", "Ska alltid skickas"],
    ["0..0", "", "Får inte skickas"],
], I(8.5), CONTENT_TOP + I(0.2), I(4.2), col_widths=[1.4, 0.8, 2.6], size=15, row_height=I(0.55))

s = d.content_slide("Terminologibindning i praktiken", notes="""
En bindning i profilen är bara halva jobbet. Vid validering används en terminologiserver för att räkna fram
värdemängder ($expand) och kontrollera koder ($validate-code). IG Publisher och FHIR Validator använder
tx.fhir.org som standard. Nationellt kan andra servrar gälla.

Viktigt för kravställare:
- required: kod utanför värdemängden ger fel.
- extensible: kod utanför ger bara varning, eftersom validatorn inte kan avgöra om en passande kod fanns.
  Det ser vi i övning 6.3.
- Versioner: SNOMED CT har editioner (svensk edition) och versioner. Ange version när det spelar roll.
- Display-texter kontrolleras. Vi råkade själva få fel när ICD-10-displayen var på svenska.

Svenska kodverk: SNOMED CT svensk edition, ICD-10-SE, ATC, NPU, KVÅ och nationella kodverk från Socialstyrelsen
och Inera. HL7 Sveriges basprofiler binder t.ex. civilstånd till ett svenskt ValueSet.
""")
d.box(s, "**Profil**\n`type from KontakttypVS`\n`(extensible)`", MARGIN, CONTENT_TOP + I(0.1), I(3.0), I(1.3), size=15)
d.box(s, "**Validator / IG Publisher**\nKontrollerar instansen", I(4.3), CONTENT_TOP + I(0.1), I(3.6), I(1.3), size=15, fill=NAVY, color=WHITE)
d.box(s, "**Terminologiserver**\n`$expand`  ·  `$validate-code`\ntx.fhir.org eller nationell", I(9.0), CONTENT_TOP + I(0.1), I(3.7), I(1.3), size=15, fill=ORANGE_LIGHT)
d.arrow(s, I(3.65), CONTENT_TOP + I(0.75), I(4.25), CONTENT_TOP + I(0.75))
d.arrow(s, I(7.95), CONTENT_TOP + I(0.75), I(8.95), CONTENT_TOP + I(0.75))
d.table(s, [
    ["Situation", "Resultat vid validering"],
    ["Kod utanför värdemängd, bindning **required**", "❌ Fel"],
    ["Kod utanför värdemängd, bindning **extensible**", "⚠️ Varning (validatorn vet inte om en passande kod fanns)"],
    ["Koden finns inte i kodsystemet den anger", "❌ Fel"],
    ["Fel display-text för koden", "❌ Fel eller ⚠️ varning"],
], MARGIN, CONTENT_TOP + I(1.7), I(7.6), col_widths=[4.0, 3.6], size=14, row_height=I(0.5))
d.callout(s, "**Svenska kodverk**\nSNOMED CT (svensk edition), ICD-10-SE, ATC, NPU, KVÅ, nationella kodverk (Socialstyrelsen, Inera)\n\n**Vid kravställning:** ange ValueSet (canonical + version), styrka och terminologiserver.",
          I(8.5), CONTENT_TOP + I(1.7), I(4.2), I(3.0), kind="info", size=14)

s = d.content_slide("Extensions i en profil", notes="""
Två steg: 1) extensionen definieras som en egen StructureDefinition med url, context (var den får användas) och
value[x]. 2) Profilen säger att extensionen får eller ska förekomma, genom att lägga till en slice på extension.

Använd i första hand befintliga extensions: från FHIR-standarden (core/extensions-paketet), HL7 Sverige eller
nationella IG:er. Skapa egna bara när inget passar.
""")
d.box(s, "**1. Definiera extensionen**\nStructureDefinition (type = Extension)\n• url – unik identitet\n• context – var den får användas\n• value[x] – datatyp",
      MARGIN, CONTENT_TOP + I(0.1), I(5.6), I(2.2), size=16, align=PP_ALIGN.LEFT, fill=TEAL_LIGHT)
d.box(s, "**2. Använd den i profilen**\nslice på Patient.extension\n• kardinalitet (0..1, 1..1 …)\n• Must Support",
      MARGIN, CONTENT_TOP + I(2.5), I(5.6), I(1.8), size=16, align=PP_ALIGN.LEFT, fill=ORANGE_LIGHT)
d.code(s, """Extension: SkyddadIdentitet
Id: SkyddadIdentitet
Context: Patient
* value[x] only boolean

Profile: EducationPatient
Parent: Patient
* extension contains
    $patient-interpreterRequired
      named tolkbehov 0..1 MS and
    SkyddadIdentitet
      named skyddadIdentitet 0..1 MS""", I(6.6), CONTENT_TOP + I(0.1), I(6.1), I(3.4), size=14)
d.callout(s, "**Återanvänd först:** FHIR-standarden → HL7 Sverige → nationella IG:er. Skapa egna extensions bara när inget passar.",
          I(6.6), CONTENT_TOP + I(3.75), I(6.1), I(0.95), kind="info", size=15)

s = d.content_slide("Slicing – dela upp en lista", notes="""
Slicing används när ett upprepande element innehåller olika "sorters" saker som ska ha olika regler.
Klassiskt exempel: identifier, där personnummer och samordningsnummer har olika system och regler.

För varje slice anges namn, kardinalitet och egna regler. Slicingen har en diskriminator, alltså vad i datan som
avgör vilken slice ett element tillhör, och regler (open/closed/openAtEnd) för element som inte matchar.

Extensions är för övrigt alltid slicade på url. Det är så profilen säger vilka extensions som får förekomma.
""")
d.box(s, "**Patient.identifier**  0..*\ndiscriminator: value @ system  ·  rules: open", MARGIN, CONTENT_TOP + I(0.1), I(5.8), I(0.95), fill=NAVY, color=WHITE, size=16)
d.box(s, "**personnummer**  0..1 MS\nsystem = http://electronichealth.se/identifier/personnummer", I(1.2), CONTENT_TOP + I(1.35), I(5.2), I(0.95), size=14)
d.box(s, "**samordningsnummer**  0..1 MS\nsystem = …/identifier/samordningsnummer", I(1.2), CONTENT_TOP + I(2.45), I(5.2), I(0.95), size=14)
d.box(s, "**(övriga)**  tillåts eftersom slicingen är öppen", I(1.2), CONTENT_TOP + I(3.55), I(5.2), I(0.7), size=14, fill=LIGHT)
d.table(s, [
    ["Diskriminator", "Matchar på"],
    ["`value`", "Fast värde på en sökväg (t.ex. system)"],
    ["`pattern`", "Mönster (t.ex. en Coding i CodeableConcept)"],
    ["`type`", "Datatyp (t.ex. value[x])"],
    ["`profile`", "Att elementet följer en viss profil"],
    ["`exists`", "Att ett element finns eller inte finns"],
], I(6.9), CONTENT_TOP + I(0.1), I(5.8), col_widths=[1.6, 4.2], size=15, row_height=I(0.5))
d.table(s, [
    ["Regel", "Element som inte matchar …"],
    ["`open`", "tillåts"],
    ["`closed`", "är fel"],
    ["`openAtEnd`", "tillåts sist i listan"],
], I(6.9), CONTENT_TOP + I(3.35), I(5.8), col_widths=[1.6, 4.2], size=15, row_height=I(0.45))

s = d.content_slide("Slicing: urvalet försvinner i instansen", notes="""
Viktig poäng: slice-namnet finns bara i profilen. I instansen finns bara en lista.
Mottagaren eller validatorn måste själv räkna ut vilken slice varje element tillhör med hjälp av diskriminatorn.

Konsekvenser att diskutera:
- Diskriminatorn måste ha ett fast värde i varje slice, annars går det inte att avgöra.
- Ett stavfel i system gör att elementet inte matchar någon slice. Med open slicing räknas det som "övrigt",
  och slicens regler (t.ex. format på personnumret) kontrolleras aldrig.
- Ordningen i listan betyder inget om inte ordered = true.
- Det är lätt att tro att instansen "har" en personnummer-slice. Det är tolkningen, inte datan.
""")
d.code(s, """* identifier contains
    personnummer 0..1 MS and
    samordningsnummer 0..1 MS
* identifier[personnummer].system =
    $personnummer""", MARGIN, CONTENT_TOP + I(0.05), I(5.5), I(2.2), size=15, title="Profilen (FSH)")
d.code(s, """"identifier": [
  { "system": ".../samordningsnummer",  // samordningsnr
    "value": "199001721234" },
  { "system": ".../personnummer",       // personnummer
    "value": "199001012384" },
  { "system": ".../personumer",         // ingen slice!
    "value": "19900101-2384" }
]""", I(6.4), CONTENT_TOP + I(0.05), I(6.3), I(3.2), lang="json", size=16, title="Instansen (JSON) – inga slice-namn!")
d.callout(s, "Validatorn räknar ut vilken slice varje element tillhör med hjälp av **diskriminatorn**. Ett stavfel i `system` ger ingen slice. Med öppen slicing är det då **inte ett fel**, och slicens regler kontrolleras aldrig.",
          MARGIN, CONTENT_TOP + I(3.55), CONTENT_W, I(1.1), kind="warn", size=16)

s = d.content_slide("Vad är en Implementation Guide?", notes="""
En IG är en samling konformitetsresurser och dokumentation som tillsammans beskriver hur FHIR ska användas i ett
visst sammanhang.

Den publiceras som en webbplats (för människor) och som ett npm-paket package.tgz (för maskiner: validatorer,
servrar och andra IG:er som bygger vidare).

Varje resurs har en canonical URL. IG:n har ett paket-id och en version, och andra IG:er anger beroenden på
paket-id#version.
""")
items = [
    ("Profiler", "StructureDefinition"),
    ("Extensions", "StructureDefinition"),
    ("Terminologi", "CodeSystem, ValueSet, ConceptMap"),
    ("Exempel", "instanser"),
    ("Krav på system", "CapabilityStatement"),
    ("Sökparametrar\noch operationer", "SearchParameter,\nOperationDefinition"),
    ("Dokumentation", "sidor i Markdown"),
]
for i, (head, body) in enumerate(items):
    col, row = i % 4, i // 4
    d.box(s, "\n".join(f"**{h}**" for h in head.split("\n")) + "\n" + body, MARGIN + col * I(3.05), CONTENT_TOP + I(0.1) + row * I(1.5), I(2.85), I(1.3), size=15)
d.box(s, "📦 **package.tgz**\nför maskiner", MARGIN + 3 * I(3.05), CONTENT_TOP + I(1.6), I(2.85), I(1.3), size=15, fill=NAVY, color=WHITE)
d.bullets(s, [
    "Publiceras som **webbplats** (för människor) och **npm-paket** (för validatorer, servrar och andra IG:er)",
    "Identifieras med **paket-id** och **version**, t.ex. `fhir.education.kursig#0.1.0`. Beroenden anges på samma sätt",
    "Varje artefakt har en **canonical URL**, t.ex. `…/StructureDefinition/EducationPatient`",
], MARGIN, CONTENT_TOP + I(3.15), CONTENT_W, I(2.0), size=17)

s = d.content_slide("Läsa en IG", notes="""
Visa kursens egen IG (deltagarnas GitHub Pages) eller en publicerad IG, t.ex. HL7 Sveriges basprofiler.

Gå igenom flikarna på en profilsida: Text summary, Differential table, Snapshot table, Key elements, Must support,
Statistics, och XML/JSON/TTL.

Visa också Artifacts-sidan och qa.html, där IG Publisher redovisar fel och varningar för hela IG:n.
""")
d.table(s, [
    ["Vy / sida", "Visar"],
    ["**Differential Table**", "Det profilen ändrar jämfört med basen"],
    ["**Snapshot Table**", "Hela strukturen efter ändringarna"],
    ["**Key Elements Table**", "Obligatoriska och Must Support-element plus deras föräldrar"],
    ["**Must Support Table**", "Bara Must Support-element"],
    ["**Artifacts**", "Alla profiler, extensions, terminologi och exempel"],
    ["**qa.html**", "Kvalitetsrapport: fel, varningar och trasiga länkar"],
], MARGIN, CONTENT_TOP, I(8.0), col_widths=[2.6, 5.4], size=16, row_height=I(0.58))
d.callout(s, "**Exempel att bläddra i**\n\n• Din egen kurs-IG (GitHub Pages)\n• HL7 Sverige basprofiler\n  hl7.se/fhir/ig/base\n• International Patient Summary\n  hl7.org/fhir/uv/ips",
          I(8.9), CONTENT_TOP + I(0.1), I(3.8), I(3.3), kind="info", size=15)

s = d.content_slide("Verktyg", notes="""
En snabb översikt över verktyg vi använder i dag (fetstil) och andra som är bra att känna till.

Forge och Simplifier (Firely) är vanliga i Sverige för grafisk profilering och publicering.
FSH och SUSHI är HL7:s textbaserade alternativ och fungerar bra med git och CI. Det är vad vi använder i dag och
vad Ineras mall-repo bygger på.
""")
d.table(s, [
    ["Verktyg", "Användning", "I dag"],
    ["**FSH + SUSHI**", "Skriva profiler, extensions, terminologi och exempel som text", "Modul 3"],
    ["**IG Publisher**", "Bygga IG-webbplats och paket, med kvalitetsrapport", "Modul 3–6"],
    ["**FHIR Validator**", "Validera instanser mot bas, profiler och terminologi", "Modul 6"],
    ["**FHIRPath Lab**", "Testa FHIRPath-uttryck", "Modul 4"],
    ["**HAPI FHIR**", "Java-bibliotek, klient och server", "Modul 5"],
    ["**FHIR Mapping Language**", "Mappa mellan strukturer, t.ex. proprietär JSON → FHIR", "Modul 5"],
    ["Forge / Simplifier", "Grafisk profilering och publicering (Firely)", ""],
    ["Inferno / Touchstone", "Testa API-beteende och konformitet", "Modul 6"],
    ["GitHub Actions", "Automatiskt bygge och validering vid varje incheckning", "Hela dagen"],
], MARGIN, CONTENT_TOP, CONTENT_W, col_widths=[2.6, 7.4, 2.0], size=15, row_height=I(0.48))

d.exercise_slide("2.1 Läs en profil  ·  2.2 Vilken slice?", [
    "**2.1** Öppna profilen i **facit-IG:n**: `https://<konto>.github.io/<repo>/facit/` → Artifacts → EducationPatient",
    (1, "Använd flikarna Differential, Snapshot och Key Elements. Vilken canonical URL och basresurs?"),
    (1, "Vilka element har ändrad kardinalitet? Vilka är Must Support?"),
    (1, "Vilken bindning har ändrats, och är ändringen tillåten?"),
    (1, "Vilka extensions används? Hur är identifier slicad?"),
    "**2.2** Öppna `Patient-identifierare.json` (fyra identifierare)",
    (1, "Vilken slice hamnar varje identifierare i? Är instansen giltig?"),
    (1, "Vad händer med den fjärde? Och om slicingen vore `closed`?"),
    "**2.3** (extra) Bläddra i en publicerad IG och hitta slicing och extensions",
], where="kursmaterial/modul-2-profiler-och-ig/  (frågor i README.md, facit i facit.md)", minutes=15, notes="""
Profilen i övningen är den som deltagarna själva bygger i modul 3 och 4, så de får en förhandstitt.
Den publiceras automatiskt som facit-IG under /facit/ på deltagarnas GitHub Pages. Saknas den: Actions → Bygg IG →
Run workflow. Läs profilen i IG Publishers vyer, så som kravställare möter profiler i verkligheten.
Den som vill kan jämföra med JSON-filen i kursmaterialet.

Facit-IG:n innehåller också invarianter. Spara dem till modul 4 (övning 4.0).

Poängen med 2.2 är den fjärde identifieraren, med felstavat system. Den hamnar utanför alla slices,
och eftersom slicingen är öppen blir instansen ändå giltig. Det leder vidare till diskussionen om
open/closed och om vad validering kan och inte kan fånga (modul 6).
""")

summary_slide([
    "En **profil** begränsar en basresurs. Den är ett maskinläsbart kontrakt",
    "**Differential** = ändringar, och **snapshot** = hela resultatet",
    "**Must Support** definieras av varje IG. Var tydlig!",
    "**Extensions** definieras först och används sedan i profilen. Återanvänd befintliga",
    "**Slicing** delar upp listor, och diskriminatorn avgör tillhörigheten. Slice-namnen syns inte i data",
    "En **IG** paketerar profiler, terminologi, exempel och krav: webbplats + npm-paket",
], "Modul 3\nFHIR Shorthand – vi skriver profilerna själva", notes="""
Nästa modul: vi skriver profilen som vi just tolkade, i FSH, och bygger den i GitHub.
""")

# =====================================================================================
# MODUL 3
# =====================================================================================
d.module_slide(3, "FHIR Shorthand (FSH)", [
    "läsa och skriva FSH",
    "skapa en profil och se den i den byggda IG:n",
    "binda terminologi med include och med referens",
    "lägga till extensions och slicing",
], [(15, "Genomgång"), (30, "Övningar 3.1–3.3 (3.4–3.5 om tid finns)"), (5, "Summering")], notes="""
Det här är den mest praktiska modulen. Räkna med att de flesta hinner 3.1–3.3. Övning 3.4–3.5 är valfria,
och Kom ikapp → modul 3 ger alla samma läge inför modul 4. Håll genomgången kort och låt deltagarna bygga.
Ha lösningen redo att visa, och påminn om "Kom ikapp".
""")

s = d.content_slide("Varför FSH?", notes="""
FHIR Shorthand är ett domänspecifikt språk för att skriva FHIR-artefakter. SUSHI kompilerar FSH till JSON.

Fördelar: kort och läsbart, fungerar med git (diff, pull requests, code review), kan byggas automatiskt i CI.
Det är HL7-standard och används av de flesta nya IG:er, bland annat Ineras mall.
""")
d.code(s, """Profile: EducationPatient
Parent: Patient
Id: EducationPatient
Title: "Education Patient"
Description: "Patientprofil för FHIR-utbildningen."
* identifier 1..* MS
* name 1..* MS
* birthDate 1..1 MS""", MARGIN, CONTENT_TOP + I(0.05), I(5.6), I(2.9), size=15, title="FSH – 8 rader")
d.code(s, """{
  "resourceType": "StructureDefinition",
  "id": "EducationPatient",
  "url": "http://example.org/fhir/.../EducationPatient",
  "name": "EducationPatient",
  "title": "Education Patient",
  "status": "draft",
  "fhirVersion": "4.0.1",
  "kind": "resource",
  "abstract": false,
  "type": "Patient",
  "baseDefinition": "http://hl7.org/fhir/StructureDefinition/Patient",
  "derivation": "constraint",
  "differential": { "element": [
    { "id": "Patient.identifier", "path": "Patient.identifier",
      "min": 1, "mustSupport": true },
    { "id": "Patient.name", "path": "Patient.name", ... """, I(6.6), CONTENT_TOP + I(0.05), I(6.1), I(5.2), lang="json", size=12, title="JSON – ca 40 rader")
d.bullets(s, [
    "**Läsbart** och kompakt",
    "**Git**: diff, pull requests och granskning",
    "**CI**: bygg och validera automatiskt",
    "**HL7-standard** som används av de flesta nya IG:er",
], MARGIN, CONTENT_TOP + I(3.3), I(5.6), I(2.2), size=17)

s = d.content_slide("Byggkedjan i ditt repo", notes="""
Visa repot: test-ig/sushi-config.yaml (metadata för IG:n), input/fsh (FSH-filerna), input/pagecontent (sidor)
och ig.ini (pekar ut IG-resursen och mallen).

SUSHI läser FSH och skriver JSON till fsh-generated/. IG Publisher läser JSON och sidorna och skapar webbplatsen
i output/. I GitHub Actions publiceras output till grenen gh-pages, som GitHub Pages visar.
""")
chain = [("FSH-filer\ninput/fsh/*.fsh", TEAL_LIGHT, DARK), ("SUSHI", NAVY, WHITE), ("FHIR-JSON\nfsh-generated/", TEAL_LIGHT, DARK),
         ("IG Publisher", NAVY, WHITE), ("Webbplats\noutput/", TEAL_LIGHT, DARK), ("GitHub Pages", ORANGE, WHITE)]
w, gap = I(1.78), I(0.3)
for i, (label, fill, color) in enumerate(chain):
    x = MARGIN + i * (w + gap)
    d.box(s, label, x, CONTENT_TOP + I(0.2), w, I(1.1), fill=fill, color=color, size=15, bold=fill != TEAL_LIGHT)
    if i < len(chain) - 1:
        d.arrow(s, x + w + I(0.02), CONTENT_TOP + I(0.75), x + w + gap - I(0.02), CONTENT_TOP + I(0.75))
d.code(s, """test-ig/
├── sushi-config.yaml        # id, canonical, namn, version
├── ig.ini                   # pekar på IG-resursen och mallen
└── input/
    ├── fsh/
    │   ├── aliases.fsh      # korta namn för URL:er
    │   ├── profiles/        # EducationPatient.fsh …
    │   ├── extensions/
    │   ├── terminology/
    │   └── examples/        # patient-tolvan.fsh
    ├── pagecontent/index.md # startsidan
    └── ignoreWarnings.txt""", MARGIN, CONTENT_TOP + I(1.7), I(8.2), I(3.6), lang="text", size=14)
d.callout(s, "Fel i FSH?\n\nSteget **Kör SUSHI** blir rött i Actions. Felet står med **fil och rad** i loggen.\n\nFel i profiler eller exempel?\n\nLäs **qa.html** i den publicerade IG:n.",
          I(9.1), CONTENT_TOP + I(1.7), I(3.6), I(3.6), kind="warn", size=15)

s = d.content_slide("FSH-syntax: entiteter", notes="""
Varje entitet börjar med ett nyckelord och ett namn, följt av metadata (Parent, Id, Title, Description) och
regler som börjar med asterisk.

Id blir en del av den canonical URL:en: [canonical]/StructureDefinition/[Id].
""")
d.table(s, [
    ["Nyckelord", "Skapar", "Används till"],
    ["`Profile:`", "StructureDefinition (constraint)", "Profiler på resurser och datatyper"],
    ["`Extension:`", "StructureDefinition (Extension)", "Egna extensions"],
    ["`ValueSet:`", "ValueSet", "Urval av koder"],
    ["`CodeSystem:`", "CodeSystem", "Egna kodverk"],
    ["`Instance:`", "Valfri resurs", "Exempel, CapabilityStatement m.m."],
    ["`Invariant:`", "constraint i profilen", "FHIRPath-regler (modul 4)"],
    ["`Logical:`", "StructureDefinition (logical)", "Logiska modeller, t.ex. källsystemets struktur (modul 5)"],
    ["`Alias:`", "–", "Korta namn för långa URL:er, t.ex. `$personnummer`"],
    ["`RuleSet:`", "–", "Återanvändbara regler"],
], MARGIN, CONTENT_TOP, I(8.2), col_widths=[1.8, 3.0, 3.4], size=14, row_height=I(0.48))
d.code(s, """Profile: EducationPatient
Parent: Patient
Id: EducationPatient
Title: "Education Patient"
Description: "..."
* ^status = #draft
* name 1..* MS""", I(9.0), CONTENT_TOP + I(0.05), I(3.7), I(2.7), size=13)
d.text(s, "Id → canonical URL:\n…/StructureDefinition/**EducationPatient**", I(9.0), CONTENT_TOP + I(2.95), I(3.7), I(1.0), size=14, color=GREY)

s = d.content_slide("FSH-syntax: regler", notes="""
Gå igenom de vanligaste reglerna. Caret (^) sätter värden på själva StructureDefinition eller ElementDefinition
i stället för på instansdata, t.ex. ^short, ^slicing och ^status.

Regler för instanser (Instance) använder samma syntax: * name.family = "Tolvansson".
""")
d.table(s, [
    ["Regel", "Exempel"],
    ["Kardinalitet", "`* name 1..*`"],
    ["Flaggor", "`* birthDate MS`   `* gender 1..1 MS`"],
    ["Bindning", "`* type from KontakttypVS (extensible)`"],
    ["Tilldelning", "`* identifier.system = $personnummer`   `* status = #finished`"],
    ["Typbegränsning", "`* subject only Reference(EducationPatient)`   `* value[x] only boolean`"],
    ["Contains", "`* extension contains SkyddadIdentitet named skyddadIdentitet 0..1`"],
    ["Invariant", "`* obeys edu-pat-1`"],
    ["Caret (metadata)", "`* ^status = #draft`   `* identifier ^short = \"Identifierare\"`"],
    ["Kod och referens", "`$v3-ActCode#AMB \"ambulatory\"`   `Reference(patient-tolvan)`"],
], MARGIN, CONTENT_TOP, CONTENT_W, col_widths=[2.4, 9.6], size=16, row_height=I(0.5))

s = d.content_slide("Startprofilen i ditt repo", notes="""
Öppna filerna tillsammans i GitHub. Visa sedan resultatet i den publicerade IG:n: profilsidan och exemplet.

Påpeka att meta.profile inte står i exemplet: SUSHI lägger till det automatiskt utifrån InstanceOf.
""")
d.code(s, """Profile: EducationPatient
Parent: Patient
Id: EducationPatient
Title: "Education Patient"
Description: "Patientprofil för FHIR-utbildningen."
* ^status = #draft
* identifier 1..* MS
* identifier.system 1..1
* identifier.value 1..1
* name 1..* MS
* name.family 1..1 MS
* name.given MS
* gender MS
* birthDate 1..1 MS""", MARGIN, CONTENT_TOP + I(0.05), I(6.0), I(5.2), size=14, title="input/fsh/profiles/EducationPatient.fsh")
d.code(s, """Instance: patient-tolvan
InstanceOf: EducationPatient
Title: "Tolvan Tolvansson"
Usage: #example
* identifier[0].system = $personnummer
* identifier[0].value = "191212121212"
* name[0].use = #official
* name[0].family = "Tolvansson"
* name[0].given[0] = "Tolvan"
* gender = #male
* birthDate = "1912-12-12\"""", I(6.9), CONTENT_TOP + I(0.05), I(5.8), I(4.2), size=14, title="input/fsh/examples/patient-tolvan.fsh")
d.text(s, "SUSHI sätter `meta.profile` automatiskt utifrån `InstanceOf`.", I(6.9), CONTENT_TOP + I(4.45), I(5.8), I(0.6), size=15, color=GREY)

s = d.content_slide("Ny profil: EducationEncounter", notes="""
Övning 3.2. Visa strukturen, låt deltagarna skriva själva. Notera:
- subject only Reference(EducationPatient) begränsar målet för referensen till vår profil.
- serviceProvider med logisk referens (HSA-id).
- Exemplet refererar till patient-tolvan med Reference(patient-tolvan). SUSHI löser upp det till Patient/patient-tolvan.
- Exemplet måste innehålla alla element som profilen kräver (1..1), annars fel i qa.html.
- type anges som fritext (type.text) tills kodsystemet Kontakttyp finns. I övning 3.3 byts den mot en kod.
""")
d.code(s, """Profile: EducationEncounter
Parent: Encounter
Id: EducationEncounter
Title: "Education Encounter"
Description: "Profil för en vårdkontakt."
* status MS
* class MS
* type 1..1 MS
* subject 1..1 MS
* subject only Reference(EducationPatient)
* period 1..1 MS
* period.start 1..1 MS
* reasonCode MS
* serviceProvider 1..1 MS
* serviceProvider.identifier 1..1 MS
* serviceProvider.identifier.system = $hsaid""", MARGIN, CONTENT_TOP + I(0.05), I(5.5), I(5.2), size=14, title="input/fsh/profiles/EducationEncounter.fsh")
d.code(s, """Instance: encounter-tolvan-1
InstanceOf: EducationEncounter
Usage: #example
* status = #finished
* class = $v3-ActCode#AMB "ambulatory"
* type.text = "Besök"   // kod i övning 3.3
* subject = Reference(patient-tolvan)
* period.start = "2026-10-01T09:00:00+02:00"
* period.end = "2026-10-01T09:30:00+02:00"
* reasonCode = $ICD10#J45.9 "Asthma, unspecified"
* serviceProvider.identifier.system = $hsaid
* serviceProvider.identifier.value = "SE2321000016-KURS"
* serviceProvider.display = "Vårdcentralen Kursköping\"""", I(6.3), CONTENT_TOP + I(0.05), I(6.4), I(5.2), size=14, title="input/fsh/examples/encounter-tolvan-1.fsh")

s = d.content_slide("Terminologi i FSH: include och referens", notes="""
Tre sätt att få en bindning på plats:
1. Eget kodsystem + ValueSet som inkluderar hela kodsystemet (include codes from system).
2. ValueSet som räknar upp enskilda koder ur ett befintligt kodsystem (include $system#kod).
3. Bindning genom referens till ett befintligt, publicerat ValueSet (canonical URL).

Diskutera förvaltning: ett eget ValueSet måste ni förvalta själva. En referens till ett nationellt ValueSet ger
automatiskt uppdateringar, men också beroenden. Man kan också inkludera ett annat ValueSet (include codes from
valueset) eller filtrera, t.ex. SNOMED CT is-a.

Kontakttyp är ett fiktivt kodverk för kursen. I verkligheten används nationella kodverk.
""")
d.code(s, """CodeSystem: KontakttypCS
Id: kontakttyp
* #besok "Besök"
* #hembesok "Hembesök"
* #video "Videokontakt"
* #telefon "Telefonkontakt"

ValueSet: KontakttypVS
Id: kontakttyp-vs
* include codes from system KontakttypCS""", MARGIN, CONTENT_TOP + I(0.05), I(5.9), I(3.2), size=14, title="a) Eget kodsystem – ValueSet med hela kodsystemet")
d.code(s, """ValueSet: EducationEncounterClassVS
Id: education-encounter-class
* include $v3-ActCode#AMB "ambulatory"
* include $v3-ActCode#IMP "inpatient encounter"
* include $v3-ActCode#EMER "emergency"
* include $v3-ActCode#HH "home health"
* include $v3-ActCode#VR "virtual\"""", I(6.8), CONTENT_TOP + I(0.05), I(5.9), I(3.2), size=14, title="a) Befintligt kodsystem – enskilda koder med include")
d.code(s, """// Bindningar i profilerna
* class from EducationEncounterClassVS (required)
* type from KontakttypVS (extensible)
* maritalStatus from http://hl7.org/fhir/ValueSet/marital-status (required)  // b)
// ... och i exemplet: * type = KontakttypCS#besok "Besök"

// Fler varianter i ett ValueSet
* include codes from valueset http://...
* include codes from system $SCT where concept is-a #308335008""", MARGIN, CONTENT_TOP + I(3.5), CONTENT_W, I(1.95), size=14, title="b) Bindning med referens – och andra varianter")

s = d.content_slide("Extensions och slicing i FSH", notes="""
Övning 3.4 och 3.5. Visa att extension-slicing (contains) och identifier-slicing har samma syntax:
contains + namn + kardinalitet. Skillnaden är att för extensions sköter FHIR själv diskriminatorn (url), medan vi
för identifier måste ange diskriminatorn med ^slicing.

I exemplet: identifier[personnummer].value = "...". Systemet fylls i automatiskt från profilens mönster.
Titta sedan i JSON-fliken: slice-namnet syns inte.

Diskussionsfråga om SkyddadIdentitet: HL7 Sveriges SEBasePatient uttrycker sekretessmarkering och skyddad
folkbokföring med meta.security (kodsystemet http://hl7.se/fhir/ig/base/CodeSystem/SecurityLabel), inte med en
extension. Vår extension är en övning i att skapa extensions, men i verkligheten återanvänder man den nationella lösningen.
""")
d.code(s, """Extension: SkyddadIdentitet
Id: SkyddadIdentitet
Title: "Skyddad identitet"
Context: Patient
* value[x] 1..1
* value[x] only boolean

// I EducationPatient:
* extension contains
    $patient-interpreterRequired named tolkbehov 0..1 MS and
    SkyddadIdentitet named skyddadIdentitet 0..1 MS

// I exemplet:
* extension[tolkbehov].valueBoolean = false""", MARGIN, CONTENT_TOP + I(0.05), I(6.0), I(5.2), size=13, title="Extensions (övning 3.4)")
d.code(s, """* identifier ^slicing.discriminator.type = #value
* identifier ^slicing.discriminator.path = "system"
* identifier ^slicing.rules = #open
* identifier contains
    personnummer 0..1 MS and
    samordningsnummer 0..1 MS
* identifier[personnummer].system = $personnummer
* identifier[samordningsnummer].system =
    $samordningsnummer

// I exemplet:
* identifier[personnummer].value = "191212121212\"""", I(6.9), CONTENT_TOP + I(0.05), I(5.8), I(5.2), size=13, title="Slicing (övning 3.5)")

s = d.content_slide("I verkligheten: bygg på HL7 Sveriges basprofiler", notes="""
Övning 3.6 (extra). I verkligheten profilerar man sällan direkt på basresursen. HL7 Sveriges SEBasePatient har
redan slicing för personnummer, samordningsnummer och nationellt reservnummer, med samma diskriminator som vi
byggde själva. Den har svenska namnregler (högst ett namn, mellannamn) och säkerhetsmärkning via meta.security.

Beroendet anges i sushi-config.yaml med paket-id och version. Det är samma princip som vid kravställning:
peka ut exakt vilken version man bygger på.

Diskutera: vad ärver man "på köpet"? Varför kan EducationSEPatient inte ha name 1..* (basprofilen säger 0..1)?
""")
d.code(s, """# test-ig/sushi-config.yaml
dependencies:
  hl7se.fhir.base: 1.1.0""", MARGIN, CONTENT_TOP + I(0.05), I(5.4), I(1.45), lang="text", size=15, title="1. Beroende till HL7 Sveriges paket")
d.code(s, """Alias: $SecLabel = http://hl7.se/fhir/ig/base/CodeSystem/SecurityLabel

Profile: EducationSEPatient
Parent: SEBasePatient            // från hl7se.fhir.base
Id: EducationSEPatient
* identifier 1..* MS
* identifier[personnummer] MS    // slicen ärvs!
* name 1..1 MS                   // basprofilen: 0..1
* birthDate 1..1 MS

Instance: patient-tolvan-se
InstanceOf: EducationSEPatient
* meta.security = $SecLabel#sekretessmarkering
* identifier[personnummer].value = "191212121212"
...""", I(6.2), CONTENT_TOP + I(0.05), I(6.5), I(5.2), size=14, title="2. Profil och exempel på SEBasePatient")
d.bullets(s, [
    "**Slicing** för personnummer, samordningsnummer och reservnummer finns redan",
    "**Svenska namnregler** och adresstyper",
    "**Skyddad identitet** via `meta.security`, inte en egen extension",
    "Peka ut **exakt version** av beroendet, som vid kravställning",
], MARGIN, CONTENT_TOP + I(1.85), I(5.4), I(3.2), size=16)

d.exercise_slide("FSH: bygg ut kursens IG", [
    "**3.1** Titta på startprofilen och jämför Differential och Snapshot i din IG  (5 min)",
    "**3.2** Skapa `profiles/EducationEncounter.fsh` + exemplet `encounter-tolvan-1`  (10 min)",
    "**3.3** Terminologi: `Kontakttyp.fsh` (CodeSystem + ValueSet med include), class-ValueSet, och bind `maritalStatus` via referens  (10 min)",
    "**3.4** (om tid finns) Extensions: `patient-interpreterRequired` och egen `SkyddadIdentitet`",
    "**3.5** (om tid finns) Slicing av `identifier`: personnummer och samordningsnummer",
    "**3.6** (extra) Bygg på HL7 Sveriges `SEBasePatient`, med beroende till `hl7se.fhir.base`",
    "Efter varje steg: **Commit** → steget **Kör SUSHI** är klart efter ~30 s → titta sedan i din IG",
    "Hamnat efter? **Actions → Kom ikapp** → `3.2` eller `3`",
], where="test-ig/input/fsh/  ·  instruktioner: kursmaterial/modul-3-fsh/README.md  ·  lösning: kursmaterial/losningar/modul-3/", minutes=30, notes="""
Hela bygget tar cirka 2 minuter, men SUSHI-steget är klart efter ungefär 30 sekunder. Lär deltagarna att titta
där först. Uppmuntra flera ändringar per incheckning, eller github.dev (tryck .) för att ändra flera filer samtidigt.

3.4–3.5 är valfria under kurstiden. 3.6 är en extrauppgift (eller hemuppgift) för den som är klar.

Vanliga fel:
- Indrag och citattecken i FSH
- Glömt alias ($personnummer) eller skrivit fel namn på ValueSet
- Profilen refererar till ett ValueSet som inte finns ännu

Visa en lösning på storskärm efter 20 minuter.
""")

summary_slide([
    "**FSH** är ett kompakt textformat för FHIR-artefakter, och **SUSHI** kompilerar till JSON",
    "Byggkedjan: FSH → SUSHI → IG Publisher → GitHub Pages, automatiskt vid varje incheckning",
    "Terminologi: eget ValueSet med **include**, eller **referens** till ett befintligt",
    "Extensions och slicing använder samma `contains`-syntax",
    "Slice-namn används i FSH-exemplen men syns inte i JSON",
], "Lunch!\n\nSedan modul 4\nFHIRPath och invarianter", notes="""
Påminn om Kom ikapp innan lunch, så att alla börjar modul 4 från samma läge.
""")

# =====================================================================================
# MODUL 4
# =====================================================================================
d.module_slide(4, "FHIRPath och invarianter", [
    "skriva FHIRPath-uttryck för att navigera och filtrera",
    "läsa invarianter i FHIR-specifikationen",
    "lägga till en egen invariant i en profil",
    "se invarianten slå till vid validering",
], [(20, "Genomgång"), (25, "Övningar 4.1–4.3"), (5, "Summering")], notes="""
Efter lunch: kom igång med något konkret. Visa FHIRPath Lab direkt och låt alla prova ett uttryck på Tolvan.
""")

s = d.content_slide("Vad är FHIRPath?", notes="""
FHIRPath är ett uttrycksspråk för att navigera och välja ut data i FHIR-resurser, ungefär som XPath för XML.

Det används på många ställen i FHIR: invarianter (constraints), sökparametrar (SearchParameter.expression),
slicing-diskriminatorer (path), mappningar, CQL, SQL on FHIR (ViewDefinition) och i verktyg som validatorn.

Grundprincipen: allt är samlingar (collections). Ett uttryck som inte hittar något ger en tom samling, inte ett fel.
""")
d.bullets(s, [
    "Ett **uttrycksspråk** för att navigera i och välja ut data ur FHIR-resurser (jfr XPath)",
    "Används i FHIR för:",
    (1, "**invarianter** (constraints) i resurser och profiler"),
    (1, "**sökparametrar**, t.ex. `Patient.name.family`"),
    (1, "**slicing**-diskriminatorer, mappningar, SQL on FHIR, CQL"),
    "Allt är **samlingar**: ett uttryck kan ge noll, ett eller flera värden",
    "Hittar uttrycket inget blir resultatet **tomt**, inte fel",
], MARGIN, CONTENT_TOP, I(7.3), I(5.2), size=19)
d.code(s, """Patient.name.given
→ ["Tolvan", "Bertil", "Tolle"]

name.where(use = 'official').family
→ ["Tolvansson"]

telecom.where(system = 'email')
→ [ ]   (tom samling)

birthDate < @1950-01-01
→ [true]""", I(8.1), CONTENT_TOP + I(0.1), I(4.6), I(4.6), lang="text", size=15)

s = d.content_slide("Grundsyntax", notes="""
Gå igenom tabellen. Viktigt att förstå:
- where filtrerar, exists/empty testar, all testar alla element.
- implies: "om A så B". Om A är falskt är hela uttrycket sant.
- Strängar med enkla citattecken, datum med @.
- extension('url') är en genväg för extension.where(url = '...').
""")
d.table(s, [
    ["Uttryck", "Betydelse"],
    ["`name.given`", "Navigera: alla förnamn i alla namn"],
    ["`name.where(use = 'official')`", "Filtrera en samling"],
    ["`identifier.exists()`   `telecom.empty()`", "Finns det något? / Är det tomt?"],
    ["`identifier.count() = 1`", "Antal element"],
    ["`telecom.all(system.exists())`", "Gäller villkoret för alla element?"],
    ["`status = 'finished' implies period.end.exists()`", "Om A så B"],
    ["`value.matches('^[0-9]{12}$')`", "Reguljärt uttryck"],
    ["`birthDate <= today()`", "Datumjämförelse (`@1912-12-12` är ett datumvärde)"],
    ["`extension('http://…/patient-interpreterRequired').value`", "Värdet i en viss extension"],
    ["`and`  `or`  `not()`  `|`", "Logik och union av samlingar"],
], MARGIN, CONTENT_TOP, CONTENT_W, col_widths=[6.2, 5.8], size=15, row_height=I(0.47))

s = d.content_slide("Invarianter i specifikationen", notes="""
Visa fliken Constraints på https://hl7.org/fhir/R4/patient.html.

pat-1 gäller Patient.contact: en kontaktperson måste ha minst något av namn, telecom, adress eller organisation.
ele-1 och ext-1 finns på alla element och extensions. dom-6 är en best practice-varning som ni kommer att se
ofta i valideringen.

Varje invariant har nyckel, allvarlighetsgrad (error/warning), en mänsklig beskrivning och ett FHIRPath-uttryck.
""")
d.table(s, [
    ["Nyckel", "Nivå", "Beskrivning", "Uttryck"],
    ["`pat-1`", "error", "En kontaktperson ska ha namn, telecom, adress eller organisation", "`name.exists() or telecom.exists() or address.exists() or organization.exists()`"],
    ["`ele-1`", "error", "Alla element ska ha ett värde eller barn", "`hasValue() or (children().count() > id.count())`"],
    ["`ext-1`", "error", "En extension har antingen värde eller nästlade extensions", "`extension.exists() != value.exists()`"],
    ["`dom-6`", "warning", "En resurs bör ha en narrativ (best practice)", "text.`div`.exists()"],
], MARGIN, CONTENT_TOP, CONTENT_W, col_widths=[1.1, 1.1, 4.0, 5.8], size=14, row_height=I(0.85))
d.callout(s, "Ett invariant-uttryck ska ge **true** för att instansen ska vara giltig. Varje invariant har en **nyckel**, en **nivå** (error/warning), en **beskrivning** och ett **uttryck**.",
          MARGIN, I(5.85), CONTENT_W, I(0.85), kind="info", size=16)

s = d.content_slide("Egna invarianter i FSH", notes="""
Det här är övning 4.2. Invarianten definieras en gång och kopplas sedan till profilen med obeys.

Man kan koppla den till hela resursen (* obeys ...) eller till ett element (* identifier obeys ...). Kontexten avgör
vad uttrycket utgår från.

Lägg märke till att edu-pat-1 använder all(): finns det inget personnummer är resultatet sant. Det är kardinaliteten
som avgör OM ett personnummer krävs, och invarianten som avgör HUR det ser ut.
""")
d.code(s, """Invariant: edu-pat-1
Description: "Ett personnummer ska bestå av exakt 12 siffror."
Expression: "identifier
  .where(system = 'http://electronichealth.se/identifier/personnummer')
  .all(value.matches('^[0-9]{12}$'))"
Severity: #error

Invariant: edu-enc-1
Description: "En avslutad vårdkontakt ska ha en sluttid."
Expression: "status = 'finished' implies period.end.exists()"
Severity: #error""", MARGIN, CONTENT_TOP + I(0.05), I(8.3), I(3.6), size=13, title="input/fsh/invariants.fsh")
d.code(s, """// i EducationPatient
* obeys edu-pat-1

// i EducationEncounter
* obeys edu-enc-1""", I(9.15), CONTENT_TOP + I(0.05), I(3.55), I(2.3), size=14, title="Koppla till profilen")
d.callout(s, "**Testa!** Ändra personnumret i exemplet till `19121212-1212` och bygg. Felet syns i **qa.html**:\n`Constraint failed: edu-pat-1: 'Ett personnummer ska bestå av exakt 12 siffror'`",
          MARGIN, CONTENT_TOP + I(3.95), CONTENT_W, I(1.1), kind="warn", size=16)

s = d.content_slide("Fallgropar", notes="""
De vanligaste missförstånden:
- Tom samling: all() på en tom samling är sant, exists() är falskt. En jämförelse med en tom samling ger tomt
  (inte false), och en invariant som ger tomt räknas normalt som uppfylld.
- Strängar jämförs exakt (skiftlägeskänsligt). Koder jämförs som strängar.
- matches: förankra alltid med ^ och $.
- Datum med olika precision (1912 jämfört med 1912-12-12) kan ge tomt resultat.
- Flera värden: name.family = 'X' när det finns två namn ger ett oväntat resultat. Använd where/exists.
""")
d.table(s, [
    ["Fallgrop", "Exempel", "Tips"],
    ["Tomma samlingar", "`{}.all(…)` är **true**, men `{}.exists()` är **false**", "Kombinera med kardinalitet eller `exists()`"],
    ["Jämförelse med tomt", "`period.end > period.start` ger tomt om end saknas", "Skriv `period.end.empty() or …`"],
    ["Flera värden", "`name.family = 'X'` när det finns flera namn", "Använd `where(…)` och `exists()`"],
    ["Reguljära uttryck", "`matches('[0-9]{12}')` matchar även 13 siffror", "Förankra med `^…$`"],
    ["Datumprecision", "`@1912` jämfört med `@1912-12-12` blir tomt", "Var medveten om precisionen"],
    ["Sträng eller kod", "`gender = 'Male'` är **false**", "Skiftlägeskänsligt"],
], MARGIN, CONTENT_TOP, CONTENT_W, col_widths=[2.3, 5.4, 4.3], size=15, row_height=I(0.65))

d.exercise_slide("FHIRPath och invarianter", [
    "**4.0** Läs invarianterna `edu-pat-1` och `edu-pat-2` i **facit-IG:n** (EducationPatient). Vad kontrollerar de?  (3 min)",
    "**4.1** Öppna **fhirpath-lab.com**, klistra in `Patient-tolvan.json` (modul 1) och testa uttrycken i README  (7 min)",
    (1, "Skriv ett eget uttryck som är sant om patienten har ett personnummer med exakt 12 siffror"),
    "**4.2** Skapa `test-ig/input/fsh/invariants.fsh` med `edu-pat-1` och `edu-enc-1`, och koppla dem med `obeys`  (10 min)",
    (1, "Bygg, och kontrollera fliken Constraints på profilsidan"),
    (1, "Ändra personnumret i exemplet så att det blir fel, och läs felet i **qa.html**. Ändra sedan tillbaka"),
    "**4.3** (extra) Skriv själv `edu-pat-2` (födelsedatum ej i framtiden) och `edu-enc-2` (slut efter start, varning)",
    "Hamnat efter? **Actions → Kom ikapp → modul 3** innan du börjar (eller **modul 4** för lösningen)",
], where="kursmaterial/modul-4-fhirpath/README.md  ·  facit: facit.md  ·  lösning: kursmaterial/losningar/modul-4/", minutes=25, notes="""
4.1 kan göras utan att bygga något, så det är bra medan bygget från 4.2 kör.

Diskutera efteråt: vad ska stå i en invariant, och vad passar bättre i bindning, kardinalitet eller mottagarens
verksamhetslogik? Invarianter är bra för strukturella regler, men tunga affärsregler hör sällan hemma i profilen.
""")

summary_slide([
    "**FHIRPath** navigerar, filtrerar och testar data. Allt är samlingar",
    "**Invarianter** = nyckel + nivå + beskrivning + FHIRPath-uttryck",
    "I FSH: `Invariant:` definieras och kopplas med `obeys`",
    "Se upp med **tomma samlingar**, flera värden och oförankrade reguljära uttryck",
    "Kardinaliteten styr **om** något krävs, och invarianten **hur** det ser ut",
], "Modul 5\nUtveckling med HAPI FHIR och API-säkerhet", notes="""
Nu lämnar vi IG:n en stund och tittar på hur man faktiskt erbjuder ett FHIR-API som följer profilerna.
""")

# =====================================================================================
# MODUL 5
# =====================================================================================
d.module_slide(5, "Utveckling med HAPI FHIR", [
    "beskriva FHIR:s REST-API: interaktioner och sökning",
    "förstå hur en FHIR-fasad ovanpå ett befintligt system byggs med HAPI",
    "läsa och ändra en mappning i FHIR Mapping Language (FML)",
    "känna till grunderna i API-säkerhet: OAuth 2.0 och SMART on FHIR",
    "känna till relevanta IHE-profiler för integration",
], [(25, "Genomgång och demo"), (20, "Övningar 5.1–5.3"), (5, "Summering")], notes="""
Modulen har en blandad publik: utvecklare vill se kod, kravställare vill förstå arkitekturval och säkerhet.
FML passar båda: mappningen är läsbar som en specifikation, inte bara som kod.

Tidsplan: REST och sökning går fort (deltagarna provar själva i 5.1). Lägg tiden på fasaden, FML och
mappningsutmaningarna, och ta säkerhet och IHE i högt tempo.
""")

s = d.content_slide("FHIR:s REST-API", notes="""
FHIR definierar ett REST-API med ett fåtal interaktioner på typ- och instansnivå.

Alla servrar behöver inte stödja allt. Vad en server stöder beskrivs i dess CapabilityStatement (modul 6).

Visa gärna live mot den publika HAPI-servern: https://hapi.fhir.org/baseR4/Patient?_count=1
""")
d.table(s, [
    ["Interaktion", "HTTP", "Exempel"],
    ["read", "GET", "`[bas]/Patient/191212121212`"],
    ["vread", "GET", "`[bas]/Patient/123/_history/2`"],
    ["search", "GET/POST", "`[bas]/Encounter?patient=191212121212&date=ge2026-10-01`"],
    ["create", "POST", "`[bas]/Patient`"],
    ["update / patch", "PUT / PATCH", "`[bas]/Patient/123`"],
    ["delete", "DELETE", "`[bas]/Patient/123`"],
    ["history", "GET", "`[bas]/Patient/123/_history`"],
    ["capabilities", "GET", "`[bas]/metadata`"],
    ["transaction / batch", "POST", "`[bas]` med en Bundle"],
    ["operation", "GET/POST", "`[bas]/Patient/$validate`,  `[bas]/Patient/123/$everything`"],
], MARGIN, CONTENT_TOP, CONTENT_W, col_widths=[2.6, 1.8, 7.6], size=15, row_height=I(0.47))

s = d.content_slide("Sökning", notes="""
Sökning är det som oftast skiljer en enkel från en användbar implementation.

Sökparametrar är definierade per resurstyp (SearchParameter). Typerna avgör syntaxen: token (system|kod),
reference, date (med prefix som ge/le), string, quantity.

Resultatet är en Bundle av typen searchset med total, länkar för paginering och entry.search.mode (match/include).
""")
d.code(s, """GET [bas]/Patient?identifier=http://electronichealth.se/identifier/personnummer|191212121212
GET [bas]/Encounter?patient=191212121212&date=ge2026-10-01&_sort=-date
GET [bas]/Encounter?patient=191212121212&_include=Encounter:subject
GET [bas]/Patient?family=Tolvansson&_count=10&_summary=true
GET [bas]/Patient?_has:Encounter:patient:status=in-progress""", MARGIN, CONTENT_TOP + I(0.05), CONTENT_W, I(2.1), lang="http", size=15)
d.table(s, [
    ["Typ", "Exempel"],
    ["token", "`identifier=system|värde`,  `gender=male`"],
    ["reference", "`patient=191212121212`,  `subject=Patient/123`"],
    ["date", "`date=ge2026-10-01`  (eq, ne, lt, le, gt, ge …)"],
    ["string", "`family=Tolv`,  `name:exact=Tolvan`"],
], MARGIN, CONTENT_TOP + I(2.45), I(6.4), col_widths=[1.4, 5], size=15, row_height=I(0.5))
d.table(s, [
    ["Resultatparameter", "Gör"],
    ["`_count`", "Antal per sida"],
    ["`_include` / `_revinclude`", "Ta med refererade resurser"],
    ["`_summary` / `_elements`", "Begränsa innehållet"],
    ["`_sort`", "Sortering"],
], I(7.2), CONTENT_TOP + I(2.45), I(5.5), col_widths=[2.6, 2.9], size=15, row_height=I(0.5))

s = d.content_slide("Tre sätt att erbjuda ett FHIR-API", notes="""
1. FHIR-server med egen lagring: HAPI JPA Server (öppen källkod), Firely Server, Smile, molntjänster
   (Azure Health Data Services, Google Healthcare API, AWS HealthLake). Data kopieras in som FHIR.
2. FHIR-fasad: API:t översätter i realtid till ett befintligt system. Ingen dubbellagring, men allt måste
   implementeras och mappas.
3. Integrationsplattform: en integrationsmotor (t.ex. Mirth, Camel, Biztalk eller regionens tjänsteplattform)
   transformerar meddelanden till och från FHIR.

Valet beror på krav på aktualitet, prestanda, skrivning, sökning och var "sanningen" finns.
""")
cols = [
    ("FHIR-server med lagring", "HAPI JPA Server, Firely,\nmolntjänster", ["Full sökning och CRUD", "Versionshistorik", "Data måste synkas/kopieras"], TEAL_LIGHT),
    ("FHIR-fasad", "HAPI Plain Server +\nFML eller egen kod", ["Data stannar i källsystemet", "Alltid aktuellt", "Bara det du implementerar"], ORANGE_LIGHT),
    ("Integrationsplattform", "Integrationsmotor,\ntjänsteplattform", ["Återanvänder befintlig integration", "Transformering av meddelanden", "Ofta asynkront"], LIGHT),
]
for i, (head, tech, points, fill) in enumerate(cols):
    x = MARGIN + i * I(4.1)
    d.box(s, f"**{head}**\n{tech}", x, CONTENT_TOP + I(0.1), I(3.9), I(1.3), fill=fill, size=16)
    d.bullets(s, points, x, CONTENT_TOP + I(1.6), I(3.9), I(2.0), size=16)
d.callout(s, "Kursens exempel `hapi-fasad/` är en **fasad**: ett FHIR-API ovanpå ett journalsystems proprietära REST-API, med mappningar i **FHIR Mapping Language**.",
          MARGIN, CONTENT_TOP + I(3.9), CONTENT_W, I(0.85), kind="info", size=16)

s = d.content_slide("Kursens FHIR-fasad", notes="""
Flödet: klienten anropar GET /fhir/Patient/191212121212. HAPI:s RestfulServer anropar PatientProvider.read().
Den hämtar JSON från journalsystemets eget REST-API (/journalsystem-api/patienter/191212121212), och FmlMotor
kör mappningen fml/patient.map som gör om JSON till en FHIR Patient med meta.profile = EducationPatient.

Visa gärna båda URL:erna sida vid sida i webbläsaren (eller sammanfattningen i arbetsflödet HAPI-fasad).

Poängen: Java-koden är generell. Hur fälten översätts står i FML-filen, som kan läsas och ändras utan att
röra koden. Resursens id sätts dock av fasaden, eftersom det är serverns ansvar.
""")
d.box(s, "**Klient**\napp, annat system", MARGIN, CONTENT_TOP + I(0.2), I(2.1), I(1.3), fill=LIGHT, size=15)
d.box(s, "**FHIR-fasad (HAPI)**\nPatientProvider · EncounterProvider\nFmlMotor: patient.map, besok.map\nCapabilityStatement (auto)",
      I(3.55), CONTENT_TOP + I(0.05), I(4.6), I(1.6), fill=NAVY, color=WHITE, size=14)
d.box(s, "**Journalsystemets REST-API**\nproprietär JSON\negna koder: M/K, AVSL, BES", I(9.3), CONTENT_TOP + I(0.2), I(3.4), I(1.3), fill=ORANGE_LIGHT, size=14)
d.arrow(s, I(2.75), CONTENT_TOP + I(0.85), I(3.5), CONTENT_TOP + I(0.85))
d.arrow(s, I(8.2), CONTENT_TOP + I(0.85), I(9.25), CONTENT_TOP + I(0.85))
d.text(s, "FHIR", I(2.65), CONTENT_TOP + I(0.45), I(1.0), I(0.35), size=12, color=GREY, align=PP_ALIGN.CENTER)
d.text(s, "JSON", I(8.2), CONTENT_TOP + I(0.45), I(1.0), I(0.35), size=12, color=GREY, align=PP_ALIGN.CENTER)
d.code(s, """GET /journalsystem-api/
    patienter/191212121212

{
  "personnummer": "191212121212",
  "fornamn": "Tolvan",
  "efternamn": "Tolvansson",
  "kon": "M",
  "fodelsedatum": "1912-12-12",
  "telefon": "070-1234567"
}""", MARGIN, CONTENT_TOP + I(1.95), I(5.0), I(3.35), lang="json", size=13, title="Källa: journalsystemets API")
d.text(s, "FML\n→", I(5.7), CONTENT_TOP + I(3.2), I(0.9), I(0.8), size=18, bold=True, color=ORANGE, align=PP_ALIGN.CENTER)
d.code(s, """GET /fhir/Patient/191212121212

{ "resourceType": "Patient", "id": "191212121212",
  "meta": { "profile": [ ".../EducationPatient" ] },
  "identifier": [ { "system": ".../personnummer",
                    "value": "191212121212" } ],
  "name": [ { "use": "official", "family": "Tolvansson",
              "given": [ "Tolvan" ] } ],
  "gender": "male",
  "birthDate": "1912-12-12" }""", I(6.7), CONTENT_TOP + I(1.95), I(6.0), I(3.35), lang="json", size=13, title="Resultat: FHIR (telefon saknas – övning 5.2)")

s = d.content_slide("FHIR Mapping Language (FML)", notes="""
FML är HL7:s standardspråk för att beskriva hur en struktur översätts till en annan. En mappning kompileras till
resursen StructureMap och körs av en FML-motor: HL7:s referensbibliotek (som fasaden använder), HAPI eller Matchbox.

Gå igenom delarna:
- conceptmap: kodöversättning, här journalsystemets M/K till FHIR:s male/female.
- uses: källans och målets struktur. Källan är inte FHIR, den beskrivs av en logisk modell (FSH: Logical:).
- group och regler: källa -> mål "namn". Finns inte källelementet körs regeln inte, så inga tomma element skapas.
- then { }: inre regler som fyller ett element som skapats i yttre regeln.

Varför FML i stället för Java? Mappningen blir en läsbar och granskningsbar specifikation som informatiker
kan förstå, och den kan publiceras i en IG. Nackdel: ett eget språk, och stödet varierar mellan FHIR-versioner.
""")
d.code(s, """conceptmap "kon" {
  prefix s = "http://example.org/.../journalsystem/kon"
  prefix t = "http://hl7.org/fhir/administrative-gender"
  s:M == t:male
  s:K == t:female
}

uses ".../StructureDefinition/JournalPatient" alias JournalPatient as source
uses "http://hl7.org/fhir/StructureDefinition/Patient" alias Patient as target

group JournalPatientTillFhir(source src : JournalPatient, target tgt : Patient) {
  src.personnummer as pnr -> tgt.identifier as ident,
      ident.system = 'http://electronichealth.se/identifier/personnummer',
      ident.value = pnr "personnummer";
  src -> tgt.name as namn, namn.use = 'official' then {
    src.efternamn as efternamn -> namn.family = efternamn "efternamn";
    src.fornamn as fornamn -> namn.given = fornamn "fornamn";
  } "namn";
  src.kon as kon -> tgt.gender = translate(kon, '#kon', 'code') "kon";
  src.fodelsedatum as fd -> tgt.birthDate = fd "fodelsedatum";
}""", MARGIN, CONTENT_TOP + I(0.05), I(8.3), I(5.25), size=12, title="hapi-fasad/src/main/resources/fml/patient.map (förkortad)")
d.box(s, "**conceptmap**\nkodöversättning M/K → male/female", I(9.15), CONTENT_TOP + I(0.4), I(3.55), I(0.95), size=14, fill=ORANGE_LIGHT)
d.box(s, "**uses**\nkällans logiska modell och målets resurs", I(9.15), CONTENT_TOP + I(1.5), I(3.55), I(0.95), size=14)
d.box(s, "**regel**\nkälla -> mål \"namn\";", I(9.15), CONTENT_TOP + I(2.6), I(3.55), I(0.95), size=14, fill=NAVY, color=WHITE)
d.box(s, "**then { … }**\ninre regler fyller samma element", I(9.15), CONTENT_TOP + I(3.7), I(3.55), I(0.95), size=14)

s = d.content_slide("Mappning: där det svåra finns", notes="""
Det tekniska ramverket är den enkla delen. Det svåra är mappningen, oavsett om den skrivs i FML eller kod.
Exempel från fasaden:

- Kön lagras som M/K och översätts med en ConceptMap till male/female (required-bindning).
- Nya koder i källan: journalsystemet har infört DIG. Den finns inte i ConceptMap:en, så type och class blir
  tomma och resultatet bryter mot profilen. Det är övning 5.3, och ett skäl att validera i drift (modul 6).
- Tidszoner: date ska inte ha tidszon, men dateTime med klockslag måste ha det. Här levererar API:t ISO 8601
  med tidszon. Annars hade mappningen behövt lägga till den, med hänsyn till sommartid.
- Logiska id: personnummer som resurs-id är enkelt men problematiskt. Personnummer kan bytas, och id:t läcker
  personuppgifter i URL:er och loggar.
- Saknade värden: en FML-regel körs inte om källan saknas, så inga tomma element skapas (ele-1).
""")
d.table(s, [
    ["Utmaning", "Exempel i fasaden", "Att tänka på"],
    ["Kodverk", "Kön `M`/`K` → `male`/`female` (ConceptMap)", "Required-bindningar kräver korrekt mappning"],
    ["Nya koder", "Kontakttypen `DIG` saknas i ConceptMap:en", "Upptäck med validering. Förvalta mappningen"],
    ["Datum och tid", "API:t levererar ISO 8601 med tidszon", "`dateTime` med klockslag kräver tidszon"],
    ["Identitet", "Personnummer som logiskt id", "Byte av personnummer, personuppgifter i URL:er"],
    ["Saknade värden", "Britta saknar telefonnummer", "Regeln körs inte – inga tomma element"],
    ["Referenser", "Vårdenhet som HSA-id", "Logisk eller bokstavlig referens?"],
    ["Prestanda", "Sökning utan index i källsystemet", "Paginering, `_count`, cache"],
    ["Profiler", "`meta.profile` = EducationPatient", "Validera svaren mot profilen i test"],
], MARGIN, CONTENT_TOP, CONTENT_W, col_widths=[2.0, 4.8, 5.2], size=15, row_height=I(0.58))

s = d.content_slide("API-säkerhet i lager", notes="""
Säkerhet är mer än en token. Gå igenom lagren:
- Transport: TLS överallt. Ofta mTLS mellan system, i Sverige t.ex. med SITHS-certifikat.
- Autentisering: vem är klienten, och vem är användaren? OpenID Connect för användare, signerad JWT eller mTLS
  för system.
- Auktorisation: vad får klienten göra? OAuth 2.0-scopes (SMART), men i vården också vårdrelation, samtycke,
  spärrar och sammanhållen journalföring. Det kräver mer än scopes.
- Loggning: vem läste vad och när? AuditEvent (IHE BALP). Krav enligt patientdatalagen.
""")
layers = [
    ("Transport", "TLS / mTLS (t.ex. SITHS-certifikat)"),
    ("Autentisering", "Vem är klienten och användaren? OpenID Connect, signerad JWT"),
    ("Auktorisation", "Vad får klienten göra? OAuth 2.0-scopes (SMART), vårdrelation, samtycke, spärrar"),
    ("Loggning", "Vem läste vad och när? AuditEvent (IHE BALP), loggkrav i patientdatalagen"),
]
for i, (head, body) in enumerate(layers):
    y = CONTENT_TOP + I(0.1) + i * I(1.1)
    d.box(s, f"**{head}**", MARGIN, y, I(2.6), I(0.9), fill=NAVY, color=WHITE, size=17)
    d.box(s, body, I(3.35), y, I(9.35), I(0.9), fill=TEAL_LIGHT, size=17, align=PP_ALIGN.LEFT)
d.callout(s, "FHIR, OAuth och SMART ger **byggstenarna**. Vårdens behörighetsregler måste fortfarande lösas i arkitekturen.",
          MARGIN, CONTENT_TOP + I(4.55), CONTENT_W, I(0.7), kind="warn", size=16)

s = d.content_slide("SMART on FHIR", notes="""
SMART on FHIR är en HL7-standard som bygger på OAuth 2.0 och OpenID Connect.

App Launch: en app startas från journalen (EHR launch) eller fristående, och får en token med kontext
(patient, encounter, användare). Används för appar inbäddade i journalsystem.

Backend Services: system-till-system utan användare. Klienten autentiserar sig med en signerad JWT och får en
token med system-scopes.

Scopes v2: resurs + behörighet (c=create, r=read, u=update, d=delete, s=search).

Discovery: /.well-known/smart-configuration talar om var auktorisationsservern finns och vad den stöder.

I fasaden finns ett förenklat exempel: DemoAuthorizationInterceptor.
""")
d.box(s, "**App Launch**\nApp startas från journalen eller fristående.\nToken + kontext (patient, användare).\nOpenID Connect för inloggning.",
      MARGIN, CONTENT_TOP + I(0.1), I(5.9), I(1.7), size=15, align=PP_ALIGN.LEFT)
d.box(s, "**Backend Services**\nSystem-till-system utan användare.\nKlienten signerar en JWT (client credentials).\nToken med system-scopes.",
      I(6.8), CONTENT_TOP + I(0.1), I(5.9), I(1.7), size=15, align=PP_ALIGN.LEFT, fill=ORANGE_LIGHT)
d.table(s, [
    ["Scope (SMART v2)", "Betyder"],
    ["`patient/Observation.rs`", "Läsa och söka observationer för patienten i kontexten"],
    ["`user/Encounter.cruds`", "Allt på vårdkontakter som användaren har rätt till"],
    ["`system/Patient.rs`", "Läsa och söka alla patienter (backend)"],
    ["`openid fhirUser launch/patient`", "Inloggning, användarens identitet, patientkontext"],
], MARGIN, CONTENT_TOP + I(2.1), I(7.6), col_widths=[3.2, 4.4], size=14, row_height=I(0.5))
d.code(s, """GET [bas]/.well-known/smart-configuration

{
  "token_endpoint": "https://auth…/token",
  "authorization_endpoint": "…",
  "scopes_supported": [ "system/*.rs", … ],
  "capabilities": [ "launch-ehr",
    "client-confidential-asymmetric", … ]
}""", I(8.4), CONTENT_TOP + I(2.1), I(4.3), I(3.1), lang="json", size=13)

s = d.content_slide("IHE-profiler för integration", notes="""
IHE (Integrating the Healthcare Enterprise) definierar profiler för hur standarder används i vanliga
integrationsscenarier. Flera finns som FHIR-varianter (det lilla m:et står för mobile, alltså FHIR/REST).

I svensk kontext är identitet (personnummer, samordningsnummer, reservnummer), katalog (HSA) och loggning (PDL)
centrala. Ofta är Inera och regionernas plattformar de som tillhandahåller tjänsterna.
""")
d.table(s, [
    ["Profil", "Område", "FHIR-resurser"],
    ["**IUA** – Internet User Authorization", "Token (OAuth 2.0) mellan system", "–"],
    ["**ATNA / BALP** – Audit", "Loggning av åtkomst", "AuditEvent"],
    ["**PDQm** – Patient Demographics Query", "Söka patientuppgifter", "Patient"],
    ["**PIXm / PMIR** – Identity", "Matcha och hantera patientidentiteter", "Patient, Bundle"],
    ["**MHD** – Mobile access to Health Documents", "Dela dokument", "DocumentReference, List"],
    ["**mCSD** – Care Services Directory", "Katalog över vårdgivare, enheter, personal", "Organization, Location, PractitionerRole"],
    ["**QEDm** – Query for Existing Data", "Hämta kliniska data", "Observation, Condition …"],
], MARGIN, CONTENT_TOP, CONTENT_W, col_widths=[4.3, 4.2, 3.5], size=15, row_height=I(0.58))

d.exercise_slide("REST, fasad och behörighet", [
    "**5.1** Utforska ett FHIR-API: **hapi.fhir.org/baseR4** (testdata!)  (5 min)",
    (1, "`/metadata`, `Patient?family=Smith&_count=5`, `_summary=count`, `_include`"),
    "**5.2** Lägg till en regel i FML-mappningen  (10 min)",
    (1, "Öppna `hapi-fasad/src/main/resources/fml/patient.map` och hitta `ÖVNING 5.2`"),
    (1, "Mappa `src.telefon` till `Patient.telecom` med `system = phone`"),
    (1, "Commit → arbetsflödet **HAPI-fasad** visar källans JSON och FHIR-resultatet sida vid sida"),
    "**5.3** (extra) Källsystemet har en ny kod, `DIG`. Lägg till den i ConceptMap:arna i `besok.map`",
    "**5.4** (demo) Fasaden med `--fasad.sakerhet.aktiv=true`: vilket scope krävs för Encounter?",
], where="kursmaterial/modul-5-hapi-fhir/README.md  ·  hapi-fasad/README.md  ·  lösning: kursmaterial/losningar/modul-5/", minutes=20, notes="""
5.2 fungerar helt i webbläsaren: arbetsflödet HAPI-fasad bygger med Maven, kör testerna, startar servern och visar
journalsystemets JSON och FHIR-resultatet sida vid sida i sammanfattningen. Tar cirka 1–2 minuter.
Lösningsregeln:
  src.telefon as tel -> tgt.telecom as telecom, telecom.system = 'phone', telecom.value = tel "telefon";
Fel i FML-filen ger rött i steget "Bygg och kör tester", med Error @rad, kolumn i loggen.

För den som vill köra lokalt: Codespaces eller Java 17 + Maven, mvn spring-boot:run i hapi-fasad.

Varna för att lägga riktiga personuppgifter på den publika testservern.
""")

summary_slide([
    "FHIR:s **REST-API**: ett fåtal interaktioner och kraftfull **sökning**",
    "Server med lagring, **fasad** eller integrationsplattform: välj efter behov",
    "HAPI: **resource providers**, och CapabilityStatement skapas automatiskt",
    "**FML** beskriver mappningen som data: regler, ConceptMaps och logiska modeller för källan",
    "Det svåra är **mappningen**: kodverk, tidszoner, identitet och saknade värden",
    "Säkerhet i lager: TLS, autentisering, **SMART/OAuth-scopes**, loggning",
    "**IHE-profiler** beskriver vanliga integrationsmönster",
], "Modul 6\nFöljsamhet, CapabilityStatement och validering", notes="""
Sista modulen knyter ihop dagen: hur vet vi att ett system och dess data följer IG:n?
""")

# =====================================================================================
# MODUL 6
# =====================================================================================
d.module_slide(6, "Följsamhet, krav och validering", [
    "förklara vad följsamhet mot en IG innebär",
    "läsa och skriva ett CapabilityStatement",
    "använda capability discovery",
    "validera instanser och tolka resultatet",
    "kravställa mot en IG med krav som går att verifiera",
], [(20, "Genomgång och demo"), (25, "Övningar 6.2–6.4"), (5, "Summering")], notes="""
Den här modulen är extra viktig för kravställare och testare: hur ställer man krav som går att verifiera?
""")

s = d.content_slide("Vad betyder följsamhet?", notes="""
Två nivåer:
- Data: en instans är giltig mot en profil (strukturell validering). Det kan kontrolleras automatiskt.
- System: ett system följer en IG om det beter sig som IG:n kräver. Det stöder rätt interaktioner och sökningar,
  hanterar Must Support-element, och säkerhet och felhantering fungerar. Det kräver test av beteende.

En IG bör innehålla tydliga konformitetskrav: SHALL/SHOULD/MAY, definition av Must Support,
och CapabilityStatements för de olika aktörerna.
""")
d.box(s, "**Data**\nÄr instansen giltig mot profilen?\n\nStruktur · kardinalitet · datatyper · bindningar · invarianter\n\n→ **Validering** (automatisk)",
      MARGIN, CONTENT_TOP + I(0.1), I(5.9), I(2.6), size=16, fill=TEAL_LIGHT)
d.box(s, "**System**\nBeter sig systemet som IG:n kräver?\n\nInteraktioner · sökparametrar · Must Support · säkerhet · felhantering\n\n→ **Test** av API-beteende",
      I(6.8), CONTENT_TOP + I(0.1), I(5.9), I(2.6), size=16, fill=ORANGE_LIGHT)
d.bullets(s, [
    "IG:n ska uttrycka krav så att de går att **verifiera**: SHALL / SHOULD / MAY",
    "**Must Support** måste definieras för både avsändare och mottagare",
    "**CapabilityStatement** beskriver vad en server ska kunna (krav) och vad den faktiskt kan",
], MARGIN, CONTENT_TOP + I(3.0), CONTENT_W, I(2.2), size=18)

s = d.content_slide("Kravställa mot en IG", notes="""
En IG blir ett krav först när kravställningen pekar ut den entydigt och säger hur följsamheten verifieras.
Gå igenom tabellen och betona kolumnen "verifieras med": ett krav som inte går att verifiera blir en diskussion
med leverantören i stället för en kontroll.

Vanliga otydligheter: "stödja FHIR" (vilken version, resurser, IG?), "hantera Must Support" (visa, lagra eller
bara inte krascha?), "följa HL7 Sverige" (vilken version av basprofilerna?).
""")
d.table(s, [
    ["Kravområde", "Exempel på verifierbart krav", "Verifieras med"],
    ["IG och version", "Lösningen SKA följa `fhir.education.kursig#0.1.0`", "Granskning"],
    ["Beroenden", "Profilerna SKA bygga på `hl7se.fhir.base#1.1.0`", "Granskning av paket"],
    ["Data", "Alla Encounter SKA validera utan fel mot EducationEncounter", "FHIR Validator i test och CI"],
    ["Must Support", "Avsändaren SKA skicka MS-element när informationen finns", "Testfall med ofullständiga data"],
    ["API", "Servern SKA ange `EducationServerCapabilities` i `instantiates`", "`GET /metadata`, Inferno/Touchstone"],
    ["Säkerhet", "Åtkomst SKA kräva SMART Backend Services, scope `system/Encounter.rs`", "Säkerhetstest"],
    ["Terminologi", "`Encounter.type` SKA kodas från `kontakttyp-vs` (version X)", "Validering mot terminologiserver"],
], MARGIN, CONTENT_TOP, CONTENT_W, col_widths=[2.0, 6.4, 3.6], size=14, row_height=I(0.55))
d.callout(s, "Peka ut IG:n med **paket-id och version**  ·  skriv **SKA / BÖR / KAN**  ·  ange **hur** varje krav verifieras  ·  lägg API-krav i ett **CapabilityStatement**",
          MARGIN, I(6.05), CONTENT_W, I(0.7), kind="info", size=15)

s = d.content_slide("CapabilityStatement", notes="""
CapabilityStatement finns i tre varianter (kind):
- instance: beskriver en faktisk, driftsatt server. Det är vad /metadata returnerar.
- capability: beskriver en mjukvaruprodukt.
- requirements: beskriver krav, t.ex. i en IG. "En server som följer IG:n SKA ..."

Viktiga element: fhirVersion, format, rest.mode (server/client), rest.security, rest.resource med type,
supportedProfile, interaction, searchParam, operation. instantiates pekar från en instans till de krav den
uppfyller, och implementationGuide anger vilka IG:er som följs.
""")
d.table(s, [
    ["kind", "Beskriver", "Exempel"],
    ["`instance`", "En faktisk, driftsatt server", "Det `GET [bas]/metadata` returnerar"],
    ["`capability`", "En mjukvaruprodukt", "\"HAPI FHIR JPA Server 8.x kan …\""],
    ["`requirements`", "Krav, t.ex. i en IG", "\"En server som följer kurs-IG:n SKA …\""],
], MARGIN, CONTENT_TOP, I(7.4), col_widths=[1.8, 2.6, 3.0], size=15, row_height=I(0.6))
d.bullets(s, [
    "`rest.resource.type` + `supportedProfile`",
    "`interaction`: read, search-type, create …",
    "`searchParam`: namn, typ, definition",
    "`rest.security`: t.ex. SMART on FHIR",
    "`instantiates`: \"jag uppfyller kraven i …\"",
    "`implementationGuide`: IG:er som följs",
    "Expectation-extension: **SHALL / SHOULD / MAY**",
], I(8.2), CONTENT_TOP - I(0.05), I(4.5), I(5.2), size=16)
d.code(s, """"rest": [ {
  "mode": "server",
  "resource": [ {
    "type": "Patient",
    "supportedProfile": [ ".../EducationPatient" ],
    "interaction": [ { "code": "read" }, { "code": "search-type" } ],
    "searchParam": [ { "name": "identifier", "type": "token" } ]
  } ]
} ]""",
       MARGIN, CONTENT_TOP + I(2.75), I(7.4), I(2.4), lang="json", size=13)

s = d.content_slide("Krav som CapabilityStatement i FSH", notes="""
Övning 6.2. Kraven från IG:n uttryckta maskinläsbart. IG Publisher gör en snygg sida av det.

Expectation-extensionen anger SHALL/SHOULD/MAY per interaktion och sökparameter.
Fasaden pekar på detta CapabilityStatement med instantiates.
""")
d.code(s, """Instance: EducationServerCapabilities
InstanceOf: CapabilityStatement
Usage: #definition
* name = "EducationServerCapabilities"
* status = #draft
* date = "2026-10-13"
* kind = #requirements
* fhirVersion = #4.0.1
* format[0] = #json
* rest[0].mode = #server
* rest[0].resource[0].type = #Patient
* rest[0].resource[0].supportedProfile = Canonical(EducationPatient)
* rest[0].resource[0].interaction[0].code = #read
* rest[0].resource[0].interaction[0].extension[$expectation].valueCode = #SHALL
* rest[0].resource[0].searchParam[0].name = "identifier"
* rest[0].resource[0].searchParam[0].type = #token
* rest[0].resource[0].searchParam[0].extension[$expectation].valueCode = #SHALL""",
       MARGIN, CONTENT_TOP + I(0.05), I(9.0), I(5.2), size=13, title="input/fsh/capabilities/EducationServerCapabilities.fsh")
d.callout(s, "**Kravet** (requirements) i IG:n\n↑ instantiates\n**Servern** (instance) via /metadata", I(9.85), CONTENT_TOP + I(0.4), I(2.85), I(1.9), kind="info", size=15)
d.callout(s, "`$expectation` är ett alias för\nextensionen capabilitystatement-expectation", I(9.85), CONTENT_TOP + I(2.6), I(2.85), I(1.3), kind="ok", size=14)

s = d.content_slide("Capability discovery", notes="""
En klient kan ta reda på vad en server stöder innan den börjar använda den:
1. GET /metadata: CapabilityStatement med FHIR-version, resurser, interaktioner, sökparametrar och profiler.
2. GET /.well-known/smart-configuration: var auktorisationsservern finns och vilka scopes och flöden som stöds.
3. Kontrollera instantiates och implementationGuide: följer servern den IG klienten är byggd för?

I R4 kan man också använda $versions för att se vilka FHIR-versioner servern stöder.
""")
steps = [
    ("1", "GET [bas]/metadata", "FHIR-version, resurser, interaktioner, sökparametrar, profiler"),
    ("2", "GET [bas]/.well-known/smart-configuration", "Auktorisationsserver, scopes, flöden"),
    ("3", "Kontrollera instantiates och implementationGuide", "Följer servern den IG klienten är byggd för?"),
    ("4", "Anpassa klienten", "Använd bara det servern faktiskt stöder"),
]
for i, (n, head, body) in enumerate(steps):
    y = CONTENT_TOP + I(0.15) + i * I(1.2)
    d.box(s, n, MARGIN, y + I(0.15), I(0.7), I(0.7), fill=ORANGE, color=WHITE, size=20, bold=True, shape=MSO_SHAPE.OVAL)
    d.box(s, f"`{head}`" if head.startswith("GET") else f"**{head}**", I(1.5), y, I(6.2), I(1.0), fill=TEAL_LIGHT, size=16, align=PP_ALIGN.LEFT)
    d.text(s, body, I(7.95), y + I(0.15), I(4.75), I(0.8), size=17, color=DARK)

s = d.content_slide("Validering", notes="""
Validatorn kontrollerar flera nivåer: struktur och datatyper, kardinalitet, bindningar mot terminologi (kräver
terminologiserver för externa kodsystem), invarianter, profiler (meta.profile eller angivna profiler) och i viss
mån referenser.

Resultatet är en OperationOutcome med issues: severity (fatal, error, warning, information), en kod, en text och
var i resursen (expression och rad).

Validering bör ske i utveckling, i CI, i test och vid behov i drift. Att validera allt i produktion kan vara dyrt.
""")
d.table(s, [
    ["Kontrolleras", "Exempel på fel"],
    ["Struktur och datatyper", "Okänt element, fel datatyp, ogiltigt datum"],
    ["Kardinalitet", "`Patient.name.family: minimum required = 1`"],
    ["Terminologi", "`'kvinna' was not found in the value set AdministrativeGender`"],
    ["Invarianter", "`Constraint failed: edu-pat-1`"],
    ["Profiler och slicing", "Fel antal i en slice, fast värde stämmer inte"],
    ["Best practice", "`dom-6: A resource should have narrative` (varning)"],
], MARGIN, CONTENT_TOP, I(7.6), col_widths=[2.6, 5.0], size=15, row_height=I(0.6))
d.code(s, """{
  "resourceType": "OperationOutcome",
  "issue": [ {
    "severity": "error",
    "code": "invariant",
    "details": { "text":
      "Constraint failed: edu-pat-1: 'Ett
       personnummer ska bestå av exakt
       12 siffror (ÅÅÅÅMMDDNNNN).'" },
    "expression": [ "Patient" ]
  } ]
}""", I(8.4), CONTENT_TOP + I(0.05), I(4.3), I(4.3), lang="json", size=13, title="Resultat: OperationOutcome")

s = d.content_slide("Verktyg för validering och test", notes="""
FHIR Validator (validator_cli.jar) är referensvalidatorn från HL7. Den används också av IG Publisher och finns
som webbtjänst på validator.fhir.org. HAPI har en egen validator som bygger på samma kärna.

I kursens repo körs validatorn i GitHub Actions på allt i mappen validering/ – samma princip kan användas i
verkliga projekt: validera exempel och testdata vid varje ändring.

För API-beteende: Inferno (ONC, öppen källkod), Touchstone (AEGIS), och connectathons.
""")
d.code(s, """java -jar validator_cli.jar validering/patient-fel.json \\
     -version 4.0.1 \\
     -ig test-ig/fsh-generated/resources \\
     -tx https://tx.fhir.org""", MARGIN, CONTENT_TOP + I(0.05), CONTENT_W, I(1.55), lang="text", size=16, title="FHIR Validator på kommandoraden (så gör arbetsflödet Validera instanser)")
d.table(s, [
    ["Verktyg", "Används till"],
    ["**FHIR Validator** (validator_cli.jar)", "Validera filer lokalt och i CI, mot valfria IG:er och paket"],
    ["**IG Publisher – qa.html**", "Validerar alla exempel i IG:n vid varje bygge"],
    ["**$validate**", "`POST [bas]/Patient/$validate` på en FHIR-server"],
    ["**validator.fhir.org**", "Webbgränssnitt för FHIR Validator"],
    ["**Inferno / Touchstone**", "Testa API-beteende mot en IG (sökning, säkerhet, CapabilityStatement)"],
], MARGIN, CONTENT_TOP + I(1.9), CONTENT_W, col_widths=[4.2, 7.8], size=15, row_height=I(0.55))

d.exercise_slide("Krav, CapabilityStatement och validering", [
    "**6.1** (demo) Kursledaren visar CapabilityStatement för fasaden och hapi.fhir.org/baseR4/metadata",
    "**6.2** Skriv kraven som ett CapabilityStatement (`kind = #requirements`) i `test-ig/input/fsh/capabilities/`  (10 min)",
    "**6.3** Validera instanser mot din profil  (10 min)",
    (1, "Kopiera filerna i `kursmaterial/modul-6-foljsamhet/exempel/` till mappen `validering/` och checka in"),
    (1, "Läs resultatet i **Validera instanser**. Vilka fel hittas? Varför är `patient-felstavat-system.json` giltig?"),
    (1, "Rätta `patient-fel.json` tills den blir grön"),
    "**6.4** I par: formulera **tre verifierbara krav** för en tjänst som visar vårdkontakter  (5 min)",
    "Förutsätter profilerna från modul 3–4: **Actions → Kom ikapp → modul 4** vid behov",
], where="kursmaterial/modul-6-foljsamhet/README.md  ·  facit: facit.md  ·  lösning: kursmaterial/losningar/modul-6/", minutes=25, notes="""
6.3 är dagens "aha"-övning: validatorn hittar det mesta, men inte stavfelet i identifierarens system.
Med öppen slicing och en invariant som filtrerar på rätt system blir instansen giltig trots fel data.

Diskutera: vilka fel kan en mottagare leva med? Vem ansvarar för valideringen? Hur skulle profilen kunna skärpas?
(Se förslaget edu-pat-3 i facit.)

6.4 knyter ihop dagen: kraven ska peka på IG, profil, CapabilityStatement och verifieringsmetod. Låt två par läsa
upp ett krav var och låt gruppen hitta tolkningsutrymmet.
""")

s = d.content_slide("Sammanfattning av dagen", notes="""
Gå tillbaka till den röda tråden: från att läsa en resurs till att validera mot egna profiler och beskriva krav
på servrar.

Uppmana deltagarna att behålla sina repon. De är en fungerande miljö för eget arbete: kopiera test-ig, byt
id och canonical, och börja profilera.
""")
recap = [
    ("1", "Läsa", "resurser, datatyper,\nbindningar, extensions"),
    ("2", "Tolka", "profiler, slicing,\nMust Support, IG:er"),
    ("3", "Skriva", "FSH + SUSHI +\nIG Publisher"),
    ("4", "Regler", "FHIRPath och\ninvarianter"),
    ("5", "Exponera", "FML-fasad, REST,\nSMART, IHE"),
    ("6", "Kvalitetssäkra", "Capability-\nStatement och\nvalidering"),
]
w, gap = I(1.85), I(0.18)
for i, (n, head, body) in enumerate(recap):
    x = MARGIN + i * (w + gap)
    d.box(s, n, x, CONTENT_TOP + I(0.2), I(0.6), I(0.6), fill=ORANGE, color=WHITE, size=20, bold=True, shape=MSO_SHAPE.OVAL)
    d.box(s, f"**{head}**\n{body}", x, CONTENT_TOP + I(0.95), w, I(1.6), fill=TEAL_LIGHT, size=15)
d.bullets(s, [
    "Ditt repo är en **fungerande miljö**: kopiera `test-ig`, byt `id` och `canonical`, och börja profilera",
    "Bygg och validera **automatiskt** vid varje ändring, lokalt med Docker eller i GitHub Actions",
    "**Återanvänd** befintliga profiler, extensions och kodverk innan du skapar nya",
], MARGIN, CONTENT_TOP + I(2.9), CONTENT_W, I(2.3), size=19)

d.section = "Avslutning"
s = d._slide(notes="""
Avslutningen (15 min): visa hur samma kedja körs utanför kursmiljön. Målet är att deltagarna ska kunna komma igång
med eget arbete, med eller utan installationsrättigheter. Materialet finns i kursmaterial/avslutning/README.md.
""", background=NAVY)
d.text(s, "Ta hem miljön", I(0.9), I(2.2), I(11.5), I(1.2), size=44, bold=True, color=WHITE)
d.text(s, "Samma kedja på din egen dator, och en egen IG att bygga vidare på", I(0.9), I(3.4), I(11.5), I(0.8), size=22, color=TEAL_LIGHT)
d.text(s, "15 minuter  ·  kursmaterial/avslutning/README.md", I(0.9), I(4.3), I(11.5), I(0.6), size=16, color=ORANGE)

s = d.content_slide("Installera verktygen lokalt", notes="""
Tre vägar beroende på vad man får installera:
1. Allt lokalt: Node + SUSHI, Java, Ruby + Jekyll. Skripten hämtar IG Publisher och Validator automatiskt.
2. Bara Docker: Docker-spåret i README (PowerShell-skript), som var det ursprungliga upplägget.
3. Ingenting: GitHub Codespaces ger samma miljö i webbläsaren.

VS Code med FSH-tillägget ger syntaxfärgning och felmarkering. Det fungerar inte fullt ut i github.dev.
""")
d.table(s, [
    ["Verktyg", "Installation", "Kontroll"],
    ["VS Code + FSH-tillägg", "code.visualstudio.com, tillägget FHIR Shorthand", ""],
    ["Git", "git-scm.com", "`git --version`"],
    ["Node.js + SUSHI", "nodejs.org, sedan `npm install -g fsh-sushi`", "`sushi --version`"],
    ["Java 17+", "adoptium.net (Temurin)", "`java -version`"],
    ["Ruby + Jekyll", "rubyinstaller.org, sedan `gem install jekyll`", "`jekyll --version`"],
    ["IG Publisher, Validator", "Hämtas automatiskt av skripten", ""],
], MARGIN, CONTENT_TOP, I(8.3), col_widths=[2.4, 4.0, 1.9], size=14, row_height=I(0.52))
d.callout(s, "**Får du inte installera?**\n\n• Bara Docker: Docker-spåret i README\n• Ingenting: GitHub Codespaces\n\nSamma skript i alla miljöer.",
          I(9.2), CONTENT_TOP + I(0.1), I(3.5), I(3.0), kind="info", size=15)
d.code(s, """./scripts/build-ig.sh --sushi-only   # snabb kontroll av FSH
./scripts/build-ig.sh                # hela IG:n -> test-ig/output/index.html
./scripts/validate.sh                # validera filerna i validering/""", MARGIN, CONTENT_TOP + I(3.95), CONTENT_W, I(1.3), lang="text", size=15)

s = d.content_slide("Starta en egen IG", notes="""
Ditt kursrepo är en färdig startpunkt. För en IG som ska förvaltas på riktigt: utgå från Ineras mall-repo, som har
versionshantering, releaser och publicering på samma sätt som kursens arbetsflöden.
""")
d.bullets(s, [
    "**1.** Kopiera `test-ig` till en ny mapp, t.ex. `min-ig`",
    "**2.** Ändra `id`, `canonical`, `name` och `title` i `sushi-config.yaml`, och sökvägen i `ig.ini`",
    "**3.** Lägg till beroenden, t.ex. `hl7se.fhir.base`, och profilera på dem",
    "**4.** Bygg: `./scripts/build-ig.sh min-ig`, eller ändra `IG_FOLDER` i arbetsflödet för GitHub",
    "**5.** Ska IG:n förvaltas på riktigt: utgå från **Ineras mall-repo** (versioner, releaser, publicering)",
    "**6.** Validera exempel och testdata i CI vid varje ändring, som i kursen",
], MARGIN, CONTENT_TOP, I(12), I(5.2), size=19)

s = d.content_slide("Vidare läsning och resurser", notes="""
Dela gärna länkarna i chatten. Uppmuntra deltagarna att gå med i chat.fhir.org (Zulip). Där svarar
specifikationens författare på frågor.
""")
d.table(s, [
    ["Resurs", "Adress"],
    ["FHIR R4-specifikationen", "hl7.org/fhir/R4"],
    ["HL7 Sverige – basprofiler", "hl7.se/fhir/ig/base"],
    ["FSH School – kurser och FSH Online", "fshschool.org"],
    ["FHIRPath Lab", "fhirpath-lab.com"],
    ["FHIR Validator (webb)", "validator.fhir.org"],
    ["SMART App Launch", "hl7.org/fhir/smart-app-launch"],
    ["IHE-profiler (FHIR)", "profiles.ihe.net"],
    ["HAPI FHIR", "hapifhir.io"],
    ["Chat – frågor och diskussion", "chat.fhir.org (#shorthand, #IG creation, #Sweden)"],
], MARGIN, CONTENT_TOP, CONTENT_W, col_widths=[5, 7], size=16, row_height=I(0.5))

s = d._slide(notes="Tack för i dag! Samla in utvärdering och frågor.", background=NAVY)
d.text(s, "Tack!", I(0.9), I(2.4), I(11.5), I(1.4), size=60, bold=True, color=WHITE)
d.text(s, "Frågor?  ·  Behåll ditt repo: det är din miljö för fortsatt arbete med FHIR", I(0.9), I(3.9), I(11.5), I(0.8), size=22, color=TEAL_LIGHT)
band = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, I(5.2), I(13.333), I(0.12))
band.fill.solid()
band.fill.fore_color.rgb = ORANGE
band.line.fill.background()


d.save(OUT)
print(f"Sparade {d.count} bilder till {OUT}")
