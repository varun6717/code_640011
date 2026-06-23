# Run Configurator — frontend (TASK-051)

The React SPA a non-technical operator uses to configure a run and hit **Generate**. It is the
working realization of `docs/design/PDLC_Configurator.jsx` — the mockup's design, layout, and 5
tabs are ported **as-is**; only the stubbed behavior is made real. It does **config + Generate
only** (FR-XS-09): it emits `UI_INPUT.yaml` and calls the backend; it never runs the agent (you
open VS Code Claude Code / Copilot yourself — the **Launch** tab shows the manual start steps).

## The 5 tabs

0. **IDE Repo Initializer** — `working_path`
1. **Domain** — `domain` (PBI → `payment_brand`)
2. **Project & Requirement** — `project_metadata` + the `frame` BRD seed
3. **Artifact Inventory** — `sources[]`: SharePoint PDF + Bitbucket code (live). **Confluence +
   Lucid are shown but disabled / "5B — deferred"** — not in 5A scope, never emitted.
4. **Generator** — pick `runtime_tool` (claude | copilot), review the emitted `UI_INPUT.yaml`,
   **Generate** → G0 descriptor, then **Launch** → manual hand-off steps.

## Emit contract

`src/emit.js` (`buildConfig`) is the single source of what gets POSTed — a §3.1 `UI_INPUT`
object. Mapping highlights: `frame.title` ← project name; `auth_ref` injected per source
(pointer only, never a secret); `run_id` omitted (assigned by Generate); Confluence/Lucid
excluded; `jira` deferred. The on-screen YAML pane is a styled **preview**; `buildConfig` is the
real payload.

Config is **immutable after Generate** (FR-XS-16): editing any field discards the generated
scaffold, so re-configuring is a new run.

## Run (live)

Needs the backend up and Node installed:

```bash
# 1) backend (from repo root)
.venv/bin/uvicorn app.backend.app:app --port 8000

# 2) frontend
cd app/frontend && npm install && npm run dev    # http://localhost:5173
```

The dev server proxies `/api/*` → the backend (`vite.config.js`; override with `PDLC_BACKEND`).

> Until **TASK-053** wires live registry resolution, the UI carries the locked `registry_sha`
> (`7d2e9a1`); a live Generate should target a registry the backend can hydrate at that pin
> (the external-build non-git copy, as the proofs do). Live source pulls are TASK-054/055; the
> full self-serve run is proven at TASK-056.

## Proof

```bash
.venv/bin/python fixtures/frontend/verify_frontend.py     # requires Node on PATH
```

Runs the **real** `emit.js` (via `scripts/emit_cli.mjs`) on a sample click-through
(`fixtures/frontend/sample_form.json`), asserts the emitted config is §3.1-conformant (live
connectors only), matches the locked example contract, and **Generates to a G0 scaffold**
through the backend. `npm run build` is the SPA compile smoke.
