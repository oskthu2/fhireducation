/**
 * COS → HAPI FHIR data extractor.
 *
 * Fetch strategy per resource type:
 *   Patient    – GET /Patient (list) or GET /Patient/{id} per known patient
 *   Observation – individual LOINC codes + status=final (same as coin-demo)
 *                 compartment returns 0 on COS — skip it for Observation
 *   Others     – compartment GET /Patient/{id}/{Type} first;
 *                 fall back to ref-param search if compartment unsupported
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
  return ["Patient", "Observation", "CarePlan", "Immunization", "ServiceRequest"];
}

// ── Skip list ───────────────────────────────────────────────────────────────

const SKIP_TYPES = new Set([
  "MedicationRequest", "MedicationDispense", "DiagnosticReport", "Task",
  "ClinicalImpression",
  // Encounter: _sid injection + no working search param combo found.
  // Compartment GET /Patient/{id}/Encounter also fails on COS.
  "Encounter",
  "Condition", "AllergyIntolerance", "DocumentReference",
]);

// ── Observation LOINC codes ───────────────────────────────────────────────────
//
// Sent one at a time with status=final, exactly as coin-demo does.
// Codes that trigger COS’s internal SNOMED-map 500 are skipped automatically.

const OBSERVATION_LOINC_CODES = [
  // Spirometry
  "20150-9",  // FEV1 measured
  "19926-5",  // FEV1 % predicted
  "19868-9",  // FVC measured
  "40445-0",  // FEV1/FVC ratio
  // Vitals
  "39156-5",  // BMI
  "29463-7",  // Body weight
  "8302-2",   // Body height
  "55284-4",  // Blood pressure
  "8867-4",   // Heart rate
  "59408-5",  // SpO2
  // Clinical scores & status
  "72166-2",  // Smoking status
  "89919-2",  // CAT score
  // Lab
  "2339-0",   // Blood glucose
  "4548-4",   // HbA1c
  "33914-3",  // eGFR
  "2160-0",   // Creatinine
  "2951-2",   // Sodium
  "6298-4",   // Potassium
  "718-7",    // Hemoglobin
  "6690-2",   // Leukocytes
  "777-3",    // Platelets
];

const STANDALONE_TYPES = new Set(["Patient", "Appointment", "Slot", "HealthcareService"]);
const COS_PNR_SYSTEM = "urn:oid:1.2.752.129.2.1.3.1";

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

function hdrs(token: string): Record<string, string> {
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
  const res = await fetch(url.toString(), { headers: hdrs(token) });
  if (!res.ok) throw new Error(`GET ${path} failed (${res.status}): ${await res.text()}`);
  return res.json() as Promise<FhirBundle>;
}

async function fhirPost(resourceType: string, params: Record<string, string>): Promise<FhirBundle> {
  const token = await getToken();
  const url = `${cfg.fhirBaseUrl.replace(/\/$/, "")}/${resourceType}/_search`;
  const res = await fetch(url, {
    method: "POST",
    headers: { ...hdrs(token), "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams(params).toString(),
  });
  if (!res.ok) throw new Error(`POST ${resourceType}/_search failed (${res.status}): ${await res.text()}`);
  return res.json() as Promise<FhirBundle>;
}

async function pages(first: FhirBundle, limit: number): Promise<FhirResource[]> {
  const out: FhirResource[] = (first.entry ?? []).map(e => e.resource);
  const next = first.link?.find(l => l.relation === "next")?.url;
  if (next && out.length < limit) {
    try {
      const res = await fetch(next, { headers: hdrs(await getToken()) });
      if (res.ok) out.push(...((await res.json() as FhirBundle).entry ?? []).map(e => e.resource));
    } catch { /* stop */ }
  }
  return out.slice(0, limit);
}

async function getList(path: string, params?: Record<string, string>): Promise<FhirResource[]> {
  return pages(await fhirGet(path, params), cfg.countPerType);
}

