/**
 * COS → HAPI FHIR data extractor.
 *
 * Strategy for patient-linked resources:
 *   1. FHIR compartment search: GET /Patient/{id}/{ResourceType}
 *      - No code/status params needed → bypasses Observation "codes cannot be null"
 *      - No subject/patient param → bypasses Encounter _sid injection issue
 *   2. If compartment is unsupported (404 / not-supported), fall back to
 *      regular search with ref params (+LOINC code groups for Observation).
 *
 * Auth model (COS Quick Start v1.7):
 *   Token:  POST with Basic auth (base64 clientId:clientSecret)
 *   FHIR:   Bearer token + Ocp-Apim-Subscription-Key header
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
  fhirBaseUrl:        required("COS_FHIR_BASE_URL"),
  tokenUrl:           required("COS_TOKEN_URL"),
  clientId:           required("COS_CLIENT_ID"),
  clientSecret:       required("COS_CLIENT_SECRET"),
  apiKey:             required("COS_API_KEY"),
  scope:              process.env.COS_SCOPE ?? "user/*.read user/*.write",
  outputDir:          resolve(__dir, process.env.EXTRACT_OUTPUT_DIR ?? "../data"),
  patientIdentifiers: csv(process.env.EXTRACT_PATIENT_IDENTIFIERS),
  patientIds:         csv(process.env.EXTRACT_PATIENT_IDS),
  resourceTypes:      csv(process.env.EXTRACT_RESOURCE_TYPES) || defaultResourceTypes(),
  countPerType:       parseInt(process.env.EXTRACT_COUNT_PER_TYPE ?? "50", 10),
};

function csv(s: string | undefined): string[] {
  return (s ?? "").split(",").map(v => v.trim()).filter(Boolean);
}

function defaultResourceTypes(): string[] {
  // Encounter re-enabled: compartment search bypasses _sid injection issue.
  // Observation: compartment search bypasses mandatory code + SNOMED-map bug.
  return ["Patient", "Observation", "Encounter", "CarePlan", "Immunization", "ServiceRequest"];
}

// ── Skip list ───────────────────────────────────────────────────────────────

const SKIP_TYPES = new Set([
  // Gateway blocks patient-reference search and compartment returns nothing:
  "MedicationRequest", "MedicationDispense", "DiagnosticReport", "Task",
  // Backend search unsupported + compartment also not listed:
  "ClinicalImpression",
  // Not in CapabilityStatement:
  "Condition", "AllergyIntolerance", "DocumentReference",
]);

// ── LOINC code groups (fallback for Observation if compartment fails) ────────────
//
// COS requires code param AND the system prefix to avoid a SNOMED-map 500.
// Used only if compartment search is unsupported or returns nothing.

const LOINC = "http://loinc.org";
const loinc = (...codes: string[]) => codes.map(c => `${LOINC}|${c}`).join(",");

const OBSERVATION_LOINC_GROUPS = [
  loinc("20150-9", "19926-5", "19868-9", "40445-0"),           // spirometry
  loinc("39156-5", "29463-7", "8302-2"),                        // BMI, weight, height
  loinc("72166-2", "89919-2", "55284-4", "8867-4"),             // smoking, CAT, BP, HR
  loinc("59408-5", "2339-0", "4548-4", "33914-3"),              // SpO2, glucose, HbA1c, eGFR
  loinc("2160-0", "2951-2", "6298-4", "718-7", "6690-2", "777-3"), // creatinine, Na, K, Hb, WBC, plt
];

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
    headers: { Authorization: `Basic ${credentials}`, "Content-Type": "application/x-www-form-urlencoded" },
    body: body.toString(),
  });
  if (!res.ok) throw new Error(`COS auth failed (${res.status}): ${await res.text()}`);
  const data = await res.json() as { access_token: string; expires_in: number };
  _token = data.access_token;
  _tokenExpiry = Date.now() + (data.expires_in - 30) * 1000;
  return _token;
}

// ── FHIR types ────────────────────────────────────────────────────────────────

type FhirResource = Record<string, unknown> & { resourceType: string; id?: string };
type FhirBundle = {
  resourceType: string;
  entry?: Array<{ resource: FhirResource }>;
  link?: Array<{ relation: string; url: string }>;
};

// ── HTTP helpers ─────────────────────────────────────────────────────────────

function headers(token: string): Record<string, string> {
  return {
    Authorization: `Bearer ${token}`,
    "Ocp-Apim-Subscription-Key": cfg.apiKey,
    Accept: "application/fhir+json",
  };
}

async function fhirGet(path: string, params?: Record<string, string>): Promise<FhirBundle> {
  const token = await getToken();
  const url = new URL(`${cfg.fhirBaseUrl.replace(/\/$/, "")}/${path.replace(/^\//, "")}`);
  if (params) for (const [k, v] of Object.entries(params)) url.searchParams.set(k, v);
  const res = await fetch(url.toString(), { headers: headers(token) });
  if (!res.ok) throw new Error(`GET ${path} failed (${res.status}): ${await res.text()}`);
  return res.json() as Promise<FhirBundle>;
}

async function fhirPost(resourceType: string, params: Record<string, string>): Promise<FhirBundle> {
  const token = await getToken();
  const url = `${cfg.fhirBaseUrl.replace(/\/$/, "")}/${resourceType}/_search`;
  const res = await fetch(url, {
    method: "POST",
    headers: { ...headers(token), "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams(params).toString(),
  });
  if (!res.ok) throw new Error(`POST ${resourceType}/_search failed (${res.status}): ${await res.text()}`);
  return res.json() as Promise<FhirBundle>;
}

async function collectPages(first: FhirBundle, limit: number): Promise<FhirResource[]> {
  const results: FhirResource[] = (first.entry ?? []).map(e => e.resource);
  const nextUrl = first.link?.find(l => l.relation === "next")?.url;
  if (nextUrl && results.length < limit) {
    try {
      const res = await fetch(nextUrl, { headers: headers(await getToken()) });
      if (res.ok) results.push(...((await res.json() as FhirBundle).entry ?? []).map(e => e.resource));
    } catch { /* stop */ }
  }
  return results.slice(0, limit);
}

