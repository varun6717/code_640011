#!/usr/bin/env python3
"""telemetry.py — the run-ledger writers: `emit()` + run_state updater (§3.4, §8.1, §3.5).

The single surface every run stage writes its ledger through. Three concerns:

  1. ``emit()`` / ``Emitter`` — the **telemetry.jsonl** event writer (§3.4 / §8.1). Every
     event carries the common envelope (``ts, run_id, domain, tool, event``) + the §8.1
     per-event payload; the record is validated against the telemetry schema before it is
     appended, so a malformed emission fails loud rather than poisoning the stream. These
     rows are the *only* source ``metrics_scan.py`` (§8.2, TASK-048) reads — **no metric is
     hand-entered** (NFR-06, FR-MX-01). All nine §8.1 events have a typed helper.

  2. ``update_run_state()`` — the **run_state.json** updater (§3.5): last-write-wins current
     state, per-stage status with ``started`` / ``completed`` stamps + artifact ``version``,
     driving §9 resume (NFR-08). Validated against the run_state schema on every write.

  3. The **decisions.jsonl** gate/flag audit (§3.6, NFR-03) — re-exported from
     ``decisions.py`` (``gate``, ``flag``, ``reonboard_flag``, ``vocab_gap_flag``) so a run
     stage has one import for any ledger record. Those record *who/when/outcome/rationale*.

It is plumbing (NFR-07): it stamps, validates, and appends/replaces files. It makes no
authoring judgment and holds no global state — every writer takes an explicit ledger dir
and accepts an explicit ``ts`` so a caller (or a test) can make a record deterministic.

Ledger layout (a run's ``ledger/``, §2.2): ``telemetry.jsonl`` (append), ``run_state.json``
(replace), ``decisions.jsonl`` (append).
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import ledger
# Re-export the decisions.jsonl writers so telemetry.py is the one ledger-writing surface.
from decisions import gate, flag, reonboard_flag, vocab_gap_flag  # noqa: F401

__all__ = [
    "emit", "Emitter", "update_run_state", "mark_stage",
    "gate", "flag", "reonboard_flag", "vocab_gap_flag",
]

# §8.1 stage vocabulary (also pinned in the telemetry/run_state schemas).
STAGES = ("ingest", "code_map", "brd_authoring", "code_impact",
          "frd_authoring", "jira_authoring", "jira_push")

_RUN_STATE_STATUS = ("pending", "running", "done", "failed")

_telemetry_schema = None  # lazily loaded + cached (schema read is pure)
_run_state_schema = None


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _tel_schema() -> dict:
    global _telemetry_schema
    if _telemetry_schema is None:
        _telemetry_schema = ledger.load_schema("telemetry")
    return _telemetry_schema


def _rs_schema() -> dict:
    global _run_state_schema
    if _run_state_schema is None:
        _run_state_schema = ledger.load_schema("run_state")
    return _run_state_schema


# ── telemetry.jsonl ────────────────────────────────────────────────────────────
def emit(
    ledger_dir: str | Path,
    event: str,
    *,
    run_id: str,
    domain: str,
    tool: str,
    ts: str | None = None,
    validate: bool = True,
    **payload,
) -> dict:
    """Append one §8.1 event to ``ledger_dir/telemetry.jsonl`` and return the record.

    Builds the envelope (``ts, run_id, domain, tool, event``) + the given ``payload`` and,
    unless ``validate=False``, asserts the result against the telemetry schema — so an event
    that would not satisfy §8.1 (wrong payload for its ``event``, a ``stage`` outside the
    vocabulary, an unknown field) is rejected here, not discovered later by ``metrics_scan``.
    """
    record = {"ts": ts or _now_iso(), "run_id": run_id, "domain": domain, "tool": tool,
              "event": event, **payload}
    if validate:
        errs = ledger.validate_record(record, _tel_schema())
        if errs:
            raise ValueError(f"telemetry event fails §8.1 schema: {errs} | record={record}")
    path = Path(ledger_dir) / "telemetry.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    return record


@dataclass
class Emitter:
    """Envelope-bound telemetry writer — binds ``ledger_dir`` + ``run_id/domain/tool`` once
    so a run stage emits events without repeating the envelope. One typed method per §8.1
    event; each validates + appends via ``emit()``."""

    ledger_dir: str | Path
    run_id: str
    domain: str
    tool: str

    def emit(self, event: str, *, ts: str | None = None, validate: bool = True, **payload) -> dict:
        return emit(self.ledger_dir, event, run_id=self.run_id, domain=self.domain,
                    tool=self.tool, ts=ts, validate=validate, **payload)

    # Typed per-event helpers — payload fields exactly as §8.1 pins them.
    def run_started(self, *, path: str, registry_sha: str, ts: str | None = None) -> dict:
        return self.emit("run_started", path=path, registry_sha=registry_sha, ts=ts)

    def stage_started(self, stage: str, *, ts: str | None = None) -> dict:
        return self.emit("stage_started", stage=stage, ts=ts)

    def stage_completed(self, stage: str, *, duration_ms: int, ts: str | None = None) -> dict:
        return self.emit("stage_completed", stage=stage, duration_ms=duration_ms, ts=ts)

    def model_call(self, *, stage: str, model: str, tokens_in: int, tokens_out: int,
                   cost_usd: float, ts: str | None = None) -> dict:
        return self.emit("model_call", stage=stage, model=model, tokens_in=tokens_in,
                          tokens_out=tokens_out, cost_usd=cost_usd, ts=ts)

    def validation(self, *, artifact: str, score: float, ts: str | None = None) -> dict:
        return self.emit("validation", artifact=artifact, score=score, ts=ts)

    def gate_decision(self, *, gate: str, outcome: str, actor: str, version: int,
                      ts: str | None = None) -> dict:
        return self.emit("gate_decision", gate=gate, outcome=outcome, actor=actor,
                          version=version, ts=ts)

    def flag_decision(self, *, flag_type: str, option: str, severity: str,
                      ts: str | None = None) -> dict:
        return self.emit("flag_decision", flag_type=flag_type, option=option,
                          severity=severity, ts=ts)

    def jira_push(self, *, epics: int, success: bool, partial: bool, ts: str | None = None) -> dict:
        return self.emit("jira_push", epics=epics, success=success, partial=partial, ts=ts)

    def error(self, *, stage: str, kind: str, message: str, ts: str | None = None) -> dict:
        return self.emit("error", stage=stage, kind=kind, message=message, ts=ts)


# ── run_state.json ───────────────────────────────────────────────────────────--
def update_run_state(
    ledger_dir: str | Path,
    *,
    stage: str | None = None,
    status: str | None = None,
    current_stage: str | None = None,
    version: int | None = None,
    repo_commit_sha: str | None = None,
    ts: str | None = None,
    validate: bool = True,
) -> dict:
    """Update ``ledger_dir/run_state.json`` (§3.5) last-write-wins; return the new state.

    Reads the existing state (seeded by ``ledger.init_ledger``), applies the change, and
    rewrites it. When ``stage``+``status`` are given, the stage's status is set and stamped
    per §3.5 — ``running`` records ``started`` (once), ``done``/``failed`` records
    ``completed`` (``started`` preserved). ``current_stage`` advances to ``stage`` unless
    set explicitly. ``version`` pins the accepted artifact version on the stage;
    ``repo_commit_sha`` sets the top-level repo pin. Validated against the run_state schema.
    """
    d = Path(ledger_dir)
    rs_path = d / "run_state.json"
    state = json.loads(rs_path.read_text(encoding="utf-8"))
    when = ts or _now_iso()

    if stage is not None:
        if stage not in STAGES:
            raise ValueError(f"stage {stage!r} not in §8.1 vocabulary {STAGES}")
        entry = state.setdefault("stages", {}).setdefault(stage, {"status": "pending"})
        if status is not None:
            if status not in _RUN_STATE_STATUS:
                raise ValueError(f"status {status!r} not in {_RUN_STATE_STATUS}")
            entry["status"] = status
            if status == "running":
                entry.setdefault("started", when)
            elif status in ("done", "failed"):
                entry["completed"] = when
        if version is not None:
            entry["version"] = version

    if current_stage is not None:
        if current_stage not in STAGES:
            raise ValueError(f"current_stage {current_stage!r} not in §8.1 vocabulary {STAGES}")
        state["current_stage"] = current_stage
    elif stage is not None:
        state["current_stage"] = stage

    if repo_commit_sha is not None:
        state["repo_commit_sha"] = repo_commit_sha

    if validate:
        errs = ledger.validate_record(state, _rs_schema())
        if errs:
            raise ValueError(f"run_state fails §3.5 schema: {errs} | state={state}")

    rs_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    return state


def mark_stage(
    emitter: Emitter,
    stage: str,
    status: str,
    *,
    duration_ms: int | None = None,
    version: int | None = None,
    ts: str | None = None,
) -> dict:
    """Convenience: advance both ledgers for a stage transition in lock-step.

    Updates ``run_state.json`` (stage status + stamps + ``current_stage``) **and** emits the
    matching telemetry event — ``stage_started`` on ``running``, ``stage_completed``
    (requires ``duration_ms``) on ``done`` — so the two ledgers never drift. ``failed`` /
    ``pending`` update run_state only (the ``error`` event is emitted separately with its
    payload). Returns the new run_state.
    """
    when = ts or _now_iso()
    state = update_run_state(emitter.ledger_dir, stage=stage, status=status,
                             version=version, ts=when)
    if status == "running":
        emitter.stage_started(stage, ts=when)
    elif status == "done":
        if duration_ms is None:
            raise ValueError("mark_stage(status='done') requires duration_ms (§8.1 stage_completed)")
        emitter.stage_completed(stage, duration_ms=duration_ms, ts=when)
    return state


# ──────────────────────────────────────────────────────────────────────────────
# Proof (TASK-032 fixture/proof). Run: python3 core/scripts/telemetry.py
#   Build a synthetic full-run event stream + run_state lifecycle + all four decision
#   kinds, then assert: every telemetry row is §8.1-schema-valid; the stream carries the
#   events each MVP metric (§8.2) is derived from with NO hand entry; run_state validates
#   and resumes coherently; decisions.jsonl validates. (metrics_scan.py is TASK-048; here
#   we prove the stream is sufficient + valid — the input contract metrics_scan consumes.)
# ──────────────────────────────────────────────────────────────────────────────
def _demo() -> None:
    import tempfile

    import decisions

    T = "2026-06-22T00:00:00Z"  # fixed ts → deterministic proof
    with tempfile.TemporaryDirectory(prefix="telemetry-proof-") as tmp:
        led = ledger.init_ledger(Path(tmp) / "ledger", run_id="r-proof-001")
        em = Emitter(led, run_id="r-proof-001", domain="payment_brand", tool="claude")

        # A full BRD→FRD→(jira) run's worth of events — one of every §8.1 event.
        em.run_started(path="/work/r-proof-001", registry_sha="7d2e9a1", ts=T)
        mark_stage(em, "ingest", "running", ts=T)
        mark_stage(em, "ingest", "done", duration_ms=12000, ts=T)
        mark_stage(em, "code_map", "running", ts=T)
        mark_stage(em, "code_map", "done", duration_ms=8000, ts=T)
        em.model_call(stage="brd_authoring", model="claude-opus-4-8", tokens_in=18000,
                      tokens_out=4200, cost_usd=0.91, ts=T)
        em.model_call(stage="code_impact", model="claude-opus-4-8", tokens_in=9000,
                      tokens_out=1500, cost_usd=0.34, ts=T)
        em.validation(artifact="brd", score=88.0, ts=T)
        em.gate_decision(gate="G1", outcome="accept", actor="vmunjal", version=1, ts=T)
        em.model_call(stage="frd_authoring", model="claude-opus-4-8", tokens_in=12000,
                      tokens_out=3000, cost_usd=0.52, ts=T)
        em.validation(artifact="frd", score=91.0, ts=T)
        em.gate_decision(gate="G2", outcome="accept", actor="vmunjal", version=1, ts=T)
        em.flag_decision(flag_type="scope_ripple", option="include in scope",
                         severity="material", ts=T)
        em.jira_push(epics=5, success=True, partial=False, ts=T)
        em.error(stage="ingest", kind="source_timeout", message="confluence read timed out", ts=T)

        # All four decisions.jsonl kinds (the NFR-03 audit twins).
        decisions.gate(led / "decisions.jsonl", gate="G1", outcome="accept", version=1, ts=T)
        decisions.flag(led / "decisions.jsonl", flag_type="scope_ripple",
                       area="settlement/reconciler", option="include in scope",
                       severity="material", rationale="Shares the brand table; in-scope per ops.", ts=T)
        decisions.reonboard_flag(led / "decisions.jsonl", language="c", coverage=0.71,
                                 floor=0.80, patterns=["macro"], decision="re-onboard", ts=T)
        decisions.vocab_gap_flag(led / "decisions.jsonl", arm="code", concept="tokenization",
                                 evidence=["payment/tokenize.c"], decision="amend-vocab", ts=T)

        # 1) Whole ledger validates against all three schemas.
        report = ledger.validate_ledger(led)
        print("ledger validation:")
        for fname, errs in report.items():
            print(f"  {fname:18} {'OK' if not errs else errs}")
        assert all(not e for e in report.values()), f"ledger must validate clean: {report}"

        # 2) The stream carries every §8.1 event the MVP metrics (§8.2) derive from.
        events = [json.loads(l) for l in (led / "telemetry.jsonl").read_text().splitlines() if l.strip()]
        kinds = {e["event"] for e in events}
        required = {"run_started", "stage_started", "stage_completed", "model_call",
                    "validation", "gate_decision", "flag_decision", "jira_push", "error"}
        missing = required - kinds
        print(f"\nevents present: {sorted(kinds)}")
        assert not missing, f"stream missing §8.1 events: {missing}"

        # 3) Spot-check the derivations are computable with NO hand entry (NFR-06/FR-MX-01).
        brd_cost = sum(e["cost_usd"] for e in events
                       if e["event"] == "model_call" and e["stage"] in ("brd_authoring", "code_impact"))
        frd_cost = sum(e["cost_usd"] for e in events
                       if e["event"] == "model_call" and e["stage"] == "frd_authoring")
        p95_inputs = [e["duration_ms"] for e in events if e["event"] == "stage_completed"]
        assert abs(brd_cost - 1.25) < 1e-9, brd_cost            # M01 $/BRD
        assert abs(frd_cost - 0.52) < 1e-9, frd_cost            # M02 $/FRD
        assert p95_inputs, "M07 needs stage_completed durations"
        print(f"derivable: M01 $/BRD={brd_cost:.2f}  M02 $/FRD={frd_cost:.2f}  "
              f"M07 inputs={p95_inputs}  (no hand entry)")

        # 4) run_state resumed coherently to the last stage touched.
        rs = json.loads((led / "run_state.json").read_text())
        assert rs["stages"]["ingest"]["status"] == "done", rs
        assert rs["stages"]["ingest"]["started"] == T and rs["stages"]["ingest"]["completed"] == T
        assert rs["current_stage"] == "code_map", rs["current_stage"]

        # 5) A bad emission is rejected at the door (validation bites).
        try:
            em.emit("stage_completed", stage="ingest", ts=T)  # missing duration_ms
        except ValueError:
            print("\nnegative: stage_completed without duration_ms -> REJECTED (good)")
        else:
            raise AssertionError("invalid event should have been rejected")
        try:
            update_run_state(led, stage="deploy", status="running", ts=T)  # stage outside vocab
        except ValueError:
            print("negative: run_state stage 'deploy' -> REJECTED (good)")
        else:
            raise AssertionError("bad stage should have been rejected")

    print("\nPASS — emit() validates + writes all §8.1 events; run_state updater stamps + "
          "resumes; decisions.jsonl audit valid; stream sufficient for MVP metrics (NFR-06, "
          "FR-MX-01, NFR-03).")


if __name__ == "__main__":
    _demo()
