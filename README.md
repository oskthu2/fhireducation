# FHIR i praktiken – utbildningsrepo

Det här repot används i FHIR-utbildningen *FHIR i praktiken: profilering, Implementation Guides, terminologi och
validering*. Det är både kursmaterial och en färdig **utbildningsmiljö**: en liten Implementation Guide (IG) som
byggs automatiskt med **SUSHI** och **IG Publisher** i GitHub Actions varje gång du checkar in en ändring.

Du kan alltså arbeta helt i webbläsaren: ändra filerna direkt på GitHub, checka in, och se din IG publiceras på
GitHub Pages. Den som vill kan också bygga lokalt med Docker.

| Innehåll | |
|----------|---|
| [`presentation/`](presentation/README.md) | Presentationen (PowerPoint, 79 bilder med talarmanus) |
| [`kursmaterial/`](kursmaterial/README.md) | Övningar, facit och lösningar för de sex modulerna, schema och avslutning |
| [`kursbok/`](kursbok/README.md) | Kursboken: fördjupning per modul och kapitel om REST, HAPI FHIR, SMART, FML, terminologi och IG-förvaltning. Publiceras på `https://<konto>.github.io/<repo>/kursbok/` |
| [`test-ig/`](test-ig/) | Kursens IG: startprofilen `EducationPatient` som byggs ut under dagen |
| [`validering/`](validering/) | JSON-instanser som valideras automatiskt mot dina profiler (modul 6) |
| [`hapi-fasad/`](hapi-fasad/README.md) | FHIR-fasad med HAPI FHIR som mappar ett proprietärt REST-API till FHIR med FHIR Mapping Language (modul 5) |
| [`hapi-fhir-sandbox/`](hapi-fhir-sandbox/README.md) | Lokal HAPI FHIR-server med svenska testpatienter (Docker) |
| `.github/workflows/` | Byggen i GitHub Actions |
| `scripts/` | Byggskript: PowerShell + Docker, eller bash utan Docker |

## Kursens moduler

| # | Modul (50 min) | Praktiskt moment |
|---|----------------|------------------|
| 1 | Läsa en FHIR-resurs | Tolka en Patient och hitta felet i en Encounter |
| 2 | Profiler, IG:er och verktyg | Tolka en profil, slicing |
| 3 | FHIR Shorthand (FSH) | Profil, terminologibindning, extension och slicing i `test-ig` |
| 4 | FHIRPath | Egna invarianter i profilerna |
| 5 | Utveckling med HAPI FHIR | FHIR-fasad ovanpå ett proprietärt REST-API med FHIR Mapping Language (FML), API-säkerhet, SMART on FHIR, IHE |
| 6 | Följsamhet, krav och validering | Kravställning mot IG, CapabilityStatement, capability discovery, validering mot profil |
| – | Avslutning (15 min) | Ta hem miljön: lokal installation och egen IG |

---

## Spår A: GitHub (rekommenderat)

Du behöver bara ett GitHub-konto och en webbläsare.

### 1. Skapa ditt eget repo från mallen

1. Öppna kursens mall-repo på GitHub.
2. Klicka **Use this template → Create a new repository**.
3. Välj ditt personliga konto som *Owner*, ge repot ett namn (t.ex. `fhir-kurs`) och välj **Public**.
   (GitHub Pages fungerar inte för privata repon på gratiskonton.)
4. Klicka **Create repository**.

### 2. Kör det första bygget

1. Gå till fliken **Actions** i ditt nya repo. Om GitHub frågar, klicka för att aktivera arbetsflödena.
2. Om inget bygge har startat: välj **Bygg IG** i listan till vänster och klicka **Run workflow**.
3. Vänta tills körningen fått en grön bock (2–4 minuter). Klicka på körningen och läs sammanfattningen.

### 3. Aktivera GitHub Pages

Bygget publicerar IG:n till grenen `gh-pages`. Den måste kopplas till GitHub Pages en gång:

