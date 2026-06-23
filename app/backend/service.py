"""service.py — Generate orchestration + run lookup (TASK-050).

The thin layer between the HTTP surface (``app.py``) and the existing deterministic
``generate.py`` CLI. It does exactly what the CLI ``main()`` does — write ``UI_INPUT.yaml``
from the validated config, call ``generate.generate()``, surface the G0 descriptor — plus a
small **runs index** so the status/ui_input endpoints can map ``run_id → working_path``
without re-deriving it. **No agent run** (FR-XS-09); no authoring judgment (FR-XS-03).

The runs index is a JSONL append log (last-write-wins per ``run_id``) — same files-as-
artifacts + JSONL-ledger discipline as the rest of the MVP (no SQLite). Its location is
``PDLC_RUNS_INDEX`` (default ``runs/.runs_index.jsonl`` under the repo); it stores pointers
only (``run_id``, ``working_path``, ``ts``) — never config content, never a secret.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

# The deterministic units (generate/ledger/telemetry) live in core/scripts; put it on the
# path so importing the service from anywhere (app, proof, REPL) resolves them.
_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPTS = _REPO_ROOT / "core" / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import generate  # noqa: E402  (core/scripts/generate.py)


class GenerateError(RuntimeError):
    """A failure from the deterministic Generate path (bad registry, hydrate error, …).

    Distinct from a §3.1 validation failure: those are caught earlier and become 422s naming
    the field; this is a 4xx/5xx surfacing of a generate.py-side error.
    """


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def runs_index_path() -> Path:
    """Resolve the runs-index JSONL location (env override, else repo ``runs/``)."""
    override = os.environ.get("PDLC_RUNS_INDEX")
    return Path(override) if override else _REPO_ROOT / "runs" / ".runs_index.jsonl"


def _record_run(run_id: str, working_path: Path, ts: str) -> None:
    """Append a ``run_id → working_path`` pointer to the runs index (last-write-wins)."""
    idx = runs_index_path()
    idx.parent.mkdir(parents=True, exist_ok=True)
    row = {"run_id": run_id, "working_path": str(working_path), "ts": ts}
    with idx.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def lookup_working_path(run_id: str) -> Path | None:
    """Resolve a ``run_id`` to its workspace via the runs index (last matching row wins)."""
    idx = runs_index_path()
    if not idx.is_file():
        return None
    found: Path | None = None
    for line in idx.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if row.get("run_id") == run_id and row.get("working_path"):
            found = Path(row["working_path"])
    return found


def _assign_run_id(ts: str) -> str:
    """Generate assigns ``run_id`` when the config omits it (§3.1: "assigned by Generate").

    Form ``r-YYYY-MM-DD-HHMMSS`` from the Generate timestamp — unique per second, sortable,
    and matching the ``r-…`` convention of the locked fixture.
    """
    # ts is ISO ``2026-06-22T18:40:05Z`` → ``r-2026-06-22-184005``.
    date, _, time = ts.rstrip("Z").partition("T")
    return f"r-{date}-{time.replace(':', '')}"


def run_generate(
    config: dict[str, Any],
    *,
    registry: str | None = None,
    force: bool = False,
    ts: str | None = None,
) -> dict[str, Any]:
    """Write ``UI_INPUT.yaml`` from ``config`` and run Generate to G0 — no workflow (FR-XS-09).

    ``config`` is assumed already §3.1-valid (``app.py`` validates first). Returns
    ``{descriptor, checklist, scaffold_path}``: the G0 descriptor verbatim from
    ``generate.generate()`` (``ran_workflow: False``), the operator's G0 checklist, and the
    laid workspace path. The written ``UI_INPUT.yaml`` is a deterministic serialization of
    ``config`` (``sort_keys=False`` preserves §3.1 order), so re-posting the same config
    reproduces it byte-for-byte.
    """
    ts = ts or _now_iso()
    # Registry source: an explicit request value wins; else PDLC_REGISTRY (deployment default);
    # else None → generate.py falls back to the repo root. TASK-053 replaces this with live
    # Bitbucket resolution; the env is the external-build / local-demo convenience until then.
    registry = registry or os.environ.get("PDLC_REGISTRY")

    cfg = dict(config)  # shallow copy — we may stamp run_id without mutating the caller's dict
    if not cfg.get("run_id"):
        cfg["run_id"] = _assign_run_id(ts)

    working_path = Path(str(cfg["working_path"]))
    working_path.mkdir(parents=True, exist_ok=True)

    # Serialize config → a UI_INPUT.yaml that generate.py copies verbatim into the workspace.
    # Write it inside working_path's parent staging area then hand its path to generate(); the
    # CLI's own copy-verbatim step lands the immutable run identity at <working_path>/UI_INPUT.yaml.
    staged = working_path.parent / f".{cfg['run_id']}.UI_INPUT.yaml"
    staged.parent.mkdir(parents=True, exist_ok=True)
    staged.write_text(
        yaml.safe_dump(cfg, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )

    try:
        descriptor = generate.generate(
            staged,
            registry=registry,
            working_path=working_path,
            force=force,
            ts=ts,
        )
    except (ValueError, FileExistsError, FileNotFoundError, RuntimeError, OSError, KeyError) as exc:
        raise GenerateError(str(exc)) from exc
    finally:
        staged.unlink(missing_ok=True)  # the verbatim copy now lives in the workspace

    _record_run(descriptor["run_id"], working_path, ts)

    return {
        "descriptor": descriptor,
        "checklist": generate._g0_checklist(descriptor),
        "scaffold_path": str(working_path),
    }


def read_status(run_id: str) -> dict[str, Any] | None:
    """Mirror the ledger for ``run_id``: ``run_state.json`` + the ``telemetry.jsonl`` events.

    Returns ``None`` if the run is unknown. Reads only — never advances a stage, never writes.
    Records progress, never artifact content (FR-XS-05).
    """
    workspace = lookup_working_path(run_id)
    if workspace is None:
        return None

    ledger_dir = workspace / "ledger"
    run_state = _read_json(ledger_dir / "run_state.json")
    events = _read_jsonl(ledger_dir / "telemetry.jsonl")

    return {
        "run_id": run_id,
        "working_path": str(workspace),
        "current_stage": (run_state or {}).get("current_stage"),
        "stages": (run_state or {}).get("stages", {}),
        "events": events,
        # G0 is the only checkpoint Generate can have reached; the run advances it later.
        "checkpoint": "G0" if events else None,
    }


def read_ui_input(run_id: str) -> dict[str, Any] | None:
    """Return the workspace ``UI_INPUT.yaml`` (parsed + raw) for ``run_id``, or ``None``."""
    workspace = lookup_working_path(run_id)
    if workspace is None:
        return None
    path = workspace / "UI_INPUT.yaml"
    if not path.is_file():
        return None
    raw = path.read_text(encoding="utf-8")
    return {"run_id": run_id, "ui_input": yaml.safe_load(raw), "raw": raw}


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    out: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            out.append(json.loads(line))
    return out
