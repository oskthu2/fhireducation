Det här är den Implementation Guide (IG) som vi bygger upp under FHIR-utbildningen.

Den byggs automatiskt med **SUSHI** och **IG Publisher** av GitHub Actions varje gång du checkar in en ändring
under `test-ig/`. Resultatet publiceras på repots GitHub Pages-sida.

### Innehåll

Startläget innehåller en enda profil, [EducationPatient](StructureDefinition-EducationPatient.html),
och ett exempel på en patient som följer profilen. Under kursen bygger vi vidare med:

| Modul | Det här lägger vi till |
|-------|------------------------|
| 3 – FSH | Profilen `EducationEncounter`, terminologibindningar, en egen extension och slicing av `identifier` |
| 4 – FHIRPath | Egna invarianter (constraints) på Patient och Encounter |
| 6 – Följsamhet | Ett CapabilityStatement som beskriver krav på en server |

Se alla artefakter under [Artefakter](artifacts.html). Kvalitetsrapporten från IG Publisher finns i [qa.html](qa.html).

{% include ip-statements.xhtml %}
{% include cross-version-analysis.xhtml %}
{% include dependency-table.xhtml %}
{% include globals-table.xhtml %}
