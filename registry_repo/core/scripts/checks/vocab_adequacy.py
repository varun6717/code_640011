#!/usr/bin/env python3
"""L1 vocabulary-adequacy detector (§5.4.1, ADR-003 / FR-DC-21) — deterministic.

The exact twin of the extractor coverage floor (``gate.check_coverage``), but for the
frozen **dictionary** instead of the frozen **tool**: *is the vocabulary big enough
for the concepts actually present in this corpus?* Containment (§10.1, ``tags ⊆
vocabulary``) is the opposite, hard-gate direction — it catches tag *invention*. This
catches the silent failure containment cannot: a concept the model recognized but
**could not tag**, because the model can never invent a tag (so an uncovered concept
would otherwise vanish without a trace).

Two signals, both model-free *here* (the model's only contribution — the per-file
``uncovered_concepts`` — was produced upstream in ``model_enrich`` and is just data by
the time it reaches this aggregation):

  1. PRIMARY — recurring ``uncovered_concepts``. A concept the model named as present
     but un-taggable, recurring across ≥ ``MIN_RECUR`` net-new files → a gap. Because
     it is independent of the tag count, it catches BOTH a fully-uncovered file
     (``tags: []``) and a *partially*-uncovered one (``tags: [routing]`` but a secondary
     ``tokenization`` concept un-nameable) — the case a plain empty-count waves through.
  2. FLOOR — deterministic ``untagged_ratio`` (files with ``tags == []`` / total) against
     ``adequacy_threshold`` (manifest §5.2, default 0.20). The always-on safety net:
     it still fires on a systematic fully-uncovered gap even if the model's
     ``uncovered_concepts`` emission was missing/unreliable, and it is the cheap trend
     line emitted as telemetry every run.

Direction: a **high** ``untagged_ratio`` is the bad one. The detector NEVER auto-grows
the vocabulary and NEVER blocks the run — it raises ``VOCAB_GAP_FLAG`` (a hand-raise,
the dictionary's twin of ``reonboard_flag``) for a human to dispose of. Turning a
recurring concept into a candidate tag (``vocab_gap_assess``), the human amendment, the
``vocab_sha`` bump, and the re-tag pass are the deferred **L2** half (Phase 5 / port).
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping, Optional, Sequence

# A concept must recur in at least this many net-new files to raise the primary flag.
# Deterministic constant (not a model judgment): one-off leftover meaning is noise; a
# concept that recurs is a systematic gap. Matches §5.4.1 ``MIN_RECUR``.
MIN_RECUR = 2

REPO_ROOT = Path(__file__).resolve().parents[3]


@dataclass(frozen=True)
class ConceptGap:
    concept: str
    evidence: tuple[str, ...]       # the files that named the concept


@dataclass
class AdequacyResult:
    arm: str
    untagged_ratio: float           # telemetry, emitted every run
    threshold: float
    floor_tripped: bool             # untagged_ratio > threshold
    concept_gaps: list[ConceptGap] = field(default_factory=list)

    @property
    def has_gap(self) -> bool:
        return self.floor_tripped or bool(self.concept_gaps)


def untagged_ratio(entries: Sequence[Mapping[str, object]]) -> float:
    """``count(entries with tags == []) / max(1, total)`` — deterministic floor signal."""
    total = len(entries)
    if total == 0:
        return 0.0
    untagged = sum(1 for e in entries if not e.get("tags"))
    return round(untagged / total, 4)


def recurring_concepts(
    uncovered_by_file: Mapping[str, Sequence[str]],
    min_recur: int = MIN_RECUR,
) -> list[ConceptGap]:
    """Aggregate per-file ``uncovered_concepts`` → concepts recurring in ≥ ``min_recur`` files.

    ``uncovered_by_file`` maps a file path → the ``uncovered_concepts`` the model emitted
    for it (the net-new delta of the build). Deterministic: a plain count + evidence
    collection, no judgment. Concepts and evidence are sorted for stable output.
    """
    evidence: dict[str, list[str]] = {}
    for path in sorted(uncovered_by_file):
        for concept in uncovered_by_file[path]:
            evidence.setdefault(concept, []).append(path)
    return [
        ConceptGap(concept=c, evidence=tuple(sorted(set(files))))
        for c, files in sorted(evidence.items())
        if len(set(files)) >= min_recur
    ]


def check_vocab_adequacy(
    entries: Sequence[Mapping[str, object]],
    uncovered_by_file: Mapping[str, Sequence[str]],
    threshold: float,
    *,
    arm: str = "code",
    min_recur: int = MIN_RECUR,
) -> AdequacyResult:
    """Run both adequacy signals. Pure — computes, never writes or blocks (§5.4.1).

    Returns an :class:`AdequacyResult` carrying the ``untagged_ratio`` (telemetry, every
    run), whether the floor tripped, and any recurring concept gaps. The caller routes
    flags to the ledger (``record_adequacy`` below) and emits the ratio as telemetry.
    """
    ratio = untagged_ratio(entries)
    return AdequacyResult(
        arm=arm,
        untagged_ratio=ratio,
        threshold=threshold,
        floor_tripped=ratio > threshold,
        concept_gaps=recurring_concepts(uncovered_by_file, min_recur),
    )


def record_adequacy(result: AdequacyResult, ledger_path: str | Path, *, ts: str | None = None) -> list[dict]:
    """Write any raised ``vocab_gap_flag`` records to ``decisions.jsonl`` (§3.6). Returns them.

    One record per recurring concept (primary), plus one floor record iff the
    ``untagged_ratio`` tripped. Emits nothing — and writes nothing — when adequate. The
    ``untagged_ratio`` telemetry is the caller's job (it goes to ``telemetry.jsonl`` every
    run, not only on a gap); this writer is for the advisory flags alone.
    """
    sys.path.insert(0, str(REPO_ROOT))
    from core.scripts.decisions import vocab_gap_flag  # local import: avoids hard dep when unused

    written: list[dict] = []
    for gap in result.concept_gaps:
        written.append(vocab_gap_flag(ledger_path, arm=result.arm, concept=gap.concept,
                                      evidence=list(gap.evidence), ts=ts))
    if result.floor_tripped:
        written.append(vocab_gap_flag(ledger_path, arm=result.arm,
                                      untagged_ratio=result.untagged_ratio,
                                      threshold=result.threshold, ts=ts))
    return written


# ──────────────────────────────────────────────────────────────────────────────
# Demonstration (TASK-013 fixture/proof). Run: python3 core/scripts/checks/vocab_adequacy.py
#   - CLEAN: the signed c_repo map (untagged_ratio ≈ 0.06, no uncovered concepts) → NO flag.
#   - CRAFTED: a fully-uncovered file AND a partially-uncovered one, both naming
#     `tokenization` → the PRIMARY signal flags the concept (the partial case is the one
#     an empty-count misses), and the floor also trips. Same proof shape as
#     assert_tags_in_vocabulary (TASK-011).
# ──────────────────────────────────────────────────────────────────────────────
def _demo() -> None:
    threshold = 0.20

    oracle = json.loads((REPO_ROOT / "fixtures/c_repo/expected_code_map.json").read_text())
    clean = check_vocab_adequacy(oracle["files"], uncovered_by_file={}, threshold=threshold)
    print("CLEAN  (signed c_repo map):")
    print(f"  untagged_ratio={clean.untagged_ratio}  threshold={threshold}  "
          f"floor_tripped={clean.floor_tripped}  concept_gaps={clean.concept_gaps}")
    assert not clean.has_gap, "clean c_repo map must raise no adequacy flag"

    crafted_entries = [
        {"path": "payment/tokenize.c", "tags": []},                 # fully uncovered
        {"path": "routing/secure_route.c", "tags": ["routing"]},     # partially uncovered (non-empty!)
    ]
    crafted_uncovered = {
        "payment/tokenize.c": ["tokenization"],
        "routing/secure_route.c": ["tokenization"],                  # recurs → primary flag
    }
    crafted = check_vocab_adequacy(crafted_entries, crafted_uncovered, threshold=threshold)
    print("\nCRAFTED (fully- + partially-uncovered, both name 'tokenization'):")
    print(f"  untagged_ratio={crafted.untagged_ratio}  floor_tripped={crafted.floor_tripped}")
    for g in crafted.concept_gaps:
        print(f"  PRIMARY  VOCAB_GAP_FLAG concept={g.concept!r} evidence={list(g.evidence)}")
    assert any(g.concept == "tokenization" for g in crafted.concept_gaps), \
        "the recurring 'tokenization' concept (incl. the partially-tagged file) must flag"
    assert crafted.floor_tripped, "the fully-uncovered file should also trip the floor"
    print("\nPASS — clean map silent; crafted map flags the partial-coverage gap an empty-count misses.")


if __name__ == "__main__":
    _demo()