1. **Settings → Pages**
2. *Source*: **Deploy from a branch**
3. *Branch*: **gh-pages** och mappen **/ (root)**, klicka **Save**
4. Efter någon minut finns din IG på `https://<ditt-konto>.github.io/<repo>/` och facit-IG:n (lösningen efter
   modul 6, används i övning 2.1) på `https://<ditt-konto>.github.io/<repo>/facit/`.
   Saknas något: *Actions → Bygg IG → Run workflow*.

> **Grattis!** 🎉 Nu har du en fungerande byggkedja med SUSHI + IG Publisher och är redo för utbildningen.

### 4. Så arbetar du under kursen

1. Öppna en fil, t.ex. `test-ig/input/fsh/profiles/EducationPatient.fsh`, och klicka på pennan (✏️).
   Vill du ändra flera filer samtidigt: tryck `.` i repot för att öppna webbeditorn **github.dev**.
2. Gör din ändring och klicka **Commit changes**.
3. Följ bygget under **Actions**. Sammanfattningen visar antal fel och varningar och länkar till din IG och till
   kvalitetsrapporten `qa.html`.

Testa direkt: ändra `title` i `test-ig/sushi-config.yaml`, checka in, och se den nya titeln i din IG efter bygget.

### Arbetsflöden i GitHub Actions

| Arbetsflöde | Startar när … | Gör |
|-------------|---------------|-----|
| **Bygg IG** | något ändras i `test-ig/` (eller manuellt) | Kör SUSHI och IG Publisher, publicerar på GitHub Pages och sparar IG:n som artefakt. Bygger även facit-IG:n under `/facit/` när den saknas och publicerar kursboken under `/kursbok/` |
| **Validera instanser** | något ändras i `validering/` eller i FSH-filerna | Validerar JSON-filerna i `validering/` mot dina profiler med HL7 FHIR Validator |
| **HAPI-fasad** | något ändras i `hapi-fasad/`, t.ex. en `.map`-fil | Bygger och testar FHIR-fasaden, startar den och visar källans JSON och FHIR-resultatet sida vid sida |
| **Kom ikapp** | du startar det manuellt | Ersätter dina FSH-filer med lösningen efter vald modul och startar bygget |
| **Kontrollera lösningar** | lösningarna ändras (eller manuellt) | För kursledaren: bygger alla lösningar och kontrollerar valideringsövningen |

Bara huvudgrenen (`main`) publiceras på GitHub Pages. Byggen på andra grenar kan laddas ner som artefakten
`ig-output` från körningen.

### Kom ikapp

Har du hamnat efter? **Actions → Kom ikapp → Run workflow**, välj läge (`3.2`, `3`, `4`, `6`, `extra-hl7se` eller
`start`) och klicka **Run workflow**. Dina egna filer sparas i mappen `mina-filer/`. Läget `extra-hl7se` lägger
även till beroendet till HL7 Sveriges basprofiler i `sushi-config.yaml`.

### Felsökning

| Problem | Lösning |
|---------|---------|
| Rött kryss i steget *Kör SUSHI* | Fel i FSH-koden. Öppna steget och läs felet (fil och rad). |
| Bygget är grönt men IG:n uppdateras inte | Kontrollera att GitHub Pages använder grenen `gh-pages` (steg 3). Ladda om sidan efter en minut. |
| 404 på GitHub Pages | Pages är inte aktiverat, eller repot är privat på ett gratiskonto. |
| Inga byggen startar | *Actions* kan vara avstängt: gå till fliken Actions och aktivera arbetsflödena. |
| Varningar om `electronichealth.se` i qa.html | Förväntat: identifierarsystemen saknar en definition (NamingSystem) i kursens IG. |

---

## Spår B: GitHub Codespaces

En komplett utvecklingsmiljö i webbläsaren med Java, Maven, Node.js (SUSHI), Jekyll och Docker.

1. I ditt repo: **Code → Codespaces → Create codespace on main**.
2. Vänta tills miljön är klar (första gången tar det några minuter).
3. Bygg IG:n i terminalen:
   ```bash
   ./scripts/build-ig.sh               # SUSHI + IG Publisher
   ./scripts/build-ig.sh --sushi-only  # bara SUSHI (snabbt)
   ./scripts/validate.sh               # validera filerna i validering/
   ```
