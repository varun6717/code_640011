#!/usr/bin/env python3
"""`decisions.jsonl` writers — the gate + flag audit ledger (§3.6, NFR-03).

Append-only, one JSON object per line. This module owns the two flag writers the
gate raises in its post-build path (§5.3):

  - ``reonboard_flag`` — the *extractor* coverage floor was tripped (§5.4, FR-DC-16):
    "a structural idiom the frozen tool can't parse — re-bless it?"
  - ``vocab_gap_flag`` — the *vocabulary* adequacy detector raised its hand
    (§5.4.1, ADR-003 / FR-DC-21): "a concept the frozen dictionary can't tag."

Both are the same shape of event: a **frozen artifact noticing it has been
outgrown and asking a human**. Neither writer mutates the artifact — it records a
hand-raise for a human to dispose of (`decision` defaults to ``"pending"`` until a
human picks ``amend-vocab`` / ``accept-as-is`` / ``re-onboard``). The run is NOT
blocked by either (advisory runtime flags; §10 containment stays the hard gate).

Records are appended to a run's ``ledger/decisions.jsonl`` (created with the run
workspace in TASK-022). The writers take an explicit ``ledger_path`` so they are
pure I/O with no global state, and an explicit ``ts`` so a caller can make the
record deterministic (tests pass a fixed timestamp; a real run stamps now).
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

DEFAULT_ACTOR = "vmunjal"


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def append_decision(ledger_path: str | Path, record: dict) -> dict:
    """Append one §3.6 record as a JSON line to ``ledger_path``. Returns the record.

    Append-only and self-contained (creates the file/parents if absent). The record
    is written exactly as given — the typed builders below construct the §3.6 shapes.
    """
    path = Path(ledger_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    return record


def reonboard_flag(
    ledger_path: str | Path,
    *,
    language: str,
    coverage: float,
    floor: float,
    patterns: Sequence[str] = (),
    decision: str = "pending",
    actor: str = DEFAULT_ACTOR,
    ts: str | None = None,
) -> dict:
    """Write a ``reonboard_flag`` record (§3.6 / §5.4) — extractor coverage below floor.

    Raised by the gate's ``check_coverage`` when ``coverage < floor`` (FR-DC-16). It
    asks a human whether to re-bless the extractor for new idioms; the frozen
    extractor is NEVER auto-modified. ``patterns`` carries the ``unresolved_patterns``
    that drove the gap so the human sees *what* the tool could not parse.
    """
    record = {
        "ts": ts or _now_iso(),
        "kind": "reonboard_flag",
        "language": language,
        "coverage": coverage,
        "floor": floor,
        "unresolved_patterns": list(patterns),
        "decision": decision,
        "actor": actor,
    }
    return append_decision(ledger_path, record)


def vocab_gap_flag(
    ledger_path: str | Path,
    *,
    arm: str,
    concept: str | None = None,
    evidence: Sequence[str] | None = None,
    untagged_ratio: float | None = None,
    threshold: float | None = None,
    decision: str = "pending",
    actor: str = DEFAULT_ACTOR,
    ts: str | None = None,
) -> dict:
    """Write a ``vocab_gap_flag`` record (§3.6 / §5.4.1, ADR-003). Two shapes, one kind.

    - **Primary** (concept): pass ``concept`` + ``evidence`` — a recurring concept the
      vocabulary lacks, caught from the model's ``uncovered_concepts`` (so it covers a
      *partially*-tagged file too, not just a fully-untagged one).
    - **Floor** (ratio): pass ``untagged_ratio`` + ``threshold`` — the deterministic,
      model-free safety net crossed ``adequacy_threshold``.

    Exactly one shape per call. The vocabulary is NEVER auto-grown — this is a
    hand-raise, the dictionary's twin of ``reonboard_flag``.
    """
    if (concept is None) == (untagged_ratio is None):
        raise ValueError("vocab_gap_flag: pass exactly one of (concept+evidence) | (untagged_ratio+threshold)")
    record: dict = {
        "ts": ts or _now_iso(),
        "kind": "vocab_gap_flag",
        "arm": arm,
    }
    if concept is not None:
        record["concept"] = concept
        record["evidence"] = list(evidence or [])
    else:
        record["untagged_ratio"] = untagged_ratio
        record["threshold"] = threshold
    record["decision"] = decision
    record["actor"] = actor
    return append_decision(ledger_path, record)
