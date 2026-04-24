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
  fhirBaseUrl:          required("COS_FHIR_BASE_URL"),
  tokenUrl:             required("COS_TOKEN_URL"),
  clientId:             required("COS_CLIENT_ID"),
  clientSecret:         required("COS_CLIENT_SECRET"),
  apiKey:               required("COS_API_KEY"),
  scope:                process.env.COS_SCOPE ?? "user/*.read user/*.write",
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
  return ["Patient", "Observation", "CarePlan", "Immunization", "ServiceRequest"];
}

// ── Skip list ───────────────────────────────────────────────────────────────

// Resource types confirmed unreachable via COS open FHIR.
const SKIP_TYPES = new Set([
  // Gateway blocks all patient-reference search combos ("not-supported"):
  "MedicationRequest", "MedicationDispense", "DiagnosticReport", "Task",
  // Backend search completely unsupported (all param combinations rejected):
  "ClinicalImpression",
  // COS APIM injects _sid into every request (GET + POST); Encounter backend
  // rejects _sid as an unknown search param → 400 "Invalid search criteria."
  // for every combination tried. No HTTP workaround exists.
  "Encounter",
  // Not in server CapabilityStatement (404 "Unknown resource type"):
  "Condition", "AllergyIntolerance", "DocumentReference",
]);

// ── COS-specific required search params ──────────────────────────────────────
//
// OBSERVATION: COS requires a "code" param — searching without one returns
// 400 "codes cannot be null". The code must include the system prefix
// ("http://loinc.org|CODE"), otherwise COS 500s with "Code translations are
// not found for the code:X and system:http://snomed.info/sct".
// We fetch in pre-defined LOINC groups and merge results.

const LOINC = "http://loinc.org";

function loincGroup(...codes: string[]): string {
  return codes.map(c => `${LOINC}|${c}`).join(",");
}

const OBSERVATION_LOINC_GROUPS: string[] = [
  loincGroup("20150-9", "19926-5", "19868-9", "40445-0"),       // spirometry
  loincGroup("39156-5", "29463-7", "8302-2"),                    // BMI, weight, height
  loincGroup("72166-2", "89919-2", "55284-4", "8867-4"),         // smoking, CAT, BP, HR
  loincGroup("59408-5", "2339-0", "4548-4", "33914-3"),          // SpO2, glucose, HbA1c, eGFR
  loincGroup("2160-0", "2951-2", "6298-4", "718-7", "6690-2", "777-3"), // creatinine, Na, K, Hb, WBC, plt
];

// Extra params required per resource type. Each entry = one separate request;
// the patient/subject reference is merged in automatically.
const REQUIRED_EXTRA_PARAMS: Map<string, Record<string, string>[]> = new Map([
  ["Observation", OBSERVATION_LOINC_GROUPS.map(codes => ({ code: codes }))],
]);

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
  resourceType: "Bundle";
  entry?: Array<{ resource: FhirResource }>;
  link?: Array<{ relation: string; url: string }>;
};

// ── HTTP helpers ─────────────────────────────────────────────────────────────

function authHeaders(token: string): Record<string, string> {
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
  const res = await fetch(url.toString(), { headers: authHeaders(token) });
  if (!res.ok) throw new Error(`GET ${path} failed (${res.status}): ${await res.text()}`);
  return res.json() as Promise<FhirBundle>;
}

async function fhirPost(resourceType: string, params: Record<string, string>): Promise<FhirBundle> {
  const token = await getToken();
  const url = `${cfg.fhirBaseUrl.replace(/\/$/, "")}/${resourceType}/_search`;
  const res = await fetch(url, {
    method: "POST",
    headers: { ...authHeaders(token), "Content-Type": "application/x-www-form-urlencoded" },
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
      const res = await fetch(nextUrl, { headers: authHeaders(await getToken()) });
      if (res.ok) {
        const page2 = await res.json() as FhirBundle;
        results.push(...(page2.entry ?? []).map(e => e.resource));
      }
    } catch { /* stop on error */ }
  }
  return results.slice(0, limit);
}