4. Kör HAPI-fasaden: `cd hapi-fasad && mvn spring-boot:run` (port 8080 öppnas automatiskt).

## Spår C: Lokalt utan Docker (Linux, macOS, WSL)

Kräver Java 17+, Node.js och Ruby med Jekyll:

```bash
npm install -g fsh-sushi
gem install jekyll
./scripts/build-ig.sh
```

Resultatet hamnar i `test-ig/output/index.html`.

---

## Spår D: Lokalt med Docker (Windows)

### Förberedelser för Docker-spåret

Installera följande via företagsportalen:

- Visual Studio Code
- PMPC (Linux subsystem for windows) krävs för Docker.  
- Docker Desktop (Starta Docker Desktop manuellt i windows innan du kör ingång)
- Git (Git kräver en omstart för att funka i powershell)

•	Om powershell klagar på behörighet kan man behöva ändra en policy: skriv

```powershell
Set-ExecutionPolicy -ExecutionPolicy Unrestricted -Scope CurrentUser
```

Skapa sedan en mapp i din hemkatalog C:\Users\<användarnamn> som heter `fhireducation`.

### Klona repot

Öppna PowerShell och klona ditt eget repo (från spår A), eller kursens mall-repo:

```powershell
cd $HOME\fhireducation
git clone https://github.com/<ditt-konto>/fhireducation.git
cd fhireducation\test-ig
```

Exemplen nedan förutsätter att repot heter `fhireducation`. Byt ut mappnamnet om ditt repo heter något annat.

### Bygg IG:n med Docker

Repot innehåller nu Docker-konfiguration för att bygga en lokal IG Publisher-image  
som laddar ner senaste `publisher.jar` från HL7:s officiella release, och kör exempel-IG:n lokalt.
Konfigurationen använder också en persistent Docker-volume för `~/.fhir`, så paket/terminologi-cache återanvänds mellan körningar.

FHIR-version styrs via env-filen i repo-roten:

```powershell
# Tillåtna värden: v4, v5, v6
notepad .\.env.fhir
```

`FHIR_VERSION` används både för IG-byggkedjan och den lokala test-klienten/testdata.

Kör från repo-roten:

```powershell
cd $HOME\fhireducation\fhireducation
.\scripts\build-example-ig.ps1
```

Om ni vill köra kommandona manuellt:

```powershell
cd $HOME\fhireducation\fhireducation
docker compose build ig-publisher
docker compose --env-file .\.env.fhir run --volume "${PWD}\test-ig:/usr/src/ig" ig-publisher -ig /usr/src/ig/ig.ini
```

> `--rm` är borttaget så containern ligger kvar efter körningen.

---

> **Grattis!** 🎉  
> Nu har du en fungerande SUSHI + IG Publisher på din dator och är redo för utbildningen.  
> Nedan följer tips på hur du kan bekanta dig vidare med miljön och använda den för lokala byggen av egna IG:ar.

---

### Håll containern igång för CLI-kommandon

För att köra flera kommandon i samma container (utan att starta om varje gång):

```powershell
cd $HOME\fhireducation\fhireducation
.\scripts\run-ig-cli.ps1 -Mode start -IgFolder test-ig
```

Detta startar en container som ligger kvar (alive) och monterar IG-mappen till `/usr/src/ig`.

Stoppa containern när ni är klara:

```powershell
.\scripts\run-ig-cli.ps1 -Mode stop
```

### Köra på nya IG-mappar i samma utbildningsmapp

Exempel: om ni har en ny IG-mapp `min-nya-ig` i repo-roten, bredvid `test-ig`.  
Om ni följt stegen ovan blir det normalt: `$HOME\fhireducation\fhireducation\min-nya-ig`.

#### Skapa en ny IG med SUSHI init

Skapa mappen och initiera en tom IG-struktur med `sushi --init`:

```powershell
cd $HOME\fhireducation\fhireducation
mkdir min-nya-ig
.\scripts\run-ig-cli.ps1 -Mode start -IgFolder min-nya-ig
```

