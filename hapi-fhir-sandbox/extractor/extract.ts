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
  // Types confirmed reachable via COS open FHIR endpoint as of 2026-04.
  // See SKIP_TYPES below for types that are blocked or unsupported.
  return [
    "Patient",
    "Observation",         // vital signs + lab results
    "Encounter",           // care contacts / admissions (POST search bypasses _sid)
    "ClinicalImpression",  // journal notes equivalent in COSMIC
    "CarePlan",
    "Immunization",
    "ServiceRequest",
  ];
}

// Types confirmed unreachable via COS: print a SKIP line and move on.
// Update this set based on your own CapabilityStatement output.
const SKIP_TYPES = new Set([
  // Gateway blocks all patient-reference search combos ("not-supported"):
  "MedicationRequest",
  "MedicationDispense",
  "DiagnosticReport",
  "Task",
  // Not in server CapabilityStatement (404 "Unknown resource type"):
  "Condition",
  "AllergyIntolerance",
  "DocumentReference",
]);

// Resource types where GET with _sid-injected params fails but POST (no _sid
// in body) succeeds. An entry with [{}] means no extra params — just force the
// GET→POST fallback path for that type.
const EXTRA_REQUIRED_PARAMS: Map<string, Record<string, string>[]> = new Map([
  // Encounter: GET fails with "Invalid search criteria" due to _sid injection;
  // POST with just the patient reference in the body works.
  ["Encounter", [{}]],
]);

// Resource types that do NOT require a patient reference for searching
const STANDALONE_TYPES = new Set(["Patient", "Appointment", "Slot", "HealthcareService"]);

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

// ── FHIR search (GET) ────────────────────────────────────────────────────────

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

// ── FHIR _search (POST) ───────────────────────────────────────────────────────
// The COS APIM gateway injects _sid into GET query params, which causes the
// HAPI backend to reject searches with unknown param combinations. POST body
// params are not touched by the gateway, so the backend sees only our params.

async function fhirPost(resourceType: string, params: Record<string, string>): Promise<FhirBundle> {
  const token = await getToken();
  const url = `${cfg.fhirBaseUrl.replace(/\/$/, "")}/${resourceType}/_search`;
  const body = new URLSearchParams(params);

  const res = await fetch(url, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Ocp-Apim-Subscription-Key": cfg.apiKey,
      "Content-Type": "application/x-www-form-urlencoded",
      Accept: "application/fhir+json",
    },
    body: body.toString(),
  });

  if (!res.ok) throw new Error(`POST ${resourceType}/_search failed (${res.status}): ${await res.text()}`);
  return res.json() as Promise<FhirBundle>;
}

// ── Fetch with pagination ─────────────────────────────────────────────────────

async function collectPages(bundle: FhirBundle, token: () => Promise<string>, apiKey: string, limit: number): Promise<FhirResource[]> {
  const results: FhirResource[] = [];
  for (const e of bundle.entry ?? []) results.push(e.resource);

  const nextUrl = bundle.link?.find(l => l.relation === "next")?.url;
  if (nextUrl && results.length < limit) {
    try {
      const t = await token();
      const res = await fetch(nextUrl, {
        headers: {
          Authorization: `Bearer ${t}`,
          "Ocp-Apim-Subscription-Key": apiKey,
          Accept: "application/fhir+json",
        },
      });
      if (res.ok) {
        const page2 = await res.json() as FhirBundle;
        for (const e of page2.entry ?? []) results.push(e.resource);
      }
    } catch { /* ignore pagination errors */ }
  }

  return results.slice(0, limit);
}

async function fetchResources(
  resourceType: string,
  params: Record<string, string> = {}
): Promise<FhirResource[]> {
  // COS rejects _count; omit it and rely on server's default page size.
  const bundle = await fhirGet(resourceType, params);
  return collectPages(bundle, getToken, cfg.apiKey, cfg.countPerType);
}

async function fetchResourcesPost(
  resourceType: string,
  params: Record<string, string>
): Promise<FhirResource[]> {
  const bundle = await fhirPost(resourceType, params);
  return collectPages(bundle, getToken, cfg.apiKey, cfg.countPerType);
}

// ── Server capability discovery ───────────────────────────────────────────────
// Fetches the FHIR CapabilityStatement (/metadata) to find which search params
// each resource type actually supports. Results are cached for the run.

type CapabilitySearchParam = { name: string; type: string };
let _capabilityCache: Map<string, CapabilitySearchParam[]> | null = null;

async function getCapability(): Promise<Map<string, CapabilitySearchParam[]>> {
  if (_capabilityCache) return _capabilityCache;
  _capabilityCache = new Map();
  try {
    const token = await getToken();
    const url = `${cfg.fhirBaseUrl.replace(/\/$/, "")}/metadata`;
    const res = await fetch(url, {
      headers: {
        Authorization: `Bearer ${token}`,
        "Ocp-Apim-Subscription-Key": cfg.apiKey,
        Accept: "application/fhir+json",
      },
    });
    if (!res.ok) return _capabilityCache;
    const cs = await res.json() as {
      rest?: Array<{
        resource?: Array<{ type: string; searchParam?: CapabilitySearchParam[] }>;
      }>;
    };
    for (const rest of cs.rest ?? []) {
      for (const resource of rest.resource ?? []) {
        _capabilityCache.set(resource.type, resource.searchParam ?? []);
      }
    }
  } catch { /* silently ignore; fall back to heuristic param sets */ }
  return _capabilityCache;
}