async function fetchByGet(rt: string, params: Record<string, string> = {}): Promise<FhirResource[]> {
  return collectPages(await fhirGet(rt, params), cfg.countPerType);
}

async function fetchByPost(rt: string, params: Record<string, string>): Promise<FhirResource[]> {
  return collectPages(await fhirPost(rt, params), cfg.countPerType);
}

// ── CapabilityStatement ───────────────────────────────────────────────────────

type CapSearchParam = { name: string; type: string };
let _capCache: Map<string, CapSearchParam[]> | null = null;

async function getCapability(): Promise<Map<string, CapSearchParam[]>> {
  if (_capCache) return _capCache;
  _capCache = new Map();
  try {
    const token = await getToken();
    const res = await fetch(`${cfg.fhirBaseUrl.replace(/\/$/, "")}/metadata`, { headers: authHeaders(token) });
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

// ── Patient-linked fetching ───────────────────────────────────────────────────

const COS_PNR_SYSTEM = "urn:oid:1.2.752.129.2.1.3.1";

function isRetryable(msg: string): boolean {
  return (
    msg.includes("not-supported") ||
    msg.includes("not know how to handle") ||
    msg.includes("Invalid search criteria") ||
    msg.includes("Invalid/Unsupported Search parameters") ||
    msg.includes("HAPI-0302")
  );
}

async function fetchPatientLinked(
  patientId: string,
  pnr: string | undefined,
  resourceType: string
): Promise<FhirResource[]> {
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

  const extraParamSets = REQUIRED_EXTRA_PARAMS.get(resourceType);

  if (extraParamSets) {
    const combined: FhirResource[] = [];
    const groupErrors: string[] = [];

    for (const extra of extraParamSets) {
      const label = Object.entries(extra).map(([k, v]) => `${k}=${v}`).join("&") || "(no extra params)";
      let fetched = false;
      const attemptErrors: string[] = [];

      for (const refParams of refParamSets) {
        const params = { ...refParams, ...extra };
        try {
          combined.push(...await fetchByGet(resourceType, params));
          fetched = true;
          break;
        } catch (err: unknown) {
          const msg = (err as Error).message;
          attemptErrors.push(`GET ${JSON.stringify(params)}: ${msg.split("\n")[0]}`);
          if (!isRetryable(msg)) throw err;
        }
        try {
          combined.push(...await fetchByPost(resourceType, params));
          fetched = true;
          break;
        } catch (err: unknown) {
          const msg = (err as Error).message;
          attemptErrors.push(`POST ${JSON.stringify(params)}: ${msg.split("\n")[0]}`);
          if (!isRetryable(msg)) throw err;
        }
      }

      if (!fetched)
        groupErrors.push(`  [${label}] all attempts failed:\n    ` + attemptErrors.join("\n    "));
    }

    if (combined.length === 0 && groupErrors.length > 0)
      console.warn(`\nWARN: no results for ${resourceType}. Details:\n${groupErrors.join("\n")}`);

    return combined;
  }

  // Standard path: GET then POST fallback
  const lastErrors: string[] = [];
  for (const refParams of refParamSets) {
    try { return await fetchByGet(resourceType, refParams); }
    catch (err: unknown) {
      const msg = (err as Error).message;
      lastErrors.push(`GET ${JSON.stringify(refParams)}: ${msg.split("\n")[0]}`);
      if (!isRetryable(msg)) throw err;
    }
  }
  for (const refParams of refParamSets) {
    try { return await fetchByPost(resourceType, refParams); }
    catch (err: unknown) {
      const msg = (err as Error).message;
      lastErrors.push(`POST ${JSON.stringify(refParams)}: ${msg.split("\n")[0]}`);
      if (!isRetryable(msg)) throw err;
    }
  }
  throw new Error(
    `No supported patient search param for ${resourceType}. Tried:\n    ` +
    lastErrors.join("\n    ")
  );
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
  console.log(`Output dir:     ${cfg.outputDir}`);
  console.log(`Resource types: ${cfg.resourceTypes.join(", ")}`);
  console.log(`Max per type:   ${cfg.countPerType}\n`);

  mkdirSync(cfg.outputDir, { recursive: true });

  // Step 0: capabilities
  process.stdout.write("Fetching server CapabilityStatement ... ");
  const capability = await getCapability();
  if (capability.size > 0) {
    console.log(`${capability.size} resource types found\n`);
    for (const rt of cfg.resourceTypes) {
      const params = capability.get(rt);
      const refs = (params ?? []).filter(p =>
        p.name === "patient" || p.name === "subject" ||
        p.name.startsWith("patient.") || p.name.startsWith("subject.")
      ).map(p => p.name);
      console.log(`  ${rt}: patient-ref params = [${refs.join(", ") || "none"}]`);
    }
  } else {
    console.log("unavailable (will use defaults)");
  }
  console.log("");

  // Step 1: resolve patient FHIR IDs
  const patientRecords: Array<{ fhirId: string; pnr?: string }> = [
    ...cfg.patientIds.map(id => ({ fhirId: id })),
  ];

  if (cfg.patientIdentifiers.length > 0) {
    for (const ident of cfg.patientIdentifiers) {
      const pnr = ident.replace(/[-+\s]/g, "");
      process.stdout.write(`Looking up patient ${pnr} ... `);
      try {
        let bundle = await fhirGet("Patient", { identifier: `${COS_PNR_SYSTEM}|${pnr}` });
        if ((bundle.entry ?? []).length === 0)
          bundle = await fhirGet("Patient", { identifier: pnr });
        const ids = (bundle.entry ?? []).map(e => e.resource.id).filter(Boolean) as string[];
        for (const id of ids)
          if (!patientRecords.some(p => p.fhirId === id)) patientRecords.push({ fhirId: id, pnr });
        console.log(`found ${ids.length}: ${ids.join(", ") || "(none)"}`);
      } catch (err: unknown) {
        console.warn(`WARN: ${(err as Error).message}`);
      }
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
        for (const id of ids)
          if (!patientRecords.some(p => p.fhirId === id)) patientRecords.push({ fhirId: id, pnr });
        console.log(ids.length > 0 ? `found ${ids.join(", ")}` : "not found");
      } catch (err: unknown) {
        console.warn(`WARN: ${(err as Error).message}`);
      }
    }
  }

  if (patientRecords.length === 0)
    console.warn("\nNo patients resolved. Patient-linked resources will be skipped.\n");
  else
    console.log(`\nPatient IDs: ${patientRecords.map(p => p.fhirId).join(", ")}\n`);

  // Step 2: fetch
  const collected: Record<string, FhirResource[]> = {};
  for (const rt of cfg.resourceTypes) collected[rt] = [];

  for (const rt of cfg.resourceTypes) {
    if (SKIP_TYPES.has(rt)) {
      console.log(`  ${rt} ... SKIP (not reachable via COS — see SKIP_TYPES)`);
      continue;
    }

    if (rt === "Patient") {
      for (const { fhirId } of patientRecords) {
        process.stdout.write(`  Patient/${fhirId} ... `);
        try {
          const res = await fetch(
            `${cfg.fhirBaseUrl.replace(/\/$/, "")}/Patient/${fhirId}`,
            { headers: authHeaders(await getToken()) }
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

  // Step 3: write
  console.log("");
  let totalFiles = 0, totalResources = 0;

  for (const [rt, resources] of Object.entries(collected)) {
    if (resources.length === 0) continue;
    const file = `${cfg.outputDir}/${rt.toLowerCase()}.json`;
    writeFileSync(file, JSON.stringify(transactionBundle(resources.map(cleanResource)), null, 2), "utf-8");
    console.log(`Wrote ${rt.toLowerCase()}.json  (${resources.length} resources)`);
    totalFiles++;
    totalResources += resources.length;
  }

  console.log(`\n✓ ${totalResources} resources → ${totalFiles} bundle files in ${cfg.outputDir}`);
  console.log("\nNext steps:");
  console.log("  1. cd ..");
  console.log("  2. bash start.sh");
  console.log("  3. Open http://localhost:3000");
}

main().catch(err => {
  console.error("\nFatal:", (err as Error).message);
  process.exit(1);
});
