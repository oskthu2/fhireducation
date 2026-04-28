#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

command -v docker >/dev/null 2>&1 || {
  echo "Error: Docker not found. Please install Docker Desktop from https://www.docker.com/products/docker-desktop/"
  exit 1
}

echo ""
echo "Starting HAPI FHIR Sandbox..."
echo ""

docker compose up -d

echo ""
echo "======================================================"
echo "  FHIR Client  ->  http://localhost:3000"
echo "  FHIR API     ->  http://localhost:8080/fhir"
echo "  HAPI UI      ->  http://localhost:8080"
echo "======================================================"
echo ""
echo "  HAPI FHIR is starting — may take ~30s on first run."
echo "  The data loader runs automatically once the server"
echo "  is ready. Check progress with:"
echo ""
echo "    docker compose logs -f fhir-loader"
echo ""
echo "  To stop everything:"
echo ""
echo "    docker compose down"
echo ""
