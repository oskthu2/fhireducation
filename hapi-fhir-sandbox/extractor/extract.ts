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
    "Patient",
    "Observation",
    "Encounter",
    "CarePlan",
    "Immunization",
    "ServiceRequest",
  ];
}

// Resource types confirmed unreachable via COS open FHIR.
const SKIP_TYPES = new Set([
  // Gateway blocks all patient-reference search combos ("not-supported"):
  "MedicationRequest",
  "MedicationDispense",
  "DiagnosticReport",
  "Task",
  // Backend search completely unsupported (all param combinations rejected):
  "ClinicalImpression",
  // Not in server CapabilityStatement (404 "Unknown resource type"):
  "Condition",
  "AllergyIntolerance",
  "DocumentReference",
]);

// ── COS-specific search constraints ──────────────────────────────────────────
//
// The COS APIM gateway injects an "_sid" session param into every request.
// This causes HAPI to reject searches whose param set is not explicitly
// declared in the CapabilityStatement ("not know how to handle").
//
// OBSERVATION: COS backend requires a "code" param — searching without one
// returns 400 "codes cannot be null". We therefore fetch in pre-defined LOINC
// code groups and merge the results.
//
// ENCOUNTER: COS backend requires "status" alongside "subject". Without it
// the search is rejected. Fetch once per status value and merge.

// LOINC code groups. Each group is fetched as a single comma-separated "code"
// parameter. Add more LOINC codes here to expand coverage.
const OBSERVATION_LOINC_GROUPS: string[] = [
  // Spirometry / lung function
  "20150-9,19926-5,19868-9,40445-0",
  // Vitals: BMI, body weight, body height
  "39156-5,29463-7,8302-2",
  // Smoking status, COPD Assessment Test (CAT), blood pressure, heart rate
  "72166-2,89919-2,55284-4,8867-4",
  // SpO2, blood glucose, HbA1c, eGFR
  "59408-5,2339-0,4548-4,33914-3",
  // Creatinine, Na+, K+, Hb, leukocytes, platelets
  "2160-0,2951-2,6298-4,718-7,6690-2,777-3",
];

// Extra search parameters that MUST be present for a resource type.
// Each entry is tried as a separate request; results are merged.
// The {patient/subject} reference is added automatically by fetchPatientLinked.
const REQUIRED_EXTRA_PARAMS: Map<string, Record<string, string>[]> = new Map([
  [
    "Observation",
    // COS 400 "codes cannot be null" — code is mandatory for Observation search.
    OBSERVATION_LOINC_GROUPS.map(codes => ({ code: codes })),
  ],
  [
    "Encounter",
    // COS requires status alongside subject for Encounter search.
    // Confirmed by fhir-tools.ts in coin-demo (always uses status=finished).
    [
      { status: "finished" },
      { status: "in-progress" },
      { status: "arrived" },
      { status: "planned" },
    ],
  ],
]);

// Resource types that do NOT require a patient reference
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

// ── FHIR types ────────────────────────────────────────────────────────────────

type FhirResource = Record<string, unknown> & { resourceType: string; id?: string };
type FhirBundle  = {
  resourceType: "Bundle";
  entry?: Array<{ resource: FhirResource }>;
  link?: Array<{ relation: string; url: string }>;
};

// ── FHIR GET ─────────────────────────────────────────────────────────────────

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
// The COS APIM gateway injects _sid into GET query strings. When the FHIR
// backend does not list _sid as a supported param for a resource type, it
// rejects the search. POST body params bypass this for some resource types.

async function fhirPost(resourceType: string, params: Record<string, string>): Promise<FhirBundle> {
  const token = await getToken();
  const url = `${cfg.fhirBaseUrl.replace(/\/$/, "")}/${resourceType}/_search`;
  const res = await fetch(url, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Ocp-Apim-Subscription-Key": cfg.apiKey,
      "Content-Type": "application/x-www-form-urlencoded",
      Accept: "application/fhir+json",
    },
    body: new URLSearchParams(params).toString(),
  });
  if (!res.ok) throw new Error(`POST ${resourceType}/_search failed (${res.status}): ${await res.text()}`);
  return res.json() as Promise<FhirBundle>;
}

// ── Pagination ────────────────────────────────────────────────────────────────

async function collectPages(first: FhirBundle, limit: number): Promise<FhirResource[]> {
  const results: FhirResource[] = (first.entry ?? []).map(e => e.resource);
  const nextUrl = first.link?.find(l => l.relation === "next")?.url;
  if (nextUrl && results.length < limit) {
    try {
      const t = await getToken();
      const res = await fetch(nextUrl, {
        headers: {
          Authorization: `Bearer ${t}`,
          "Ocp-Apim-Subscription-Key": cfg.apiKey,
          Accept: "application/fhir+json",
        },
      });
      if (res.ok) {
        const page2 = await res.json() as FhirBundle;
        results.push(...(page2.entry ?? []).map(e => e.resource));
      }
    } catch { /* stop pagination on network error */ }
  }
  return results.slice(0, limit);
}