Kör sedan `sushi --init` inne i containern (svarar interaktivt på några frågor om namn, id och FHIR-version):

```powershell
docker exec -it ig-publisher-cli sushi --init /usr/src/ig
```

Stoppa containern när ni är klara:

```powershell
.\scripts\run-ig-cli.ps1 -Mode stop
```

Alternativt manuellt via Docker:

```powershell
docker compose --env-file .\.env.fhir run --entrypoint "" --volume "$HOME\fhireducation\fhireducation\min-nya-ig:/usr/src/ig" ig-publisher sushi --init /usr/src/ig
```

Detta skapar grundstrukturen (`sushi-config.yaml`, `input/fsh/`, `ig.ini` m.m.) i `min-nya-ig`.  
Därefter kan ni bygga IG:n med scripten nedan.

#### Bygga en befintlig IG-mapp

Bygg image en gång från repo-roten:

```powershell
cd $HOME\fhireducation\fhireducation
docker compose build ig-publisher
```

Eller kör scriptet direkt med valbar mapp:

```powershell
cd $HOME\fhireducation\fhireducation
.\scripts\build-example-ig.ps1 -IgFolder min-nya-ig
```

#### Endast SUSHI

Via script:

```powershell
.\scripts\run-ig-cli.ps1 -Mode sushi -IgFolder min-nya-ig
```

Manuellt via Docker:

```powershell
docker compose --env-file .\.env.fhir run --entrypoint "" --volume "$HOME\fhireducation\fhireducation\min-nya-ig:/usr/src/ig" ig-publisher sushi --out /usr/src/ig /usr/src/ig
```

#### Endast IG Publisher

Via script:

```powershell
.\scripts\run-ig-cli.ps1 -Mode publisher -IgFolder min-nya-ig
```

Manuellt via Docker:

```powershell
docker compose --env-file .\.env.fhir run --volume "$HOME\fhireducation\fhireducation\min-nya-ig:/usr/src/ig" ig-publisher -ig /usr/src/ig/ig.ini
```

#### SUSHI + IG Publisher

Via script (i en körning):

```powershell
.\scripts\run-ig-cli.ps1 -Mode sushi-publisher -IgFolder min-nya-ig
```

Manuellt via Docker (två steg):

1. Kör först "Endast SUSHI"
2. Kör sedan "Endast IG Publisher"

> Varje ny IG-mapp behöver en `ig.ini` i mappens rot som pekar på rätt `ImplementationGuide-*.json`.

## HAPI FHIR Sandbox

För att utforska FHIR mot en riktig lokal server med testpatienter, se [hapi-fhir-sandbox/README.md](hapi-fhir-sandbox/README.md).

## Resultat

När bygget är klart finns resultatet i mappen `test-ig/output`. Öppna `test-ig/output/index.html`.

## Tips

Öppna gärna hela repot i Visual Studio Code (eller github.dev) och titta särskilt på:

- `test-ig/sushi-config.yaml`
- `test-ig/input/fsh/profiles/EducationPatient.fsh`
- `test-ig/input/fsh/examples/patient-tolvan.fsh`
- `test-ig/input/pagecontent/index.md`

FHIR-versionen styrs av `FHIR_VERSION` i `.env.fhir` (`v4` = 4.0.1) och används av både Docker-skripten och
`scripts/build-ig.sh`. Kursens övningar är skrivna för R4.

---

## För kursledaren

- Gör repot till en mall: **Settings → General → Template repository**. Deltagarna skapar sedan egna repon med
  *Use this template*.
- Kör **Actions → Kontrollera lösningar** några dagar före kursen, för att se att alla lösningar fortfarande bygger
  med senaste IG Publisher.
- Kör **Actions → Bygg IG → Run workflow** på `main` så att facit-IG:n finns under `/facit/`.
- Schema, checklista och hur IG:n byggs upp under dagen: [kursmaterial/README.md](kursmaterial/README.md).
- Material för avslutningen (lokal installation, egen IG): [kursmaterial/avslutning/README.md](kursmaterial/avslutning/README.md).
