# Presentation

`FHIR-utbildning.pptx` är kursens presentation med 79 bilder för inledning, 6 moduler à 50 minuter och avslutning. Varje bild har
talarmanus i anteckningsfältet.

| Bilder | Innehåll |
|--------|----------|
| 1–6 | Inledning (15 min): upplägg, mål, röd tråd och utbildningsmiljön i GitHub |
| 7–18 | Modul 1 – Läsa en FHIR-resurs |
| 19–32 | Modul 2 – Profiler och Implementation Guides (inkl. terminologi i praktiken) |
| 33–44 | Modul 3 – FHIR Shorthand (FSH) (inkl. HL7 Sveriges basprofiler) |
| 45–52 | Modul 4 – FHIRPath och invarianter |
| 53–64 | Modul 5 – Utveckling med HAPI FHIR, FHIR-fasad med FHIR Mapping Language, API-säkerhet, SMART on FHIR och IHE |
| 65–74 | Modul 6 – Följsamhet, kravställning, CapabilityStatement och validering |
| 75–79 | Avslutning (15 min): ta hem miljön, resurser |

## Ändra presentationen

Presentationen genereras från `bygg_presentation.py`. Det gör den lätt att hålla i takt med övningarna
och kodexemplen. Du kan också redigera `.pptx`-filen direkt i PowerPoint, men då skrivs ändringarna över
nästa gång skriptet körs.

```bash
pip install python-pptx
python presentation/bygg_presentation.py
```

- `bygg_presentation.py` – innehållet: bilder, tabeller, kodexempel och talarmanus
- `pptx_helpers.py` – layout, färger och hjälpfunktioner (punktlistor, kodrutor, tabeller, övningsbilder)
