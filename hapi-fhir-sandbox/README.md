# HAPI FHIR Sandbox

A local FHIR R4 development environment with:

- **HAPI FHIR** — fully featured FHIR R4 server, in-memory only (data is lost on restart)
- **FHIR Client** — lightweight browser UI for searching, reading, creating, updating and deleting resources
- **Data Loader** — automatically loads any FHIR JSON files from `data/` at startup

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
├── loader/
│   └── load-data.sh    # Startup data loading script
└── client/
    ├── index.html      # Web client
    └── nginx.conf
```

## Requirements

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Mac / Windows) or Docker + Docker Compose (Linux)