async function fetchByGet(
  resourceType: string,
  params: Record<string, string>
): Promise<FhirResource[]> {
  const bundle = await fhirGet(resourceType, params);
  return collectPages(bundle, cfg.countPerType);
}

async function fetchByPost(
  resourceType: string,
  params: Record<string, string>
): Promise<FhirResource[]> {
  const bundle = await fhirPost(resourceType, params);
  return collectPages(bundle, cfg.countPerType);
}

// ── CapabilityStatement ───────────────────────────────────────────────────────

type CapSearchParam = { name: string; type: string };
let _capCache: Map<string, CapSearchParam[]> | null = null;

async function getCapability(): Promise<Map<string, CapSearchParam[]>> {
  if (_capCache) return _capCache;
  _capCache = new Map();
  try {
    const token = await getToken();
    const res = await fetch(`${cfg.fhirBaseUrl.replace(/\/$/, "")}/metadata`, {
      headers: {
        Authorization: `Bearer ${token}`,
        "Ocp-Apim-Subscription-Key": cfg.apiKey,
        Accept: "application/fhir+json",
      },
    });
    if (!res.ok) return _capCache;
    const cs = await res.json() as {
      rest?: Array<{ resource?: Array<{ type: string; searchParam?: CapSearchParam[] }> }>;
    };
    for (const rest of cs.rest ?? []) {
      for (const r of rest.resource ?? []) {
        _capCache.set(r.type, r.searchParam ?? []);
      }
    }
  } catch { /* ignore */ }
  return _capCache;
}

// ── Fetch patient-linked resources ───────────────────────────────────────────

const COS_PNR_SYSTEM = "urn:oid:1.2.752.129.2.1.3.1";

// Whether an error message is "try the next param set" vs a hard failure.
function isRetryable(msg: string): boolean {
  return (
    msg.includes("not-supported") ||
    msg.includes("not know how to handle") ||
    msg.includes("Invalid search criteria") ||
    msg.includes("Invalid/Unsupported Search parameters") ||
    msg.includes("HAPI-0302")  // HAPI unknown search param
  );
}

