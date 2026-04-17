# FHIR Education

Det här repot används i FHIR-utbildningen.

## Förberedelser

Installera följande via företagsportalen:

- Visual Studio Code
- Docker Desktop
- Git

Skapa sedan en mapp på skrivbordet som heter `fhireducation`.

## Klona repot

Öppna PowerShell och kör:

```powershell
cd $HOME\Desktop\fhireducation
git clone https://github.com/<din-org-eller-användare>/fhireducation.git
cd fhireducation\test-ig
```

## Bygg IG:n med Docker

Repot innehåller nu Docker-konfiguration för att bygga IG Publisher-imagen direkt från  
`https://github.com/HL7/fhir-ig-publisher.git` och köra exempel-IG:n lokalt.

Kör från repo-roten:

```powershell
cd $HOME\Desktop\fhireducation\fhireducation
.\scripts\build-example-ig.ps1
```

Om ni vill köra kommandona manuellt:

```powershell
cd $HOME\Desktop\fhireducation\fhireducation
docker compose build ig-publisher
docker compose run --rm --volume "${PWD}\test-ig:/usr/src/ig" ig-publisher -ig /usr/src/ig
```

## Resultat

När bygget är klart finns resultatet i mappen `output`.

Öppna sedan:

`output/index.html`

## Tips

Öppna gärna hela repot i Visual Studio Code och titta särskilt på:

- `sushi-config.yaml`
- `input/fsh/profiles.fsh`
- `input/pagecontent/index.md`