// ── Fetch patient-linked resources ───────────────────────────────────────────
// Builds the param set from CapabilityStatement search params, then tries each
// patient-reference param that the server advertises. Falls back to a default
// set when the CapabilityStatement is unavailable.

async function fetchPatientLinked(
  patientId: string,
  pnr: string | undefined,
  resourceType: string
): Promise<FhirResource[]> {
  const COS_PNR_SYSTEM = "urn:oid:1.2.752.129.2.1.3.1";
  const capability = await getCapability();
  const supportedParams = capability.get(resourceType)?.map(p => p.name) ?? [];

  // Build candidate param sets from capability first, then defaults as fallback.
  const refCandidates = supportedParams.length > 0
    ? supportedParams.filter(n => n === "patient" || n === "subject" ||
        n.startsWith("patient.") || n.startsWith("subject."))
    : ["patient", "subject"];

  const patientRefParams: Record<string, string>[] = [];
  for (const name of refCandidates) {
    if (name === "patient") {
      patientRefParams.push({ patient: `Patient/${patientId}` });
      // Also try chained identifier — COS may only accept the chained form
      // (evidence from run-1: MedicationRequest expected "subject.identifier")
      if (pnr) patientRefParams.push({ "patient.identifier": `${COS_PNR_SYSTEM}|${pnr}` });
    } else if (name === "subject") {
      patientRefParams.push({ subject: `Patient/${patientId}` });
      if (pnr) patientRefParams.push({ "subject.identifier": `${COS_PNR_SYSTEM}|${pnr}` });
    } else if ((name === "subject.identifier" || name === "patient.identifier") && pnr) {
      patientRefParams.push({ [name]: `${COS_PNR_SYSTEM}|${pnr}` });
    }
  }

  // Treat these error patterns as "try next param combination" rather than fatal.
  // "Invalid search criteria" (400) is thrown when _sid injection pollutes the
  // GET query string; the same params in a POST body (no _sid) may succeed.
  const isRetryable = (msg: string) =>
    msg.includes("not-supported") ||
    msg.includes("not know how to handle") ||
    msg.includes("Invalid search criteria") ||
    msg.includes("Invalid/Unsupported Search parameters");

  // Types in EXTRA_REQUIRED_PARAMS always go through GET→POST fallback.
  // An empty extra-params object {} means: just force that fallback for the type.
  const extraParamSets = EXTRA_REQUIRED_PARAMS.get(resourceType);
  if (extraParamSets) {
    const combined: FhirResource[] = [];
    for (const extra of extraParamSets) {
      let fetched = false;
      for (const refParams of patientRefParams) {
        const params = { ...refParams, ...extra };
        try {
          const resources = await fetchResources(resourceType, params);
          combined.push(...resources);
          fetched = true;
          break;
        } catch (err: unknown) {
          const msg = (err as Error).message;
          if (isRetryable(msg)) continue;
          // Unexpected error: try POST before moving to next refParams
          try {
            const resources = await fetchResourcesPost(resourceType, params);
            combined.push(...resources);
            fetched = true;
            break;
          } catch (postErr: unknown) {
            const pmsg = (postErr as Error).message;
            if (isRetryable(pmsg)) continue;
            // Still failing — continue to next refParams rather than aborting
            continue;
          }
        }
      }
      if (!fetched) {
        const label = Object.keys(extra).length > 0 ? JSON.stringify(extra) : "plain patient ref";
        process.stdout.write(`(no results for ${label}) `);
      }
    }
    return combined;
  }

  const isNotSupported = isRetryable;  // alias for the phases below

  const lastErrors: string[] = [];

  // Phase 1: try GET with each param set
  for (const params of patientRefParams) {
    try {
      return await fetchResources(resourceType, params);
    } catch (err: unknown) {
      const msg = (err as Error).message;
      if (isNotSupported(msg)) { lastErrors.push(`GET ${JSON.stringify(params)}: ${msg.split("\n")[0]}`); continue; }
      throw err;
    }
  }

  // Phase 2: try POST _search with each param set (gateway doesn't inject _sid into POST body)
  for (const params of patientRefParams) {
    try {
      return await fetchResourcesPost(resourceType, params);
    } catch (err: unknown) {
      const msg = (err as Error).message;
      if (isNotSupported(msg)) { lastErrors.push(`POST ${JSON.stringify(params)}: ${msg.split("\n")[0]}`); continue; }
      throw err;
    }
  }

  throw new Error(`No supported patient search param found for ${resourceType}. Tried:\n    ${lastErrors.join("\n    ")}`);
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

  // ── Step 0: discover server capabilities ──────────────────────────────────

  process.stdout.write("Fetching server CapabilityStatement ... ");
  const capability = await getCapability();
  if (capability.size > 0) {
    console.log(`${capability.size} resource types found\n`);
    for (const rt of cfg.resourceTypes) {
      const params = capability.get(rt);
      if (params) {
        const refs = params.filter(p =>
          p.name === "patient" || p.name === "subject" ||
          p.name.startsWith("patient.") || p.name.startsWith("subject.")
        ).map(p => p.name);
        console.log(`  ${rt}: patient-ref params = [${refs.join(", ") || "none"}]`);
      } else {
        console.log(`  ${rt}: not in CapabilityStatement`);
      }
    }
  } else {
    console.log("unavailable (will use defaults)\n");
  }
  console.log("");

  // ── Step 1: resolve patient FHIR IDs ──────────────────────────────────────

  // Map fhirId → pnr so we can use pnr-based search params as a fallback.
  const patientRecords: Array<{ fhirId: string; pnr?: string }> = [
    ...cfg.patientIds.map(id => ({ fhirId: id })),
  ];

  // If specific identifiers or IDs were given, look those up.
  // Otherwise, fetch up to countPerType patients from a plain listing.
  if (cfg.patientIdentifiers.length > 0) {
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
        for (const id of ids) {
          if (!patientRecords.some(p => p.fhirId === id)) {
            patientRecords.push({ fhirId: id, pnr });
          }
        }
        console.log(`found ${ids.length}: ${ids.join(", ") || "(none)"}`);
      } catch (err: unknown) {
        console.warn(`WARN: ${(err as Error).message}`);
      }
    }
  } else if (cfg.patientIds.length === 0) {
    // The COS sandbox exposes exactly 5 fixed test patients and provides no
    // bulk listing endpoint. Use the known personnummer as the default set.
    // Source: https://developer.openservices.cambio.se/test-data
    const COS_SANDBOX_PATIENTS = [
      "194609073277", // Richard Lindeskog
      "198001072381", // Bianca Fredriksson
      "194902142696", // Lars Björk
      "197702202396", // Kim Sundström
      "202103172389", // Leah Nordberg (child)
    ];
    const pnrsToFetch = COS_SANDBOX_PATIENTS.slice(0, cfg.countPerType);
    console.log(`using ${pnrsToFetch.length} known COS sandbox patients`);
    const COS_PNR_SYSTEM = "urn:oid:1.2.752.129.2.1.3.1";
    for (const pnr of pnrsToFetch) {
      process.stdout.write(`  Looking up ${pnr} ... `);
      try {
        const bundle = await fhirGet("Patient", { identifier: `${COS_PNR_SYSTEM}|${pnr}` });
        const ids = (bundle.entry ?? []).map(e => e.resource.id).filter(Boolean) as string[];
        for (const id of ids) {
          if (!patientRecords.some(p => p.fhirId === id)) {
            patientRecords.push({ fhirId: id, pnr });
          }
        }
        console.log(ids.length > 0 ? `found ${ids.join(", ")}` : "not found");
      } catch (err: unknown) {
        console.warn(`WARN: ${(err as Error).message}`);
      }
    }
  }

  if (patientRecords.length === 0) {
    console.warn("\nNo patients found. Patient-linked resources will be skipped.\n");
  } else {
    console.log(`\nPatient IDs: ${patientRecords.map(p => p.fhirId).join(", ")}\n`);
  }

  // ── Step 2: fetch resources per type ─────────────────────────────────────

  const collected: Record<string, FhirResource[]> = {};
  for (const rt of cfg.resourceTypes) collected[rt] = [];

  for (const rt of cfg.resourceTypes) {
    const isStandalone = STANDALONE_TYPES.has(rt);

    if (SKIP_TYPES.has(rt)) {
      console.log(`  ${rt} ... SKIP (not reachable via COS open FHIR — see SKIP_TYPES in extract.ts)`);
      continue;
    }

    if (rt === "Patient") {
      // COS does not support listing Patient; read each by direct GET /Patient/{id}.
      for (const { fhirId } of patientRecords) {
        process.stdout.write(`  Patient/${fhirId} ... `);
        try {
          const token = await getToken();
          const url = `${cfg.fhirBaseUrl.replace(/\/$/, "")}/Patient/${fhirId}`;
          const res = await fetch(url, {
            headers: {
              Authorization: `Bearer ${token}`,
              "Ocp-Apim-Subscription-Key": cfg.apiKey,
              Accept: "application/fhir+json",
            },
          });
          if (res.ok) {
            collected[rt].push(await res.json() as FhirResource);
            console.log("found");
          } else {
            console.warn(`WARN: ${res.status}`);
          }
        } catch (err: unknown) {
          console.warn(`WARN: ${(err as Error).message}`);
        }
      }
    } else if (!isStandalone && patientRecords.length > 0) {
      for (const { fhirId, pnr } of patientRecords) {
        process.stdout.write(`  ${rt} for Patient/${fhirId} ... `);
        try {
          const resources = await fetchPatientLinked(fhirId, pnr, rt);
          collected[rt].push(...resources);
          console.log(`${resources.length} found`);
        } catch (err: unknown) {
          console.warn(`WARN: ${(err as Error).message}`);
        }
      }
    } else if (isStandalone && patientRecords.length === 0) {
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