async function fetchByGet(path: string, params: Record<string, string> = {}): Promise<FhirResource[]> {
  return collectPages(await fhirGet(path, params), cfg.countPerType);
}

async function fetchByPost(resourceType: string, params: Record<string, string>): Promise<FhirResource[]> {
  return collectPages(await fhirPost(resourceType, params), cfg.countPerType);
}

// ── CapabilityStatement ───────────────────────────────────────────────────────

type CapSearchParam = { name: string; type: string };
let _capCache: Map<string, CapSearchParam[]> | null = null;

async function getCapability(): Promise<Map<string, CapSearchParam[]>> {
  if (_capCache) return _capCache;
  _capCache = new Map();
  try {
    const token = await getToken();
    const res = await fetch(`${cfg.fhirBaseUrl.replace(/\/$/, "")}/metadata`, { headers: headers(token) });
    if (!res.ok) return _capCache;
    const cs = await res.json() as {
      rest?: Array<{ resource?: Array<{ type: string; searchParam?: CapSearchParam[] }> }>;
    };
    for (const rest of cs.rest ?? [])
      for (const r of rest.resource ?? [])
        _capCache.set(r.type, r.searchParam ?? []);
  } catch { /* ignore */ }
  return _capCache;
}

// ── Fetch helpers ────────────────────────────────────────────────────────────

const COS_PNR_SYSTEM = "urn:oid:1.2.752.129.2.1.3.1";

function isRetryable(msg: string): boolean {
  return (
    msg.includes("not-supported") ||
    msg.includes("not know how to handle") ||
    msg.includes("Invalid search criteria") ||
    msg.includes("Invalid/Unsupported Search parameters") ||
    msg.includes("HAPI-0302") ||
    // COS 500: internal SNOMED-map failure when using bare LOINC codes.
    // Try the next code group rather than aborting.
    msg.includes("Code translations are not found")
  );
}

function isCompartmentUnsupported(msg: string): boolean {
  return (
    msg.includes("404") ||
    msg.includes("not found") ||
    msg.includes("not-supported") ||
    msg.includes("not know how to handle") ||
    msg.includes("Unknown resource type") ||
    msg.includes("Compartment")
  );
}

// PRIMARY: FHIR compartment search GET /Patient/{id}/{ResourceType}
// Bypasses _sid param injection (no search params → COS gateway has nothing to
// append to) and the Observation mandatory-code restriction.
async function fetchCompartment(
  patientId: string,
  resourceType: string
): Promise<FhirResource[] | null> {
  try {
    const results = await fetchByGet(`Patient/${patientId}/${resourceType}`);
    return results; // may be empty array, that's fine
  } catch (err: unknown) {
    if (isCompartmentUnsupported((err as Error).message)) return null; // fall through
    throw err;
  }
}