async function postSearch(rt: string, params: Record<string, string>): Promise<FhirResource[]> {
  return pages(await fhirPost(rt, params), cfg.countPerType);
}

// ── CapabilityStatement ───────────────────────────────────────────────────────

type CapParam = { name: string; type: string };
let _cap: Map<string, CapParam[]> | null = null;

async function getCap(): Promise<Map<string, CapParam[]>> {
  if (_cap) return _cap;
  _cap = new Map();
  try {
    const res = await fetch(`${cfg.fhirBaseUrl.replace(/\/$/, "")}/metadata`, { headers: hdrs(await getToken()) });
    if (!res.ok) return _cap;
    const cs = await res.json() as { rest?: Array<{ resource?: Array<{ type: string; searchParam?: CapParam[] }> }> };
    for (const rest of cs.rest ?? [])
      for (const r of rest.resource ?? [])
        _cap.set(r.type, r.searchParam ?? []);
  } catch { /* ignore */ }
  return _cap;
}

// ── Error classification ─────────────────────────────────────────────────────────

function isRetryable(msg: string): boolean {
  return (
    msg.includes("not-supported") ||
    msg.includes("not know how to handle") ||
    msg.includes("Invalid search criteria") ||
    msg.includes("Invalid/Unsupported Search parameters") ||
    msg.includes("HAPI-0302") ||
    // COS 500: SNOMED translation failure — skip this code, try next.
    msg.includes("Code translations are not found")
  );
}

function isCompartmentUnsupported(msg: string): boolean {
  return (
    msg.includes("404") ||
    msg.includes("not found") ||
    msg.includes("not-supported") ||
    msg.includes("not know how to handle") ||
    msg.includes("Invalid search criteria") ||
    msg.includes("Unknown resource type") ||
    msg.includes("Compartment")
  );
}

// ── Patient-linked fetch strategies ──────────────────────────────────────────

async function fetchObservations(
  patientId: string,
): Promise<FhirResource[]> {
  // Fetch one LOINC code at a time with status=final, exactly as coin-demo does.
  // Comma-separated codes trigger a COS internal SNOMED-map 500 on some codes.
  const combined: FhirResource[] = [];
  const skipped: string[] = [];
  const failed: string[] = [];

  for (const code of OBSERVATION_LOINC_CODES) {
    try {
      const results = await getList("Observation", {
        patient: `Patient/${patientId}`,
        code,
        status: "final",
      });
      combined.push(...results);
    } catch (err: unknown) {
      const msg = (err as Error).message;
      if (msg.includes("Code translations are not found")) {
        skipped.push(code);
      } else if (isRetryable(msg)) {
        skipped.push(code);
      } else {
        failed.push(`${code}: ${msg.split("\n")[0]}`);
      }
    }
  }

  if (skipped.length > 0) {
    process.stdout.write(`(${combined.length} found, ${skipped.length} codes skipped by COS) `);
  }
  if (failed.length > 0) {
    console.warn(`\n  WARN unexpected errors for Observation codes: ${failed.join("; ")}`);
  }
  return combined;
}

async function fetchCompartment(patientId: string, resourceType: string): Promise<FhirResource[] | null> {
  try {
    return await getList(`Patient/${patientId}/${resourceType}`);
  } catch (err: unknown) {
    if (isCompartmentUnsupported((err as Error).message)) return null;
    throw err;
  }
}

