# `frd_validator` fixtures — G2 fail/pass proof (TASK-045)

Two FRDs validated against the **accepted BRD v1** (`fixtures/brd_validator/brd_pass.md`, locked at
G1) using the 8 `frd_profile.payment_brand.yaml` topics. They make the §9.3 score + the absolute
coverage precondition concrete; the **runnable** proof that the arithmetic and the verdict follow is
`core/scripts/frd_validator.py`'s `_demo()` (`python3 core/scripts/frd_validator.py`), which encodes
exactly the two cases below.

The validator (the skill) parses `FRD.md`'s `traces_to` + `<!-- traces: {...} -->` block +
per-section `functional_kind` + testability artifacts into `FrdTopic`s; the helper resolves anchors
(set membership) and computes the score + `eligible`.

**The 9 BRD requirements** (from `brd_pass.md`): `business_context.{mandate,brand_rules}`,
`scope_objectives.card_brand`, `requirements.{certification,interchange_fees}`,
`code_impact.{routing,settlement}`, `success_metrics.reporting`,
`constraints_assumptions.compliance_deadline`. `interchange_fees` + `compliance_deadline` have no
functional behavior → **out-of-scope** in both cases (the §9.3 out-of-scope arm).

## `frd_fail.md` — one BRD requirement untraced → **must fail G2**

- The `data_contracts.reporting` FRD topic is **untraced** (its `traces_to` to
  `success_metrics.reporting` is missing) and carries **no acceptance criteria**; `success_metrics.reporting`
  is **not** marked out-of-scope.
- → `traceability = 7/8 = 0.875`, `testability = 7/8 = 0.875`,
  `score = round(100*(0.5*0.875 + 0.5*0.875)) = 88`.
- **Verdict:** `score_pass=True` (88 ≥ 85) **but** `coverage_ok=False` — `success_metrics.reporting`
  is neither traced nor out-of-scope → `eligible=False`. This is the key demonstration: **the hard
  coverage precondition is absolute**, so a clean numeric score does not save an untraced BRD
  requirement. A G2 `accept` is **refused**; the operator **reopens** → FRD **v2**.

## `frd_pass.md` — every BRD requirement traced or out-of-scope → **must pass G2**

- All 8 FRD topics trace validly to real BRD anchors and carry their testability artifact
  (acceptance criteria for the four behavioral kinds; a **measurable target** for `nfrs.certification`).
  Every BRD requirement is traced by ≥1 FRD topic, except the two out-of-scope facts.
- → `traceability = 1.00`, `testability = 1.00`, `score = 100`.
- **Verdict:** both preconditions hold → `eligible=True`. Operator **accepts** → `FRD.md` locked,
  pinned to BRD v1; `validation` (artifact `frd`) + `gate_decision` (`G2`) telemetry + the
  `decisions.jsonl` `gate` record are stamped.

The lever between the two is a single topic's trace (`data_contracts.reporting` traced vs not) — the
same lever the demo flips. The demo also shows an `nfr` missing its measurable target is `untestable`,
symmetric with a behavioral topic missing acceptance criteria.

`frd_pass.md` is the same content as `fixtures/frd_author/expected_frd.md` (the TASK-044 output),
closing the loop: `frd_author` produces it, `frd_validator` passes it.
