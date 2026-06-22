# Expected grounding / cite-or-flag — `brd_author` proof (TASK-039)

Proof for § "Grounding & citation — cite-or-flag" (FR-BR-06) and the coverage footer (§3.7) in
`core/skills/brd_author.skill.md`. Shows a drafted section where one `must_capture` is grounded in a
source and one is **unsourced → marked `[TBD — unsourced]`**, with the footer agreeing.

**Setup**
- Section: `business_context` (payment_brand profile), topics `mandate` (required) + `brand_rules`.
- Routed source (per `expected_routing.md`): `P1` =
  `sharepoint/mastercard_mandate_part1_2026.md`, topics include `mandate, brand_rules`.
- Scenario: `P1` names the mandate, its ID, and the deadline, but does **not** state the brand
  technical/operational rules; the operator has not yet been asked. → `mandate` is `source`-grounded;
  `brand_rules` is unsatisfied by source and frame and so far un-probed.

**Expected drafted section in `BRD.md`**

```markdown
## Business context

This work is triggered by the Mastercard 2026 routing mandate (ID MC-2026-ROUTE), with a
compliance deadline of 2026-09-30 [src: sharepoint/mastercard_mandate_part1_2026.md]. The
program scope confirmed at intake is brand-routing conformance for the merchant routing
service [frame].

Brand technical/operational rules constraining the implementation: [TBD — unsourced]

<!-- coverage: {mandate: source, brand_rules: open} -->
```

**Checks demonstrated**
- Cite-or-flag (FR-BR-06): every substantive claim carries an inline tier tag — `[src: …]` for the
  source-grounded mandate facts, `[frame]` for the intake-confirmed scope.
- The unsourced `brand_rules` `must_capture` is **marked `[TBD — unsourced]`, not invented** — surfacing
  the gap is the correct outcome.
- Footer agrees with the citations: `mandate: source`, `brand_rules: open` (the open entry the
  `brd_validator` reads as an unmet topic, and the trigger to probe `probe_if_missing` for `brand_rules`
  on a later pass — without ever re-asking `mandate`, FR-BR-05).
- `brand_rules` is `required: false` in the profile, so this section can still progress; were it
  required, the open topic would block G1 until probed or accepted.
