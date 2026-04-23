# HAPI FHIR Sandbox

A local FHIR R4 development environment with:

- **HAPI FHIR** — fully featured FHIR R4 server, in-memory only (data is lost on restart)
- **FHIR Client** — lightweight browser UI for searching, reading, creating, updating and deleting resources
- **Data Loader** — automatically loads any FHIR JSON files from `data/` at startup
- **COS Extractor** — one-shot script to pull real data from Cambio Open Services into `data/`

## Quick Start

```bash
bash start.sh
```

Then open **http://localhost:3000** in your browser.

> HAPI FHIR takes ~30 seconds to start on the first run while it pulls the image and initialises.

## Ports

| Service | URL |
|---------|-----|
| FHIR Client | http://localhost:3000 |
| FHIR API | http://localhost:8080/fhir |
| HAPI Web UI | http://localhost:8080 |

## Loading Data

Place FHIR JSON files in the `data/` directory before starting. The loader supports:

- **Transaction / Batch Bundles** — `POST`ed to the base URL
- **Individual resources** — `POST`ed to `/{ResourceType}`

Filenames must end in `.json`. The loader runs once on startup and logs progress:

```bash
docker compose logs -f fhir-loader
```

To reload data after making changes:

```bash
docker compose restart fhir-loader
```

## Extracting Real Data from COS

The `extractor/` directory contains a TypeScript script that authenticates with
Cambio Open Services and writes FHIR transaction bundles directly into `data/`.

```bash
cd extractor
cp .env.example .env        # fill in COS credentials
npm install
npm run extract             # fetches resources, writes data/*.json
cd ..
bash start.sh               # starts HAPI + loads the extracted data
```

Configure what to extract via `.env`:

| Variable | Default | Description |
|---|---|---|
| `EXTRACT_PATIENT_IDENTIFIERS` | — | Comma-separated personnummer to look up |
| `EXTRACT_PATIENT_IDS` | — | Comma-separated FHIR Patient IDs (skip lookup) |
| `EXTRACT_RESOURCE_TYPES` | Patient, Condition, ... | Resource types to fetch |
| `EXTRACT_COUNT_PER_TYPE` | `50` | Max resources per type |
| `EXTRACT_OUTPUT_DIR` | `../data` | Where to write bundle files |

See `extractor/.env.example` for the full list.

## Stopping

```bash
docker compose down
```

All data is in-memory only — stopping the stack clears everything.

## Structure

```
hapi-fhir-sandbox/
├── start.sh            # Run this to start everything
├── docker-compose.yml
├── data/               # Put your FHIR JSON files here
├── extractor/          # COS → data/ extraction script
│   ├── .env.example
│   ├── extract.ts
│   └── package.json
├── loader/
│   └── load-data.sh    # Startup data loading script
└── client/
    ├── index.html      # Web client
    └── nginx.conf
```

## Requirements

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Mac / Windows) or Docker + Docker Compose (Linux)
- Node.js 18+ (only needed if using the extractor)
