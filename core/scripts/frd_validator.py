#!/usr/bin/env python3
"""`frd_validator` scoring + G2 gate wiring — the deterministic soft-gate (§9.3, FR-FR-05).

The FRD-side twin of `brd_validator.py` (TASK-043). The `frd_validator` skill is the *reader*: it
parses `FRD.md`'s per-topic `traces_to` + the trailing `<!-- traces: {...} -->` block + each
section's `functional_kind` and its testability artifact (acceptance criteria, or a measurable
target for `nfr`), against the accepted BRD's anchors. That extraction is the model's job. This
module is the part that MUST be deterministic and **model-free**: the §9.3 score arithmetic, the
anchor **resolution** (set membership — a typo'd anchor does not silently "cover" a BRD requirement),
and the single absolute hard precondition that decides **G2 eligibility**. No model call here.

§9.3:
    traceability = frd_topics_with_valid_traces_to / total_frd_topics
                   # valid = every anchor in traces_to resolves to a REAL BRD anchor (and is non-empty)
    testability  = topics_with_required_artifact / total_frd_topics
                   # acceptance criteria required for actor_flow|system_behavior|data_contract|
                   # error_state; nfr requires a measurable target INSTEAD
    frd_score = round(100 * (0.5 * traceability + 0.5 * testability))
    G2 passes iff  frd_score >= threshold  AND (hard) every BRD requirement traced by >=1 FRD topic
                   OR explicitly marked out-of-scope.

Same two-stage split as `brd_validator`: ``evaluate(...)`` is pure (score + eligibility, no I/O, no
operator outcome — a validator never auto-advances, FR-XS-13); ``record_g2(...)`` is the wiring that
stamps both ledgers for the **operator's** accept/reopen and returns the locked version (FR-XS-14:
accept → FRD pinned to BRD vN; reopen → vN+1). An ``accept`` on a non-eligible FRD is refused — the
hard coverage precondition is absolute (§9.1).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, Sequence

THRESHOLD_DEFAULT = 85

# Functional kinds whose testability artifact is **acceptance criteria** (§9.3).
ACCEPTANCE_KINDS = ("actor_flow", "system_behavior", "data_contract", "error_state")
# `nfr` requires a **measurable target** instead.
NFR_KIND = "nfr"
_VALID_KINDS = set(ACCEPTANCE_KINDS) | {NFR_KIND}
_VALID_OUTCOMES = ("accept", "reopen")


@dataclass(frozen=True)
class FrdTopic:
    """One FRD topic as parsed from `FRD.md` + the profile.

    ``traces_to`` are the BRD anchors this topic claims (a section id like ``scope_objectives`` or a
    ``section.topic`` like ``code_impact.routing``). ``has_acceptance_criteria`` /
    ``has_measurable_target`` are the testability artifacts the skill read from the section. The
    helper decides which one is *required* from ``functional_kind`` — the skill supplies both flags.
    """
    topic: str                              # qualified, e.g. "system_behaviors.routing"
    functional_kind: str
    traces_to: tuple = ()
    has_acceptance_criteria: bool = False
    has_measurable_target: bool = False

    def __post_init__(self) -> None:
        if self.functional_kind not in _VALID_KINDS:
            raise ValueError(
                f"topic {self.topic!r}: functional_kind {self.functional_kind!r} not in {sorted(_VALID_KINDS)}"
            )

    def traces_valid(self, brd_anchors: frozenset) -> bool:
        """Valid iff non-empty AND every anchor resolves to a real BRD anchor (§9.3)."""
        return bool(self.traces_to) and all(a in brd_anchors for a in self.traces_to)

    def is_testable(self) -> bool:
        """Has the testability artifact its ``functional_kind`` requires (acceptance criteria for the
        four behavioral kinds; a measurable target for ``nfr``)."""
        if self.functional_kind == NFR_KIND:
            return self.has_measurable_target
        return self.has_acceptance_criteria


@dataclass(frozen=True)
class ScoreBreakdown:
    traceability: float
    testability: float
    score: int


@dataclass(frozen=True)
class G2Result:
    breakdown: ScoreBreakdown
    threshold: int
    score_pass: bool                         # score >= threshold
    coverage_ok: bool                        # hard: every BRD req traced or out-of-scope
    invalid_traces: tuple = ()               # FRD topics whose traces_to does not resolve (lowers score)
    untestable: tuple = ()                   # FRD topics missing their required testability artifact
    untraced_requirements: tuple = ()        # BRD reqs neither traced nor out-of-scope (the G2 blockers)
    gaps: tuple = field(default=())          # remediation suggestions (FR-FR-05)

    @property
    def score(self) -> int:
        return self.breakdown.score

    @property
    def eligible(self) -> bool:
        return self.score_pass and self.coverage_ok


def _requirement_traced(req: str, valid_anchors: frozenset) -> bool:
    """A BRD requirement ``section.topic`` is traced if a valid FRD anchor names it directly OR names
    its whole ``section`` (a section-level trace covers its topics)."""
    if req in valid_anchors:
        return True
    section = req.split(".", 1)[0]
    return section in valid_anchors


def evaluate(
    *,
    frd_topics: Sequence[FrdTopic],
    brd_anchors: Sequence[str],
    brd_requirements: Sequence[str],
    out_of_scope: Sequence[str] = (),
    threshold: int = THRESHOLD_DEFAULT,
    gaps: Sequence[str] = (),
) -> G2Result:
    """Score the FRD and decide G2 eligibility — pure, model-free (§9.3).

    Args:
      frd_topics:        one :class:`FrdTopic` per FRD profile topic (with its traces + testability).
      brd_anchors:       every anchor an FRD topic may validly point at — the accepted BRD's section
                         ids AND ``section.topic`` ids (the model supplies this from the BRD/profile).
      brd_requirements:  the BRD requirement ids (``section.topic``) that must each be traced or
                         out-of-scope (the §9.3 hard rule's coverage set).
      out_of_scope:      BRD requirements explicitly marked out-of-scope in the FRD traces block.
      threshold:         the G2 score bar (default 85, §9.1).
      gaps:              remediation suggestions for the operator (FR-FR-05).

    Returns a :class:`G2Result`. No I/O, no operator outcome.
    """
    if not frd_topics:
        raise ValueError("frd_topics is empty; nothing to validate")
    anchors = frozenset(brd_anchors)

    # ── traceability: fraction of FRD topics whose traces_to all resolve. ──
    invalid = tuple(t.topic for t in frd_topics if not t.traces_valid(anchors))
    traceability = (len(frd_topics) - len(invalid)) / len(frd_topics)

    # ── testability: fraction of FRD topics carrying the artifact their kind requires. ──
    untestable = tuple(t.topic for t in frd_topics if not t.is_testable())
    testability = (len(frd_topics) - len(untestable)) / len(frd_topics)

    score = round(100 * (0.5 * traceability + 0.5 * testability))
    breakdown = ScoreBreakdown(traceability=traceability, testability=testability, score=score)

    # ── hard precondition: every BRD requirement traced (by a VALID anchor) or out-of-scope. ──
    valid_anchors = frozenset(a for t in frd_topics if t.traces_valid(anchors) for a in t.traces_to)
    oos = frozenset(out_of_scope)
    untraced = tuple(r for r in brd_requirements
                     if not _requirement_traced(r, valid_anchors) and r not in oos)

    return G2Result(
        breakdown=breakdown,
        threshold=threshold,
        score_pass=score >= threshold,
        coverage_ok=not untraced,
        invalid_traces=invalid,
        untestable=untestable,
        untraced_requirements=untraced,
        gaps=tuple(gaps),
    )


def lock_version(version: int, outcome: str) -> int:
    """FR-XS-14: accept → FRD pinned to BRD v``version`` (locked as-is); reopen → v``version+1``."""
    if outcome not in _VALID_OUTCOMES:
        raise ValueError(f"outcome must be one of {_VALID_OUTCOMES}; got {outcome!r}")
    return version if outcome == "accept" else version + 1


def record_g2(
    ledger_dir,
    *,
    result: G2Result,
    outcome: str,
    version: int,
    actor: str = "vmunjal",
    ts: str | None = None,
):
    """Wire the validator into G2: stamp both ledgers for the operator's decision (§8.1 / §3.6).

    Soft gate — the human supplies ``outcome``. An ``accept`` on a non-eligible FRD is refused: the
    coverage precondition is absolute (§9.1), so G2 cannot pass with an untraced BRD requirement.
    Writes the ``validation`` (artifact ``frd``) + ``gate_decision`` (``G2``) telemetry events and the
    ``decisions.jsonl`` ``gate`` audit record; returns the locked version.
    """
    if outcome not in _VALID_OUTCOMES:
        raise ValueError(f"outcome must be one of {_VALID_OUTCOMES}; got {outcome!r}")
    if outcome == "accept" and not result.eligible:
        raise ValueError(
            "G2 accept refused: hard precondition not met (§9.1) — "
            f"score_pass={result.score_pass} coverage_ok={result.coverage_ok} "
            f"(untraced_requirements={result.untraced_requirements})"
        )

    import telemetry  # lazy: telemetry/decisions pull in `ledger` (schema I/O)
    from pathlib import Path

    locked = lock_version(version, outcome)
    em = telemetry.Emitter(ledger_dir, run_id=_run_id(ledger_dir), domain="payment_brand",
                           tool=_runtime_tool(ledger_dir))
    em.validation(artifact="frd", score=float(result.score), ts=ts)
    em.gate_decision(gate="G2", outcome=outcome, actor=actor, version=locked, ts=ts)
    telemetry.gate(Path(ledger_dir) / "decisions.jsonl", gate="G2", outcome=outcome,
                   version=locked, actor=actor, ts=ts)
    return locked


def _run_id(ledger_dir) -> str:
    import json
    from pathlib import Path
    rs = json.loads((Path(ledger_dir) / "run_state.json").read_text(encoding="utf-8"))
    return rs.get("run_id", "unknown")


def _runtime_tool(ledger_dir, default: str = "claude") -> str:
    """Read ``runtime_tool`` from the run's immutable ``UI_INPUT.yaml`` (written verbatim at
    Generate — FR-XS-16) so G2 telemetry envelopes carry the run's actual tool (``claude`` |
    ``copilot``, §8.1 enum) instead of a hardcoded default (TASK-060). Sibling of ``ledger_dir`` —
    same read pattern as ``_run_id``. Falls back to ``default`` when no UI_INPUT.yaml is present
    (the standalone proof)."""
    import yaml
    from pathlib import Path
    ui = Path(ledger_dir).parent / "UI_INPUT.yaml"
    if not ui.exists():
        return default
    cfg = yaml.safe_load(ui.read_text(encoding="utf-8")) or {}
    return cfg.get("runtime_tool") or default


# ──────────────────────────────────────────────────────────────────────────────
# Proof (TASK-045 fixture/proof). Run: python3 core/scripts/frd_validator.py
#   Two FRDs against the accepted payment_brand BRD (its 9 requirement anchors), using the 8
#   frd_profile topics:
#     FAIL — one BRD requirement (`success_metrics.reporting`) untraced AND not out-of-scope →
#            coverage_ok=False → eligible=False even though the numeric score clears the bar
#            (the hard precondition is absolute). accept refused; reopen → v2.
#     PASS — every FRD topic traces validly + carries its testability artifact; every BRD
#            requirement traced or out-of-scope → score 100, eligible=True; accept locks FRD v1.
# ──────────────────────────────────────────────────────────────────────────────
def _demo() -> None:
    import json
    import tempfile
    from pathlib import Path

    import ledger

    T = "2026-06-22T00:00:00Z"

    # Accepted BRD v1 anchors (brd_pass.md): section ids + section.topic ids.
    BRD_SECTIONS = ["business_context", "scope_objectives", "requirements", "code_impact",
                    "success_metrics", "constraints_assumptions"]
    BRD_REQUIREMENTS = [
        "business_context.mandate", "business_context.brand_rules", "scope_objectives.card_brand",
        "requirements.certification", "requirements.interchange_fees", "code_impact.routing",
        "code_impact.settlement", "success_metrics.reporting", "constraints_assumptions.compliance_deadline",
    ]
    BRD_ANCHORS = BRD_SECTIONS + BRD_REQUIREMENTS
    # interchange_fees + compliance_deadline have no functional behavior → out-of-scope (both cases).
    OOS = ["requirements.interchange_fees", "constraints_assumptions.compliance_deadline"]

    def topics(reporting_traced: bool):
        """The 8 frd_profile topics. `reporting_traced` is the lever between the two cases."""
        reporting = FrdTopic("data_contracts.reporting", "data_contract",
                             traces_to=("success_metrics.reporting",) if reporting_traced else (),
                             has_acceptance_criteria=reporting_traced)
        return [
            FrdTopic("actor_flows.transaction_flow", "actor_flow",
                     ("scope_objectives.card_brand", "code_impact.routing"), has_acceptance_criteria=True),
            FrdTopic("system_behaviors.routing", "system_behavior",
                     ("code_impact.routing", "scope_objectives.card_brand"), has_acceptance_criteria=True),
            FrdTopic("system_behaviors.brand_rules", "system_behavior",
                     ("business_context.brand_rules", "business_context.mandate"), has_acceptance_criteria=True),
            FrdTopic("system_behaviors.settlement", "system_behavior",
                     ("code_impact.settlement",), has_acceptance_criteria=True),
            FrdTopic("data_contracts.message_format", "data_contract",
                     ("business_context.brand_rules", "business_context.mandate"), has_acceptance_criteria=True),
            reporting,
            FrdTopic("error_states.error_handling", "error_state",
                     ("code_impact.routing", "code_impact.settlement"), has_acceptance_criteria=True),
            FrdTopic("nfrs.certification", NFR_KIND,
                     ("requirements.certification",), has_measurable_target=True),  # measurable target, not AC
        ]

    # ── FAIL: reporting topic untraced + missing acceptance criteria; reporting BRD req not OOS. ──
    fail = evaluate(frd_topics=topics(reporting_traced=False), brd_anchors=BRD_ANCHORS,
                    brd_requirements=BRD_REQUIREMENTS, out_of_scope=OOS,
                    gaps=["data_contracts.reporting: add traces_to success_metrics.reporting + acceptance criteria"])
    print("FAIL case (BRD requirement `success_metrics.reporting` untraced):")
    print(f"  traceability={fail.breakdown.traceability:.3f}  testability={fail.breakdown.testability:.3f}  "
          f"score={fail.score}")
    print(f"  score_pass={fail.score_pass}  coverage_ok={fail.coverage_ok} → eligible={fail.eligible}")
    print(f"  untraced_requirements={fail.untraced_requirements}")
    assert fail.untraced_requirements == ("success_metrics.reporting",), fail.untraced_requirements
    assert not fail.coverage_ok and not fail.eligible
    # 7/8 valid traces (0.875) + 7/8 testable (0.875) → round(87.5)=88 >= 85, yet the hard rule fails.
    assert fail.score == 88 and fail.score_pass, fail
    print("  → score clears the 85 bar but the absolute coverage precondition fails (good).")

    # ── PASS: every topic traces validly + carries its testability artifact. ──
    ok = evaluate(frd_topics=topics(reporting_traced=True), brd_anchors=BRD_ANCHORS,
                  brd_requirements=BRD_REQUIREMENTS, out_of_scope=OOS)
    print("\nPASS case (every BRD requirement traced or out-of-scope):")
    print(f"  traceability={ok.breakdown.traceability:.3f}  testability={ok.breakdown.testability:.3f}  "
          f"score={ok.score}")
    print(f"  score_pass={ok.score_pass}  coverage_ok={ok.coverage_ok} → eligible={ok.eligible}")
    assert ok.score == 100 and ok.eligible, ok

    # An nfr without its measurable target is untestable, symmetric with a missing acceptance criterion.
    bad_nfr = [t for t in topics(reporting_traced=True) if t.functional_kind != NFR_KIND]
    bad_nfr.append(FrdTopic("nfrs.certification", NFR_KIND, ("requirements.certification",)))  # no target
    nfr_res = evaluate(frd_topics=bad_nfr, brd_anchors=BRD_ANCHORS, brd_requirements=BRD_REQUIREMENTS,
                       out_of_scope=OOS)
    assert nfr_res.untestable == ("nfrs.certification",), nfr_res.untestable
    print(f"\nnfr without measurable target → untestable={nfr_res.untestable} (good)")

    # ── G2 wiring against a real ledger: accept refused on FAIL; reopen → v2; PASS accept → v1. ──
    with tempfile.TemporaryDirectory(prefix="frd-validator-proof-") as tmp:
        led = ledger.init_ledger(Path(tmp) / "ledger", run_id="r-frd-001")
        try:
            record_g2(led, result=fail, outcome="accept", version=1, ts=T)
        except ValueError:
            print("\nnegative: G2 accept on untraced FRD -> REFUSED (good)")
        else:
            raise AssertionError("accept on non-eligible result must be refused")

        v2 = record_g2(led, result=fail, outcome="reopen", version=1, ts=T)
        v1 = record_g2(led, result=ok, outcome="accept", version=1, ts=T)
        assert v2 == 2 and v1 == 1, (v2, v1)
        print(f"reopen failed draft → FRD v{v2};  accept passing draft → locked FRD v{v1}")

        report = ledger.validate_ledger(led)
        assert all(not e for e in report.values()), report
        tel = [json.loads(l) for l in (led / "telemetry.jsonl").read_text().splitlines() if l.strip()]
        dec = [json.loads(l) for l in (led / "decisions.jsonl").read_text().splitlines() if l.strip()]
        val = [e for e in tel if e["event"] == "validation" and e["artifact"] == "frd"]
        gates = [e for e in tel if e["event"] == "gate_decision" and e["gate"] == "G2"]
        audit = [d for d in dec if d["kind"] == "gate" and d["gate"] == "G2"]
        assert len(val) == 2 and len(audit) == 2, (val, audit)
        assert {e["outcome"] for e in gates} == {"reopen", "accept"}, gates
        print(f"ledgers: {len(val)} validation + {len(gates)} gate_decision (G2) events, "
              f"{len(audit)} decisions.jsonl gate records — all schema-valid")

    print("\nPASS — §9.3 score is deterministic + 0.5/0.5-weighted; an untraced BRD requirement fails "
          "G2 regardless of score; nfr needs a measurable target, the four behavioral kinds need "
          "acceptance criteria; the gate never auto-advances (accept refused when ineligible); "
          "accept→vN, reopen→vN+1 (FR-FR-05, FR-XS-13/14).")


if __name__ == "__main__":
    _demo()
