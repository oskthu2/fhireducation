/**
 * COS → HAPI FHIR data extractor.
 *
 * Fetches FHIR resources from COS (Cambio Open Services) and writes
 * FHIR transaction bundles to the sandbox data/ directory so the
 * HAPI loader can import them on startup.
 *
 * Auth model (COS Quick Start v1.7):
 *   Token:  POST with Basic auth (base64 clientId:clientSecret)
 *   FHIR:   Bearer token + Ocp-Apim-Subscription-Key header
 *
 * Usage:
 *   cp .env.example .env   # fill in credentials
 *   npm install
 *   npm run extract
 */

import { writeFileSync, mkdirSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";
import "dotenv/config";

// ── Config ───────────────────────────────────────────────────────────────────

function required(name: string): string {
  const v = process.env[name];
  if (!v) throw new Error(`Missing required env var: ${name}`);
  return v;
}

const __dir = dirname(fileURLToPath(import.meta.url));

const cfg = {
  // COS connection
  fhirBaseUrl:    required("COS_FHIR_BASE_URL"),
  tokenUrl:       required("COS_TOKEN_URL"),
  clientId:       required("COS_CLIENT_ID"),
  clientSecret:   required("COS_CLIENT_SECRET"),
  apiKey:         required("COS_API_KEY"),
  scope:          process.env.COS_SCOPE ?? "user/*.read user/*.write",

  // Extraction
  outputDir:            resolve(__dir, process.env.EXTRACT_OUTPUT_DIR ?? "../data"),
  patientIdentifiers:   csv(process.env.EXTRACT_PATIENT_IDENTIFIERS),
  patientIds:           csv(process.env.EXTRACT_PATIENT_IDS),
  resourceTypes:        csv(process.env.EXTRACT_RESOURCE_TYPES) || defaultResourceTypes(),
  countPerType:         parseInt(process.env.EXTRACT_COUNT_PER_TYPE ?? "50", 10),
};

function csv(s: string | undefined): string[] {
  return (s ?? "").split(",").map(v => v.trim()).filter(Boolean);
}

function defaultResourceTypes(): string[] {
  return [
    "Patient", "Condition", "MedicationRequest",
    "Observation", "Encounter", "AllergyIntolerance",
    "Practitioner", "Organization",
  ];
}

// Resource types that do NOT require a patient reference for searching
const STANDALONE_TYPES = new Set(["Patient", "Practitioner", "Organization", "Location"]);

// COS uses 'patient' for Observation, 'subject' for most others
const PATIENT_PARAM: Record<string, string> = {
  Observation: "patient",
};

// ── Auth ─────────────────────────────────────────────────────────────────────

let _token: string | null = null;
let _tokenExpiry = 0;

async function getToken(): Promise<string> {
  if (_token && Date.now() < _tokenExpiry) return _token;

  const credentials = Buffer.from(`${cfg.clientId}:${cfg.clientSecret}`).toString("base64");
  const body = new URLSearchParams({ grant_type: "client_credentials" });
  if (cfg.scope) body.set("scope", cfg.scope);

  const res = await fetch(cfg.tokenUrl, {
    method: "POST",
    headers: {
      Authorization: `Basic ${credentials}`,
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: body.toString(),
  });

  if (!res.ok) throw new Error(`COS auth failed (${res.status}): ${await res.text()}`);

  const data = await res.json() as { access_token: string; expires_in: number };
  _token = data.access_token;
  _tokenExpiry = Date.now() + (data.expires_in - 30) * 1000;
  return _token;
}

// ── FHIR GET ─────────────────────────────────────────────────────────────────

type FhirResource = Record<string, unknown> & { resourceType: string; id?: string };
type FhirBundle  = { resourceType: "Bundle"; entry?: Array<{ resource: FhirResource }>; link?: Array<{ relation: string; url: string }> };

async function fhirGet(path: string, params?: Record<string, string>): Promise<FhirBundle> {
  const token = await getToken();
  const url = new URL(`${cfg.fhirBaseUrl.replace(/\/$/, "")}/${path.replace(/^\//, "")}`);
  if (params) {
    for (const [k, v] of Object.entries(params)) url.searchParams.set(k, v);
  }

  const res = await fetch(url.toString(), {
    headers: {
      Authorization: `Bearer ${token}`,
      "Ocp-Apim-Subscription-Key": cfg.apiKey,
      Accept: "application/fhir+json",
    },
  });

  if (!res.ok) throw new Error(`GET ${path} failed (${res.status}): ${await res.text()}`);
  return res.json() as Promise<FhirBundle>;
}

// ── Fetch with one page of pagination ────────────────────────────────────────

async function fetchResources(
  resourceType: string,
  params: Record<string, string> = {}
): Promise<FhirResource[]> {
  const results: FhirResource[] = [];
  const page1 = await fhirGet(resourceType, { ...params, _count: String(cfg.countPerType) });

  for (const e of page1.entry ?? []) results.push(e.resource);

  // Follow one next-page link so we don't hammer the API
  const nextUrl = page1.link?.find(l => l.relation === "next")?.url;
  if (nextUrl && results.length < cfg.countPerType) {
    try {
      const token = await getToken();
      const res = await fetch(nextUrl, {
        headers: {
          Authorization: `Bearer ${token}`,
          "Ocp-Apim-Subscription-Key": cfg.apiKey,
          Accept: "application/fhir+json",
        },
      });
      if (res.ok) {
        const page2 = await res.json() as FhirBundle;
        for (const e of page2.entry ?? []) results.push(e.resource);
      }
    } catch { /* ignore pagination errors */ }
  }

  return results.slice(0, cfg.countPerType);
}

// ── Strip server-generated metadata ──────────────────────────────────────────

function cleanResource(r: FhirResource): FhirResource {
  if (!r.meta) return r;
  const { lastUpdated, versionId, source, ...rest } = r.meta as Record<string, unknown>;
  return { ...r, meta: Object.keys(rest).length > 0 ? rest : undefined };
}

// ── Build transaction bundle ──────────────────────────────────────────────────

function transactionBundle(resources: FhirResource[]): object {
  return {
    resourceType: "Bundle",
    type: "transaction",
    entry: resources.map(r => ({
      resource: r,
      request: {
        method: r.id ? "PUT" : "POST",
        url:    r.id ? `${r.resourceType}/${r.id}` : r.resourceType,
      },
    })),
  };
}

// ── Deduplication ─────────────────────────────────────────────────────────────

function dedup(resources: FhirResource[]): FhirResource[] {
  const seen = new Set<string>();
  return resources.filter(r => {
    if (!r.id) return true;
    if (seen.has(r.id)) return false;
    seen.add(r.id);
    return true;
  });
}

// ── Main ─────────────────────────────────────────────────────────────────────

async function main() {
  console.log("COS → HAPI FHIR extractor");
  console.log("==========================\n");
  console.log(`Output dir:   ${cfg.outputDir}`);
  console.log(`Resource types: ${cfg.resourceTypes.join(", ")}`);
  console.log(`Max per type:   ${cfg.countPerType}\n`);

  mkdirSync(cfg.outputDir, { recursive: true });

  // ── Step 1: resolve patient FHIR IDs ──────────────────────────────────────

  const patientFhirIds: string[] = [...cfg.patientIds];

  for (const ident of cfg.patientIdentifiers) {
    const pnr = ident.replace(/[-+\s]/g, "");
    process.stdout.write(`Looking up patient ${pnr} ... `);
    try {
      let bundle = await fhirGet("Patient", {
        identifier: `urn:oid:1.2.752.129.2.1.3.1|${pnr}`,
      });
      if ((bundle.entry ?? []).length === 0) {
        bundle = await fhirGet("Patient", { identifier: pnr });
      }
      const ids = (bundle.entry ?? []).map(e => e.resource.id).filter(Boolean) as string[];
      ids.forEach(id => { if (!patientFhirIds.includes(id)) patientFhirIds.push(id); });
      console.log(`found ${ids.length}: ${ids.join(", ") || "(none)"}`);
    } catch (err: unknown) {
      console.warn(`WARN: ${(err as Error).message}`);
    }
  }

  if (patientFhirIds.length === 0 && cfg.patientIdentifiers.length === 0) {
    console.log("No patient filter set — fetching standalone resource types only.\n");
  } else if (patientFhirIds.length === 0) {
    console.warn("\nNo patient FHIR IDs resolved. Patient-linked resources will be skipped.\n");
  } else {
    console.log(`\nPatient IDs: ${patientFhirIds.join(", ")}\n`);
  }

  // ── Step 2: fetch resources ────────────────────────────────────────────────

  const collected: Record<string, FhirResource[]> = {};

  for (const rt of cfg.resourceTypes) {
    collected[rt] = [];
    const linked = !STANDALONE_TYPES.has(rt);
    const paramKey = PATIENT_PARAM[rt] ?? "subject";

    if (linked && patientFhirIds.length > 0) {
      for (const pid of patientFhirIds) {
        process.stdout.write(`  ${rt} for Patient/${pid} ... `);
        try {
          const resources = await fetchResources(rt, { [paramKey]: `Patient/${pid}` });
          collected[rt].push(...resources);
          console.log(`${resources.length} found`);
        } catch (err: unknown) {
          console.warn(`WARN: ${(err as Error).message}`);
        }
      }
    } else if (!linked || patientFhirIds.length === 0) {
      process.stdout.write(`  ${rt} ... `);
      try {
        const resources = await fetchResources(rt);
        collected[rt].push(...resources);
        console.log(`${resources.length} found`);
      } catch (err: unknown) {
        console.warn(`WARN: ${(err as Error).message}`);
      }
    }

    collected[rt] = dedup(collected[rt]);
  }

  // ── Step 3: write bundles ─────────────────────────────────────────────────

  console.log("");
  let totalFiles = 0;
  let totalResources = 0;

  for (const [rt, resources] of Object.entries(collected)) {
    if (resources.length === 0) continue;
    const bundle = transactionBundle(resources.map(cleanResource));
    const file = `${cfg.outputDir}/${rt.toLowerCase()}.json`;
    writeFileSync(file, JSON.stringify(bundle, null, 2), "utf-8");
    console.log(`Wrote ${rt.toLowerCase()}.json  (${resources.length} resources)`);
    totalFiles++;
    totalResources += resources.length;
  }

  console.log(`\n✓ ${totalResources} resources → ${totalFiles} bundle files in ${cfg.outputDir}`);
  console.log("");
  console.log("Next steps:");
  console.log("  1. cd ..");
  console.log("  2. bash start.sh");
  console.log("  3. Open http://localhost:3000");
}

main().catch(err => {
  console.error("\nFatal:", (err as Error).message);
  process.exit(1);
});
