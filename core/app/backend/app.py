"""app.py — Generate backend service (FastAPI) for the React Run Configurator (TASK-050).

The HTTP surface the UI calls to turn a configured run into a laid §2.2 scaffold at the G0
checkpoint. It does **config + Generate only** (FR-XS-09): it writes ``UI_INPUT.yaml`` and
runs ``generate.py`` — it does **not** run the agent (auto-launch stays deferred; the
operator opens VS Code Claude Code / Copilot by hand). A service wrapper around an existing
deterministic CLI — no new judgment (FR-XS-03).

Endpoints (TASK-050):
  POST /generate            config → UI_INPUT.yaml → generate.py → G0 descriptor + checklist
  GET  /runs/{id}/status    run_state.json + telemetry.jsonl (mirrors the ledger)
  GET  /runs/{id}/ui_input  the immutable run config for the run

Run:  uvicorn core.app.backend.app:app --reload    (deps: core/app/backend/requirements.txt)
"""
from __future__ import annotations

from typing import Any, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from . import service, validation

app = FastAPI(
    title="PDLC Generate backend",
    version="1.0.0",
    description="Config → UI_INPUT.yaml → Generate (G0). Config + Generate only; no agent run.",
)


class GenerateRequest(BaseModel):
    """A Generate request: the §3.1 config plus the external-build knobs ``generate.py`` exposes.

    ``config`` is the full ``UI_INPUT`` mapping (validated against §3.1 before anything is
    written). ``registry`` is the registry location ``generate.py`` hydrates from (a path now,
    a Bitbucket URL once TASK-053 lands; default = repo root). ``ts`` is accepted only so the
    proof harness can pin a deterministic Generate timestamp; the UI never sends it.
    """

    config: dict[str, Any] = Field(..., description="The §3.1 UI_INPUT mapping")
    registry: Optional[str] = Field(None, description="Registry path/URL (default: repo root)")
    force: bool = Field(False, description="Overwrite an already-hydrated working_path")
    ts: Optional[str] = Field(None, description="Pin the Generate timestamp (test/replay only)")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/generate")
def post_generate(req: GenerateRequest) -> dict[str, Any]:
    """Validate config (§3.1) → write ``UI_INPUT.yaml`` → Generate to G0. No agent run.

    Invalid config → **422 naming the failing field(s)**. A valid config lays the §2.2
    workspace, writes the immutable ``UI_INPUT.yaml``, and returns the G0 descriptor
    (``ran_workflow: False``) + the operator's inspection checklist + the scaffold path.
    """
    errors = validation.validate_ui_input(req.config)
    if errors:
        # 422 with one entry per failing field — the UI highlights exactly what to fix.
        raise HTTPException(status_code=422, detail={"errors": errors})

    try:
        result = service.run_generate(
            req.config, registry=req.registry, force=req.force, ts=req.ts
        )
    except service.GenerateError as exc:
        # A valid-shaped config that Generate could not realize (bad registry, hydrate fault).
        raise HTTPException(status_code=400, detail={"generate_error": str(exc)}) from exc

    return result


@app.get("/runs/{run_id}/status")
def get_status(run_id: str) -> dict[str, Any]:
    """Mirror the ledger for ``run_id`` (``run_state.json`` + ``telemetry.jsonl``)."""
    status = service.read_status(run_id)
    if status is None:
        raise HTTPException(status_code=404, detail={"unknown_run": run_id})
    return status


@app.get("/runs/{run_id}/ui_input")
def get_ui_input(run_id: str) -> dict[str, Any]:
    """Return the immutable ``UI_INPUT.yaml`` for ``run_id`` (parsed + raw)."""
    ui = service.read_ui_input(run_id)
    if ui is None:
        raise HTTPException(status_code=404, detail={"unknown_run": run_id})
    return ui
