/* api.js — thin client for the Generate backend (TASK-050). */

// Dev: Vite proxies /api → the FastAPI backend (see vite.config.js). Prod: same-origin.
const BASE = import.meta.env?.VITE_API_BASE ?? "/api";

/** POST /generate. Resolves to {descriptor, checklist, scaffold_path}; throws on failure
 *  with `.errors` (the §3.1 field messages from a 422, or a single generate error). */
export async function postGenerate(body) {
  const r = await fetch(`${BASE}/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const data = await r.json().catch(() => ({}));
  if (!r.ok) {
    const detail = data?.detail ?? {};
    const err = new Error(`Generate failed (${r.status})`);
    err.errors = detail.errors
      ?? (detail.generate_error ? [detail.generate_error] : [r.statusText || "request failed"]);
    throw err;
  }
  return data;
}

/** GET /runs/{id}/status — mirrors the ledger (run_state + telemetry events). */
export async function getStatus(runId) {
  const r = await fetch(`${BASE}/runs/${encodeURIComponent(runId)}/status`);
  if (!r.ok) throw new Error(`status ${r.status}`);
  return r.json();
}