async function fetchWithRefParams(
  patientId: string,
  pnr: string | undefined,
  resourceType: string,
): Promise<FhirResource[]> {
  const cap = await getCap();
  const supported = cap.get(resourceType)?.map(p => p.name) ?? [];
  const candidates = supported.length > 0
    ? supported.filter(n => n === "patient" || n === "subject" || n.startsWith("patient.") || n.startsWith("subject."))
    : ["patient", "subject"];

  const refSets: Record<string, string>[] = [];
  for (const name of candidates) {
    if (name === "patient") {
      refSets.push({ patient: `Patient/${patientId}` });
      if (pnr) refSets.push({ "patient.identifier": `${COS_PNR_SYSTEM}|${pnr}` });
    } else if (name === "subject") {
      refSets.push({ subject: `Patient/${patientId}` });
      if (pnr) refSets.push({ "subject.identifier": `${COS_PNR_SYSTEM}|${pnr}` });
    } else if ((name === "patient.identifier" || name === "subject.identifier") && pnr) {
      refSets.push({ [name]: `${COS_PNR_SYSTEM}|${pnr}` });
    }
  }

  const errors: string[] = [];
  for (const p of refSets) {
    try { return await getList(resourceType, p); }
    catch (e: unknown) {
      const msg = (e as Error).message;
      errors.push(`GET: ${msg.split("\n")[0]}`);
      if (!isRetryable(msg)) throw e;
    }
  }
  for (const p of refSets) {
    try { return await postSearch(resourceType, p); }
    catch (e: unknown) {
      const msg = (e as Error).message;
      errors.push(`POST: ${msg.split("\n")[0]}`);
      if (!isRetryable(msg)) throw e;
    }
  }
  throw new Error(`All search strategies failed:\n  ` + errors.join("\n  "));
}

async function fetchPatientLinked(
  patientId: string,
  pnr: string | undefined,
  resourceType: string,
): Promise<FhirResource[]> {
  // Observation: individual code search (compartment returns 0 on COS)
  if (resourceType === "Observation") {
    return fetchObservations(patientId);
  }

  // All other types: compartment first, ref-param fallback
  const compartment = await fetchCompartment(patientId, resourceType);
  if (compartment !== null) return compartment;

  return fetchWithRefParams(patientId, pnr, resourceType);
}

// ── Helpers ───────────────────────────────────────────────────────────────────

function cleanResource(r: FhirResource): FhirResource {
  if (!r.meta) return r;
  const { lastUpdated, versionId, source, ...rest } = r.meta as Record<string, unknown>;
  return { ...r, meta: Object.keys(rest).length > 0 ? rest : undefined };
}

