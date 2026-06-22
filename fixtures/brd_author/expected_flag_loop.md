# Expected flag loop — `brd_author` GF proof (TASK-042)

Proof for § "Human-mediated flag loop (GF)" in `core/skills/brd_author.skill.md` (FR-BR-08, FR-BR-13,
D6c). Takes the one flag `code_impact` returned in TASK-041
(`fixtures/code_impact/expected_deep_flags.md`) and shows the **same flag** resolving **material** under
one operator choice and **advisory** under another — i.e. the operator's decision confirms severity.

**Returned flag (from TASK-041, proposed `severity: material`)**
- `type: scope_ripple`, `area: settlement/reconciler`, `requirement_ref: code_impact.routing`
- finding: brand routing is statically wired to settlement reconciliation
- options: `[include settlement in scope, phase separately, adjust requirement, accept risk]`
- recommended_option: `include settlement in scope`

The loop surfaces it **once, with the recommendation**, and waits — no scope change is auto-applied.

---

## Scenario A — MATERIAL (operator: "include settlement in scope")

- **Classify (D6c):** adds the `settlement` module to the in-scope set → **changes the impacted code
  surface** → **material** (confirms the proposed severity).
- **Apply:** revise Scope & objectives (settlement now in scope), the Requirements section
  (`settlement` topic raised), and the code-impact section — including the earlier scope section
  (revisit rule).
- **Re-run (FR-BR-13):** re-run `code_impact` **scoped to the changed surface only** = the `settlement`
  modules just added — not the whole map. Fold any new flags back into the loop.
- **Ledger + telemetry:**
  ```
  decisions.flag(ledger, flag_type="scope_ripple", area="settlement/reconciler",
                 option="include settlement in scope", severity="material",
                 rationale="Settlement shares the brand-rule path; in-scope per ops.", actor="vmunjal")
  telemetry.flag_decision(flag_type="scope_ripple", option="include settlement in scope",
                          severity="material")
  ```

## Scenario B — ADVISORY (operator: "accept risk")

- **Classify (D6c):** does **not** add/remove a module, does **not** change a relied-on `must_capture`,
  does **not** move a Scope/Out-of-scope boundary → **advisory** (downgrades the proposed `material`).
- **Apply:** record the decision + rationale; note the residual risk in the code-impact section. **No**
  scope/boundary change.
- **Re-run:** **none** (advisory).
- **Ledger + telemetry:**
  ```
  decisions.flag(ledger, flag_type="scope_ripple", area="settlement/reconciler",
                 option="accept risk", severity="advisory",
                 rationale="Ripple acknowledged; settlement change deferred, risk accepted by ops.",
                 actor="vmunjal")
  telemetry.flag_decision(flag_type="scope_ripple", option="accept risk", severity="advisory")
  ```

---

**Checks demonstrated**
- **No auto-applied scope change** (FR-BR-08): both paths require an operator decision; the loop surfaces
  → waits → applies.
- **Severity confirmed by the operator** (D6c): the same proposed-`material` flag becomes `material` (A)
  or `advisory` (B) by the option chosen — the three-line test, not the proposal, decides.
- **Re-run only when material, scoped to the changed surface** (FR-BR-13): A re-runs over only the added
  `settlement` modules; B never re-runs.
- **Audited** (§3.6 / §8.1): every disposition writes a `decisions.jsonl` `flag` record + a
  `flag_decision` telemetry event, both carrying the operator's `option` + confirmed `severity`.
- **G1 is the backstop** for any flag not surfaced here.
