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

Bygg först Docker-imagen för IG Publisher om ni använder den lokalt från HL7:s repo:

```powershell
cd $HOME\Desktop\fhireducation
git clone https://github.com/HL7/fhir-ig-publisher.git
cd fhir-ig-publisher
docker build -t fhir-ig-publisher:test .
```

Gå sedan tillbaka till test-IG:n och kör bygget:

```powershell
docker run --rm --mount type=bind,src=$HOME\Desktop\fhireducation\fhireducation\test-ig,dst=/usr/src/ig fhir-ig-publisher:test -ig /usr/src/ig
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