async function fetchPatientLinked(
  patientId: string,
  pnr: string | undefined,
  resourceType: string
): Promise<FhirResource[]> {
  const capability = await getCapability();
  const supportedNames = capability.get(resourceType)?.map(p => p.name) ?? [];

  // Build reference param candidates (direct ID + chained identifier)
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
    // For resource types with required extra params (Observation, Encounter, …)
    // iterate over each extra-params set and attempt GET then POST for each.
    const combined: FhirResource[] = [];
    const groupErrors: string[] = [];

    for (const extra of extraParamSets) {
      const label = Object.keys(extra).length > 0
        ? Object.entries(extra).map(([k, v]) => `${k}=${v}`).join("&")
        : "(no extra params)";
      let fetched = false;
      const attemptErrors: string[] = [];

      for (const refParams of refParamSets) {
        const params = { ...refParams, ...extra };

        // Phase 1: GET
        try {
          const resources = await fetchByGet(resourceType, params);
          combined.push(...resources);
          fetched = true;
          break;
        } catch (err: unknown) {
          const msg = (err as Error).message;
          attemptErrors.push(`GET ${JSON.stringify(params)}: ${msg.split("\n")[0]}`);
          if (!isRetryable(msg)) throw err;
        }

        // Phase 2: POST (gateway may not inject _sid into POST body)
        try {
          const resources = await fetchByPost(resourceType, params);
          combined.push(...resources);
          fetched = true;
          break;
        } catch (err: unknown) {
          const msg = (err as Error).message;
          attemptErrors.push(`POST ${JSON.stringify(params)}: ${msg.split("\n")[0]}`);
          if (!isRetryable(msg)) throw err;
        }
      }

      if (!fetched) {
        groupErrors.push(`  [${label}] all attempts failed:\n    ` + attemptErrors.join("\n    "));
      }
    }

    if (combined.length === 0 && groupErrors.length > 0) {
      // Surface the errors so the caller prints them, but don't throw —
      // other resource types should still be attempted.
      const summary = groupErrors.join("\n");
      console.warn(`\nWARN: no results fetched for ${resourceType}. Details:\n${summary}`);
    }
    return combined;
  }

  // Standard path: try GET with each ref param set, then POST fallback.
  const lastErrors: string[] = [];

  for (const refParams of refParamSets) {
    try {
      return await fetchByGet(resourceType, refParams);
    } catch (err: unknown) {
      const msg = (err as Error).message;
      lastErrors.push(`GET ${JSON.stringify(refParams)}: ${msg.split("\n")[0]}`);
      if (!isRetryable(msg)) throw err;
    }
  }

  for (const refParams of refParamSets) {
    try {
      return await fetchByPost(resourceType, refParams);
    } catch (err: unknown) {
      const msg = (err as Error).message;
      lastErrors.push(`POST ${JSON.stringify(refParams)}: ${msg.split("\n")[0]}`);
      if (!isRetryable(msg)) throw err;
    }
  }

  throw new Error(
    `No supported patient search param found for ${resourceType}. Tried:\n    ` +
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
      request: {
        method: r.id ? "PUT" : "POST",
        url:    r.id ? `${r.resourceType}/${r.id}` : r.resourceType,
      },
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

  // ── Step 0: discover server capabilities ──────────────────────────────────

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
      const note = params ? `[${refs.join(", ") || "none"}]` : "not in CapabilityStatement";
      console.log(`  ${rt}: patient-ref params = ${note}`);
    }
  } else {
    console.log("unavailable (will use defaults)\n");
  }
  console.log("");

  // ── Step 1: resolve patient FHIR IDs ──────────────────────────────────────

  const patientRecords: Array<{ fhirId: string; pnr?: string }> = [
    ...cfg.patientIds.map(id => ({ fhirId: id })),
  ];

  if (cfg.patientIdentifiers.length > 0) {
    for (const ident of cfg.patientIdentifiers) {
      const pnr = ident.replace(/[-+\s]/g, "");
      process.stdout.write(`Looking up patient ${pnr} ... `);
      try {
        let bundle = await fhirGet("Patient", { identifier: `${COS_PNR_SYSTEM}|${pnr}` });
        if ((bundle.entry ?? []).length === 0) {
          bundle = await fhirGet("Patient", { identifier: pnr });
        }
        const ids = (bundle.entry ?? []).map(e => e.resource.id).filter(Boolean) as string[];
        for (const id of ids) {
          if (!patientRecords.some(p => p.fhirId === id)) patientRecords.push({ fhirId: id, pnr });
        }
        console.log(`found ${ids.length}: ${ids.join(", ") || "(none)"}`);
      } catch (err: unknown) {
        console.warn(`WARN: ${(err as Error).message}`);
      }
    }
  } else if (cfg.patientIds.length === 0) {
    // COS sandbox has exactly 5 fixed test patients; no bulk listing is available.
    const COS_SANDBOX_PATIENTS = [
      "194609073277",  // Richard Lindeskog
      "198001072381",  // Bianca Fredriksson
      "194902142696",  // Lars Björk
      "197702202396",  // Kim Sundström
      "202103172389",  // Leah Nordberg (child)
    ];
    console.log(`using ${COS_SANDBOX_PATIENTS.length} known COS sandbox patients`);
    for (const pnr of COS_SANDBOX_PATIENTS) {
      process.stdout.write(`  Looking up ${pnr} ... `);
      try {
        const bundle = await fhirGet("Patient", { identifier: `${COS_PNR_SYSTEM}|${pnr}` });
        const ids = (bundle.entry ?? []).map(e => e.resource.id).filter(Boolean) as string[];
        for (const id of ids) {
          if (!patientRecords.some(p => p.fhirId === id)) patientRecords.push({ fhirId: id, pnr });
        }
        console.log(ids.length > 0 ? `found ${ids.join(", ")}` : "not found");
      } catch (err: unknown) {
        console.warn(`WARN: ${(err as Error).message}`);
      }
    }
  }

  if (patientRecords.length === 0) {
    console.warn("\nNo patients resolved. Patient-linked resources will be skipped.\n");
  } else {
    console.log(`\nPatient IDs: ${patientRecords.map(p => p.fhirId).join(", ")}\n`);
  }

  // ── Step 2: fetch resources ────────────────────────────────────────────────

  const collected: Record<string, FhirResource[]> = {};
  for (const rt of cfg.resourceTypes) collected[rt] = [];

  for (const rt of cfg.resourceTypes) {
    if (SKIP_TYPES.has(rt)) {
      console.log(`  ${rt} ... SKIP (not reachable via COS — see SKIP_TYPES)`);
      continue;
    }

    const isStandalone = STANDALONE_TYPES.has(rt);

    if (rt === "Patient") {
      // COS does not support listing Patient; read each resource individually.
      for (const { fhirId } of patientRecords) {
        process.stdout.write(`  Patient/${fhirId} ... `);
        try {
          const token = await getToken();
          const res = await fetch(`${cfg.fhirBaseUrl.replace(/\/$/, "")}/Patient/${fhirId}`, {
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
            console.warn(`WARN: ${res.status} ${await res.text()}`);
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
    } else if (isStandalone) {
      process.stdout.write(`  ${rt} ... `);
      try {
        const resources = await fetchByGet(rt);
        collected[rt].push(...resources);
        console.log(`${resources.length} found`);
      } catch (err: unknown) {
        console.warn(`WARN: ${(err as Error).message}`);
      }
    }

    collected[rt] = dedup(collected[rt]);
  }

  // ── Step 3: write bundles ──────────────────────────────────────────────────

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