async function fetchPatientLinked(
  patientId: string,
  pnr: string | undefined,
  resourceType: string
): Promise<FhirResource[]> {
  // ── Strategy 1: compartment search ────────────────────────────────────────
  const compartmentResults = await fetchCompartment(patientId, resourceType);
  if (compartmentResults !== null) {
    // Compartment worked (even if empty). Don't double-fetch with regular search.
    return compartmentResults;
  }

  // ── Strategy 2: regular search with ref params ─────────────────────────
  const capability = await getCapability();
  const supportedNames = capability.get(resourceType)?.map(p => p.name) ?? [];

  const refCandidates = supportedNames.length > 0
    ? supportedNames.filter(n =>
        n === "patient" || n === "subject" ||
        n.startsWith("patient.") || n.startsWith("subject."))
    : ["patient", "subject"];

  const refParamSets: Record<string, string>[] = [];
  for (const name of refCandidates) {
    if (name === "patient") {
      refParamSets.push({ patient: `Patient/${patientId}` });
      if (pnr) refParamSets.push({ "patient.identifier": `${COS_PNR_SYSTEM}|${pnr}` });
    } else if (name === "subject") {
      refParamSets.push({ subject: `Patient/${patientId}` });
      if (pnr) refParamSets.push({ "subject.identifier": `${COS_PNR_SYSTEM}|${pnr}` });
    } else if ((name === "patient.identifier" || name === "subject.identifier") && pnr) {
      refParamSets.push({ [name]: `${COS_PNR_SYSTEM}|${pnr}` });
    }
  }

  // Observation fallback: try each LOINC code group
  if (resourceType === "Observation") {
    const combined: FhirResource[] = [];
    for (const codes of OBSERVATION_LOINC_GROUPS) {
      for (const refParams of refParamSets) {
        try {
          combined.push(...await fetchByGet(resourceType, { ...refParams, code: codes }));
          break; // this refParam worked, move to next code group
        } catch (err: unknown) {
          const msg = (err as Error).message;
          if (isRetryable(msg)) continue;
          throw err;
        }
      }
    }
    return combined;
  }

  // Standard: try GET then POST for each ref param
  const errors: string[] = [];
  for (const refParams of refParamSets) {
    try { return await fetchByGet(resourceType, refParams); }
    catch (err: unknown) {
      const msg = (err as Error).message;
      errors.push(`GET: ${msg.split("\n")[0]}`);
      if (!isRetryable(msg)) throw err;
    }
  }
  for (const refParams of refParamSets) {
    try { return await fetchByPost(resourceType, refParams); }
    catch (err: unknown) {
      const msg = (err as Error).message;
      errors.push(`POST: ${msg.split("\n")[0]}`);
      if (!isRetryable(msg)) throw err;
    }
  }
  throw new Error(`All search strategies failed for ${resourceType}:\n  ` + errors.join("\n  "));
}

// ── Helpers ───────────────────────────────────────────────────────────────────

function cleanResource(r: FhirResource): FhirResource {
  if (!r.meta) return r;
  const { lastUpdated, versionId, source, ...rest } = r.meta as Record<string, unknown>;
  return { ...r, meta: Object.keys(rest).length > 0 ? rest : undefined };
}

function transactionBundle(resources: FhirResource[]): object {
  return {
    resourceType: "Bundle",
    type: "transaction",
    entry: resources.map(r => ({
      resource: r,
      request: { method: r.id ? "PUT" : "POST", url: r.id ? `${r.resourceType}/${r.id}` : r.resourceType },
    })),
  };
}

function dedup(resources: FhirResource[]): FhirResource[] {
  const seen = new Set<string>();
  return resources.filter(r => { if (!r.id) return true; if (seen.has(r.id)) return false; seen.add(r.id); return true; });
}

// ── Main ─────────────────────────────────────────────────────────────────────

