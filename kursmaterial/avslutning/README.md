# Avslutning – ta hem miljön (15 min)

Under kursen har du byggt i GitHub. Samma kedja kan köras på din egen dator, och ditt repo är en färdig
startpunkt för eget arbete.

## 1. Installera verktygen lokalt

| Verktyg | Installation | Kontrollera |
|---------|--------------|-------------|
| Visual Studio Code | code.visualstudio.com, eller via företagsportalen | |
| FSH-tillägg till VS Code | Sök efter *FHIR Shorthand* (MITRE-Health) i Extensions | Färgade .fsh-filer |
| Git | git-scm.com | `git --version` |
| Node.js (LTS) | nodejs.org | `node --version` |
| SUSHI | `npm install -g fsh-sushi` | `sushi --version` |
| Java 17+ | adoptium.net (Temurin) | `java -version` |
| Ruby + Jekyll | rubyinstaller.org (Windows), sedan `gem install jekyll` | `jekyll --version` |
| IG Publisher | Hämtas automatiskt av `scripts/build-ig.sh` | |
| FHIR Validator | Hämtas automatiskt av `scripts/validate.sh` | |

**Kan du inte installera Java, Ruby och Node?** Använd Docker-spåret i [README](../../README.md#spår-d-lokalt-med-docker-windows)
(bara Docker Desktop och Git behövs) eller GitHub Codespaces (inget alls behöver installeras).

## 2. Klona och bygg

```bash
git clone https://github.com/<ditt-konto>/<repo>.git
cd <repo>
./scripts/build-ig.sh --sushi-only   # snabb kontroll av FSH
./scripts/build-ig.sh                # hela IG:n -> test-ig/output/index.html
./scripts/validate.sh                # validera filerna i validering/
```

På Windows utan bash: `.\scripts\build-example-ig.ps1` (Docker).

## 3. Starta en egen IG

1. Kopiera `test-ig` till en ny mapp, t.ex. `min-ig`.
2. Ändra `id`, `canonical`, `name`, `title` i `min-ig/sushi-config.yaml`, och sökvägen i `min-ig/ig.ini`
   (`ImplementationGuide-<id>.json`).
3. Lägg till beroenden, t.ex. HL7 Sveriges basprofiler (`hl7se.fhir.base`), och profilera på dem.
4. Bygg: `./scripts/build-ig.sh min-ig`. Vill du bygga i GitHub: ändra `IG_FOLDER` i `.github/workflows/build-ig.yml`.
5. Ska IG:n förvaltas på riktigt: utgå från Ineras mall-repo för IG:er, som har versionshantering,
   releaser och publicering.

## 4. Fortsätt lära

| Resurs | |
|--------|---|
| FHIR R4-specifikationen | hl7.org/fhir/R4 |
| HL7 Sverige – basprofiler | hl7.se/fhir/ig/base |
| FSH School (kurser, FSH Online) | fshschool.org |
| FHIRPath Lab | fhirpath-lab.com |
| SMART App Launch | hl7.org/fhir/smart-app-launch |
| IHE-profiler | profiles.ihe.net |
| Chat för frågor | chat.fhir.org (`#shorthand`, `#IG creation`, `#Sweden`) |