function txBundle(resources: FhirResource[]): object {
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
  return resources.filter(r => {
    if (!r.id) return true;
    if (seen.has(r.id)) return false;
    seen.add(r.id); return true;
  });
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
  process.stdout.write("Fetching CapabilityStatement ... ");
  const cap = await getCap();
  console.log(cap.size > 0 ? `${cap.size} types\n` : "unavailable\n");

  // Step 1: resolve patients
  const patients: Array<{ fhirId: string; pnr?: string }> = [
    ...cfg.patientIds.map(id => ({ fhirId: id })),
  ];

  if (cfg.patientIdentifiers.length > 0) {
    // Explicit PNR list
    for (const ident of cfg.patientIdentifiers) {
      const pnr = ident.replace(/[-+\s]/g, "");
      process.stdout.write(`Looking up ${pnr} ... `);
      try {
        let b = await fhirGet("Patient", { identifier: `${COS_PNR_SYSTEM}|${pnr}` });
        if (!(b.entry ?? []).length) b = await fhirGet("Patient", { identifier: pnr });
        const ids = (b.entry ?? []).map(e => e.resource.id).filter(Boolean) as string[];
        ids.forEach(id => { if (!patients.some(p => p.fhirId === id)) patients.push({ fhirId: id, pnr }); });
        console.log(`found ${ids.length}: ${ids.join(", ") || "(none)"}`);
      } catch (e: unknown) { console.warn(`WARN: ${(e as Error).message}`); }
    }
  } else if (cfg.patientIds.length === 0) {
    // Try open patient listing first — COS may support it
    process.stdout.write("Trying GET /Patient (open listing) ... ");
    let discovered = false;
    try {
      const b = await fhirGet("Patient", { _count: String(cfg.countPerType) });
      const ids = (b.entry ?? []).map(e => e.resource.id).filter(Boolean) as string[];
      if (ids.length > 0) {
        console.log(`found ${ids.length} patients`);
        ids.forEach(id => { if (!patients.some(p => p.fhirId === id)) patients.push({ fhirId: id }); });
        discovered = true;
      } else {
        console.log("0 results — falling back to known list");
      }
    } catch { console.log("not supported — falling back to known list"); }

    if (!discovered) {
      // Known COS sandbox patients (developer.openservices.cambio.se/test-data)
      const KNOWN = ["194609073277", "198001072381", "194902142696", "197702202396", "202103172389"];
      console.log(`Looking up ${KNOWN.length} known sandbox patients ...`);
      for (const pnr of KNOWN) {
        process.stdout.write(`  ${pnr} ... `);
        try {
          const b = await fhirGet("Patient", { identifier: `${COS_PNR_SYSTEM}|${pnr}` });
          const ids = (b.entry ?? []).map(e => e.resource.id).filter(Boolean) as string[];
          ids.forEach(id => { if (!patients.some(p => p.fhirId === id)) patients.push({ fhirId: id, pnr }); });
          console.log(ids.length ? `found ${ids.join(", ")}` : "not found");
        } catch (e: unknown) { console.warn(`WARN: ${(e as Error).message}`); }
      }
    }
  }

  if (!patients.length)
    console.warn("\nNo patients resolved — patient-linked resources will be skipped.\n");
  else
    console.log(`\nPatient IDs: ${patients.map(p => p.fhirId).join(", ")}\n`);

  // Step 2: fetch resources
  const collected: Record<string, FhirResource[]> = {};
  for (const rt of cfg.resourceTypes) collected[rt] = [];

  for (const rt of cfg.resourceTypes) {
    if (SKIP_TYPES.has(rt)) { console.log(`  ${rt} ... SKIP`); continue; }

    if (rt === "Patient") {
      for (const { fhirId } of patients) {
        process.stdout.write(`  Patient/${fhirId} ... `);
        try {
          const res = await fetch(`${cfg.fhirBaseUrl.replace(/\/$/, "")}/Patient/${fhirId}`, { headers: hdrs(await getToken()) });
          if (res.ok) { collected[rt].push(await res.json() as FhirResource); console.log("found"); }
          else console.warn(`WARN: ${res.status}`);
        } catch (e: unknown) { console.warn(`WARN: ${(e as Error).message}`); }
      }
    } else if (!STANDALONE_TYPES.has(rt) && patients.length) {
      for (const { fhirId, pnr } of patients) {
        process.stdout.write(`  ${rt} for Patient/${fhirId} ... `);
        try {
          const resources = await fetchPatientLinked(fhirId, pnr, rt);
          collected[rt].push(...resources);
          console.log(`${resources.length} found`);
        } catch (e: unknown) { console.warn(`WARN: ${(e as Error).message}`); }
      }
    } else if (STANDALONE_TYPES.has(rt)) {
      process.stdout.write(`  ${rt} ... `);
      try {
        const r = await getList(rt);
        collected[rt].push(...r);
        console.log(`${r.length} found`);
      } catch (e: unknown) { console.warn(`WARN: ${(e as Error).message}`); }
    }

    collected[rt] = dedup(collected[rt]);
  }

  // Step 3: write
  console.log("");
  let files = 0, total = 0;
  for (const [rt, resources] of Object.entries(collected)) {
    if (!resources.length) continue;
    const file = `${cfg.outputDir}/${rt.toLowerCase()}.json`;
    writeFileSync(file, JSON.stringify(txBundle(resources.map(cleanResource)), null, 2), "utf-8");
    console.log(`Wrote ${rt.toLowerCase()}.json  (${resources.length} resources)`);
    files++; total += resources.length;
  }

  console.log(`\n✓ ${total} resources → ${files} files in ${cfg.outputDir}`);
  console.log("\nNext: cd .. && bash start.sh  →  http://localhost:3000");
}

main().catch(err => { console.error("\nFatal:", (err as Error).message); process.exit(1); });