async function main() {
  console.log("COS → HAPI FHIR extractor");
  console.log("==========================\n");
  console.log(`Output dir:     ${cfg.outputDir}`);
  console.log(`Resource types: ${cfg.resourceTypes.join(", ")}`);
  console.log(`Max per type:   ${cfg.countPerType}\n`);

  mkdirSync(cfg.outputDir, { recursive: true });

  // Step 0: capabilities
  process.stdout.write("Fetching server CapabilityStatement ... ");
  const capability = await getCapability();
  console.log(capability.size > 0 ? `${capability.size} resource types found\n` : "unavailable\n");
  if (capability.size > 0) {
    for (const rt of cfg.resourceTypes) {
      const refs = (capability.get(rt) ?? []).filter(p =>
        p.name === "patient" || p.name === "subject" ||
        p.name.startsWith("patient.") || p.name.startsWith("subject.")
      ).map(p => p.name);
      console.log(`  ${rt}: [${refs.join(", ") || "no patient-ref params"}]`);
    }
    console.log("");
  }

  // Step 1: resolve patients
  const patientRecords: Array<{ fhirId: string; pnr?: string }> = [
    ...cfg.patientIds.map(id => ({ fhirId: id })),
  ];

  if (cfg.patientIdentifiers.length > 0) {
    for (const ident of cfg.patientIdentifiers) {
      const pnr = ident.replace(/[-+\s]/g, "");
      process.stdout.write(`Looking up patient ${pnr} ... `);
      try {
        let bundle = await fhirGet("Patient", { identifier: `${COS_PNR_SYSTEM}|${pnr}` });
        if ((bundle.entry ?? []).length === 0) bundle = await fhirGet("Patient", { identifier: pnr });
        const ids = (bundle.entry ?? []).map(e => e.resource.id).filter(Boolean) as string[];
        for (const id of ids) if (!patientRecords.some(p => p.fhirId === id)) patientRecords.push({ fhirId: id, pnr });
        console.log(`found ${ids.length}: ${ids.join(", ") || "(none)"}`);
      } catch (err: unknown) { console.warn(`WARN: ${(err as Error).message}`); }
    }
  } else if (cfg.patientIds.length === 0) {
    const COS_SANDBOX_PATIENTS = [
      "194609073277", "198001072381", "194902142696", "197702202396", "202103172389",
    ];
    console.log(`using ${COS_SANDBOX_PATIENTS.length} known COS sandbox patients`);
    for (const pnr of COS_SANDBOX_PATIENTS) {
      process.stdout.write(`  Looking up ${pnr} ... `);
      try {
        const bundle = await fhirGet("Patient", { identifier: `${COS_PNR_SYSTEM}|${pnr}` });
        const ids = (bundle.entry ?? []).map(e => e.resource.id).filter(Boolean) as string[];
        for (const id of ids) if (!patientRecords.some(p => p.fhirId === id)) patientRecords.push({ fhirId: id, pnr });
        console.log(ids.length > 0 ? `found ${ids.join(", ")}` : "not found");
      } catch (err: unknown) { console.warn(`WARN: ${(err as Error).message}`); }
    }
  }

  if (patientRecords.length === 0)
    console.warn("\nNo patients resolved. Patient-linked resources will be skipped.\n");
  else
    console.log(`\nPatient IDs: ${patientRecords.map(p => p.fhirId).join(", ")}\n`);

  // Step 2: fetch resources
  const collected: Record<string, FhirResource[]> = {};
  for (const rt of cfg.resourceTypes) collected[rt] = [];

  for (const rt of cfg.resourceTypes) {
    if (SKIP_TYPES.has(rt)) { console.log(`  ${rt} ... SKIP`); continue; }

    if (rt === "Patient") {
      for (const { fhirId } of patientRecords) {
        process.stdout.write(`  Patient/${fhirId} ... `);
        try {
          const res = await fetch(
            `${cfg.fhirBaseUrl.replace(/\/$/, "")}/Patient/${fhirId}`,
            { headers: headers(await getToken()) }
          );
          if (res.ok) { collected[rt].push(await res.json() as FhirResource); console.log("found"); }
          else console.warn(`WARN: ${res.status}`);
        } catch (err: unknown) { console.warn(`WARN: ${(err as Error).message}`); }
      }
    } else if (!STANDALONE_TYPES.has(rt) && patientRecords.length > 0) {
      for (const { fhirId, pnr } of patientRecords) {
        process.stdout.write(`  ${rt} for Patient/${fhirId} ... `);
        try {
          const resources = await fetchPatientLinked(fhirId, pnr, rt);
          collected[rt].push(...resources);
          console.log(`${resources.length} found`);
        } catch (err: unknown) { console.warn(`WARN: ${(err as Error).message}`); }
      }
    } else if (STANDALONE_TYPES.has(rt)) {
      process.stdout.write(`  ${rt} ... `);
      try {
        const resources = await fetchByGet(rt);
        collected[rt].push(...resources);
        console.log(`${resources.length} found`);
      } catch (err: unknown) { console.warn(`WARN: ${(err as Error).message}`); }
    }

    collected[rt] = dedup(collected[rt]);
  }

  // Step 3: write bundles
  console.log("");
  let totalFiles = 0, totalResources = 0;
  for (const [rt, resources] of Object.entries(collected)) {
    if (resources.length === 0) continue;
    const file = `${cfg.outputDir}/${rt.toLowerCase()}.json`;
    writeFileSync(file, JSON.stringify(transactionBundle(resources.map(cleanResource)), null, 2), "utf-8");
    console.log(`Wrote ${rt.toLowerCase()}.json  (${resources.length} resources)`);
    totalFiles++; totalResources += resources.length;
  }

  console.log(`\n✓ ${totalResources} resources → ${totalFiles} bundle files in ${cfg.outputDir}`);
  console.log("\nNext steps:\n  1. cd ..\n  2. bash start.sh\n  3. Open http://localhost:3000");
}

main().catch(err => { console.error("\nFatal:", (err as Error).message); process.exit(1); });
