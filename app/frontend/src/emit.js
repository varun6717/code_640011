/* emit.js — form state → §3.1 UI_INPUT config object (TASK-051).
 *
 * The single source of truth for what the Run Configurator emits. The component's `buildYaml`
 * renders a *preview*; this builds the actual object POSTed to the backend (`POST /generate`),
 * which validates it against TECH_SPEC §3.1 and writes `UI_INPUT.yaml`. Kept React-free and
 * pure so it is importable by both the SPA and the offline proof (`scripts/emit_cli.mjs`).
 *
 * Mapping rules (mirrors the buildYaml preview + the §3.1 contract):
 *   - run_id        — omitted; "assigned by Generate" (§3.1). The backend stamps it.
 *   - registry_sha  — defaulted to the locked pin; TASK-053 replaces this with live
 *                     Bitbucket resolution. Carried in the config because generate.py reads it.
 *   - frame.title   — seeded from project_name (§3.1: project_name "also seeds frame.title").
 *   - auth_ref      — injected per source type at emit; the operator never enters a secret
 *                     (§7, FR-DC-12). Pointer only.
 *   - sources       — only the 5A-live connectors (SharePoint PDF, Bitbucket code) are emitted.
 *                     Confluence + Lucid are shown in the UI but deferred (5B) — never emitted.
 *   - jira          — omitted; deferred this slice (BRD → FRD only).
 */

// The locked registry pin (matches fixtures/UI_INPUT.example.yaml). Until TASK-053 wires real
// registry resolution from a Bitbucket URL, the UI carries this so the config is §3.1-valid.
export const DEFAULT_REGISTRY_SHA = "7d2e9a1";

// Auth-seam reference per source type (§7). Never a secret — a pointer the connector resolves.
const AUTH_REF = {
  sharepoint: "jpmc_adapters:sharepoint",
  bitbucket: "jpmc_adapters:bitbucket",
};

const trimmed = (x) => (x ?? "").toString().trim();

export function buildConfig(form, { registrySha = DEFAULT_REGISTRY_SHA } = {}) {
  const sources = [];

  // SharePoint PDF document sources → type:sharepoint (TASK-055 connector).
  for (const it of form.pdf ?? []) {
    const url = trimmed(it.url);
    if (url) sources.push({ type: "sharepoint", url, auth_ref: AUTH_REF.sharepoint });
  }

  // Bitbucket code repo sources → type:bitbucket (clone.py, TASK-054). seal + repo_url.
  for (const it of form.code ?? []) {
    const repo_url = trimmed(it.url);
    const seal_id = trimmed(it.seal);
    if (repo_url || seal_id) {
      sources.push({ type: "bitbucket", seal_id, repo_url, auth_ref: AUTH_REF.bitbucket });
    }
  }

  const config = {
    schema_version: 1,
    working_path: trimmed(form.working_path),
    domain: trimmed(form.domain),
    runtime_tool: trimmed(form.runtime_tool),
    registry_sha: registrySha,
    project_metadata: {
      project_name: trimmed(form.project_name),
      application_name: trimmed(form.application_name),
      line_of_business: trimmed(form.lob),
      requestor: trimmed(form.requestor),
      requestor_sid: trimmed(form.requestor_sid),
    },
    frame: {
      title: trimmed(form.project_name),
      intent: trimmed(form.intent),
      scope_hints: [...(form.scope_hints ?? [])],
      stakeholders: [...(form.stakeholders ?? [])],
    },
    sources,
    gates: { score_threshold: Number.parseInt(form.score_threshold, 10) },
  };

  const deadline = trimmed(form.compliance_deadline);
  if (deadline) config.frame.key_dates = { compliance_deadline: deadline };

  return config;
}
