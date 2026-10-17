# Kursbok

`index.html` är kursboken för deltagare: en webbsida med fördjupning till varje modul, kontrollfrågor med svar,
länkar till övningarna och nio fristående fördjupningskapitel:

| Kapitel | Innehåll |
|---------|----------|
| A | REST-API:t på djupet: interaktioner, versioner, villkorliga anrop, sökning, transaktioner, operationer |
| B | HAPI FHIR: moduler, klient, Plain Server, interceptorer, JPA Server, validering |
| C | SMART on FHIR: App Launch, discovery, scopes, Backend Services |
| D | FHIR Mapping Language och StructureMap |
| E | Terminologi och terminologitjänster |
| F | IG-förvaltning, paket och versioner |
| G | IHE, Sverige och Europa (EHDS) |
| H | Bulk Data, Subscriptions, CDS Hooks, SQL on FHIR, SDC med mera |
| I | Ordlista och länksamling |

Arbetsflödet **Bygg IG** kopierar mappen till GitHub Pages, så boken finns på
`https://<konto>.github.io/<repo>/kursbok/`. Där pekar länkarna till övningarna automatiskt på ditt eget repo.
Öppnar du filen någon annanstans pekar de på kursens mallrepo.

Boken är en enda HTML-fil utan byggsteg. Ändra direkt i `index.html`. Typsnitten hämtas från Google Fonts.
