# FHIR Education

Det här repot används i FHIR-utbildningen.

## Förberedelser

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

## Klona repot

Öppna PowerShell och kör:

```powershell
cd $HOME\fhireducation
git clone https://github.com/oskthu2/fhireducation.git
cd fhireducation\test-ig
```

## Bygg IG:n med Docker

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

## Håll containern igång för CLI-kommandon

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

## Köra på nya IG-mappar i samma utbildningsmapp

Exempel: om ni har en ny IG-mapp `min-nya-ig` i repo-roten, bredvid `test-ig`.  
Om ni följt stegen ovan blir det normalt: `$HOME\fhireducation\fhireducation\min-nya-ig`.

### Skapa en ny IG med SUSHI init

Skapa mappen och initiera en tom IG-struktur med `sushi --init`:

```powershell
cd $HOME\fhireducation\fhireducation
mkdir min-nya-ig
.\scripts\run-ig-cli.ps1 -Mode start -IgFolder min-nya-ig
```

Kör sedan `sushi --init` inne i containern (svarar interaktivt på några frågor om namn, id och FHIR-version):

```powershell
.\scripts\run-ig-cli.ps1 -Mode shell -IgFolder min-nya-ig
# Inne i containern:
sushi --init /usr/src/ig
exit
```

Alternativt manuellt via Docker:

```powershell
docker compose --env-file .\.env.fhir run --entrypoint "" --volume "$HOME\fhireducation\fhireducation\min-nya-ig:/usr/src/ig" ig-publisher sushi --init /usr/src/ig
```

Detta skapar grundstrukturen (`sushi-config.yaml`, `input/fsh/`, `ig.ini` m.m.) i `min-nya-ig`.  
Därefter kan ni bygga IG:n med scripten nedan.

### Bygga en befintlig IG-mapp

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

### Endast SUSHI

Via script:

```powershell
.\scripts\run-ig-cli.ps1 -Mode sushi -IgFolder min-nya-ig
```

Manuellt via Docker:

```powershell
docker compose --env-file .\.env.fhir run --entrypoint "" --volume "$HOME\fhireducation\fhireducation\min-nya-ig:/usr/src/ig" ig-publisher sushi --out /usr/src/ig /usr/src/ig
```

### Endast IG Publisher

Via script:

```powershell
.\scripts\run-ig-cli.ps1 -Mode publisher -IgFolder min-nya-ig
```

Manuellt via Docker:

```powershell
docker compose --env-file .\.env.fhir run --volume "$HOME\fhireducation\fhireducation\min-nya-ig:/usr/src/ig" ig-publisher -ig /usr/src/ig/ig.ini
```

### SUSHI + IG Publisher

Via script (i en körning):

```powershell
.\scripts\run-ig-cli.ps1 -Mode sushi-publisher -IgFolder min-nya-ig
```

Manuellt via Docker (två steg):

1. Kör först "Endast SUSHI"
2. Kör sedan "Endast IG Publisher"

> Varje ny IG-mapp behöver en `ig.ini` i mappens rot som pekar på rätt `ImplementationGuide-*.json`.

## Lokal test-klient med versionsstyrd testdata

Starta test-klienten:

```powershell
cd $HOME\fhireducation\fhireducation
docker compose --env-file .\.env.fhir up --build -d test-client
```

Öppna sedan `http://localhost:8080` (eller porten i `TEST_CLIENT_PORT` i `.env.fhir`).

Sidan visar vald `FHIR_VERSION` och laddar motsvarande testdata (`test-data/v4|v5|v6`).

## Resultat

När bygget är klart finns resultatet i mappen `output`.

Öppna sedan:

`output/index.html`

## Tips

Öppna gärna hela repot i Visual Studio Code och titta särskilt på:

- `test-ig/sushi-config.yaml`
- `test-ig/input/fsh/profiles.fsh`
- `test-ig/input/pagecontent/index.md`
