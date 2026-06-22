# `brd_validator` fixtures — G1 fail/pass proof (TASK-043)

Two BRD drafts against the `payment_brand` required-topic set
`{mandate, card_brand, certification, routing, compliance_deadline}` (from
`core/profiles/payment_brand/brd_profile.payment_brand.yaml`). They make the §9.2 score + the
absolute hard preconditions concrete at the artifact level; the **runnable** proof that the
arithmetic and the verdict follow from these signals is `core/scripts/brd_validator.py`'s `_demo()`
(`python3 core/scripts/brd_validator.py`), which encodes exactly the two cases below.

The validator (the skill) parses each BRD's `<!-- coverage: {...} -->` footers + inline citations
into `TopicResult`s + claim counts; the helper computes the score and `eligible`. These fixtures show
what the model reads; the demo shows what the helper does with it.

## `brd_fail.md` — one required topic unsatisfied → **must fail G1**

- `routing` (required) is left **`open`** — its `must_capture` is `[TBD — unsourced]` (the
  code-impact routing detail was never grounded). The other four required topics are satisfied.
- Substantive claims: 25 total, 23 cited (two `[TBD — unsourced]`).
- → `topic_coverage = 4/5 = 0.80`, `citation_integrity = 23/25 = 0.92`,
  `score = round(100*(0.7*0.80 + 0.3*0.92)) = 84`.
- **Verdict:** `score_pass=False` (84 < 85) **AND** `required_satisfied=False` (routing `open`) →
  `eligible=False`. A G1 `accept` is **refused**; the operator **reopens** → BRD **v2**, and the
  `routing` gap goes back to `brd_author` for in-chat fill-in.

## `brd_pass.md` — every required topic satisfied → **must pass G1**

- All five required topics grounded (`routing` now `source`-grounded after the code-impact pass);
  every substantive claim cited (25/25); no undispositioned `code_impact` flag in `decisions.jsonl`.
- → `topic_coverage = 1.00`, `citation_integrity = 1.00`, `score = 100`.
- **Verdict:** all three preconditions hold → `eligible=True`. Operator **accepts** → `BRD.md`
  locked as **BRD v1**; `validation` + `gate_decision` telemetry + the `decisions.jsonl` `gate`
  record are stamped.

The lever between the two is a single footer value (`routing: open` vs `routing: source`) — the same
lever the demo flips — proving an unsatisfied required topic fails G1 *regardless of how close the
score is*, and (separately, in the demo's third case) that one unresolved flag fails G1 even at 100.
