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

Kör från repo-roten:

```powershell
cd $HOME\fhireducation\fhireducation
.\scripts\build-example-ig.ps1
```

Om ni vill köra kommandona manuellt:

```powershell
cd $HOME\fhireducation\fhireducation
docker compose build ig-publisher
docker compose run --volume "${PWD}\test-ig:/usr/src/ig" ig-publisher -ig /usr/src/ig/ig.ini
```

> `--rm` är borttaget så containern ligger kvar efter körningen.

## Köra på nya IG-mappar i samma utbildningsmapp

Exempel: om ni har en ny IG-mapp `min-nya-ig` i repo-roten, bredvid `test-ig`.  
Om ni följt stegen ovan blir det normalt: `$HOME\fhireducation\fhireducation\min-nya-ig`.

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

```powershell
docker compose run --entrypoint "" --volume "$HOME\fhireducation\fhireducation\min-nya-ig:/usr/src/ig" ig-publisher sushi --out /usr/src/ig /usr/src/ig
```

### Endast IG Publisher

```powershell
docker compose run --volume "$HOME\fhireducation\fhireducation\min-nya-ig:/usr/src/ig" ig-publisher -ig /usr/src/ig/ig.ini
```

### SUSHI + IG Publisher

Kör först "Endast SUSHI", och kör sedan "Endast IG Publisher".

> Varje ny IG-mapp behöver en `ig.ini` i mappens rot som pekar på rätt `ImplementationGuide-*.json`.

## Resultat

När bygget är klart finns resultatet i mappen `output`.

Öppna sedan:

`output/index.html`

## Tips

Öppna gärna hela repot i Visual Studio Code och titta särskilt på:

- `sushi-config.yaml`
- `input/fsh/profiles.fsh`
- `input/pagecontent/index.md`
