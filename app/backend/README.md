# Generate backend service (TASK-050)

A FastAPI wrapper around the deterministic `core/scripts/generate.py` CLI. It is the HTTP
surface the React Run Configurator (TASK-051) calls to turn a configured run into a laid
§2.2 scaffold at the **G0 checkpoint**. It does **config + Generate only** (FR-XS-09): it
writes `UI_INPUT.yaml` and runs Generate — it does **not** run the agent. The operator opens
VS Code (Claude Code / Copilot) by hand afterward.

No new judgment lives here (FR-XS-03): every authoring decision stays in the spine. This is
filesystem + subprocess plumbing that reuses the existing units (`generate`, `hydrate`,
`ledger`, `telemetry`).

## Endpoints

| Method & path | Purpose |
|---|---|
| `POST /generate` | Validate config against §3.1 → write `UI_INPUT.yaml` → `generate.generate()` → return the **G0 descriptor** (`ran_workflow: false`) + the operator checklist + scaffold path. Invalid config → **422 naming the failing field(s)**. |
| `GET /runs/{id}/status` | Mirror the ledger: `run_state.json` (current stage + per-stage status) + `telemetry.jsonl` events. Read-only. |
| `GET /runs/{id}/ui_input` | Return the immutable run config (parsed + raw). |
| `GET /health` | Liveness. |

### `POST /generate` body

```json
{
  "config": { "...": "the §3.1 UI_INPUT mapping" },
  "registry": "optional registry path or URL (default: repo root)",
  "force": false
}
```

`config.run_id` is optional — Generate assigns `r-YYYY-MM-DD-HHMMSS` when absent (§3.1:
"assigned by Generate"). The config is serialized to `UI_INPUT.yaml` deterministically
(`sort_keys=False`), so re-posting the same config reproduces it byte-for-byte (NFR-01).

## Run

```bash
.venv/bin/pip install -r app/backend/requirements.txt
.venv/bin/uvicorn app.backend.app:app --reload      # run from the repo root
```

## Runs index

`run_id → working_path` is persisted to a JSONL append log (last-write-wins) so the status /
ui_input endpoints can resolve a run after a restart — same files-as-artifacts + JSONL
discipline as the rest of the MVP (no SQLite). Location: `$PDLC_RUNS_INDEX`, default
`runs/.runs_index.jsonl` (gitignored). It stores pointers only — never config content, never
a secret.

## Proof

```bash
.venv/bin/python fixtures/generate/verify_backend.py
```

Replays the locked `fixtures/UI_INPUT.example.yaml` through the in-process FastAPI
`TestClient` and asserts the API path is byte-identical to the CLI path (same `UI_INPUT.yaml`,
same G0 descriptor), the status/ui_input endpoints mirror the ledger, and invalid config →
422 naming the field. Offline + deterministic.
