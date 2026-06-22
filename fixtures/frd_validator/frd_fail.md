<!-- frd_validator fixture: FAIL case (TASK-045). data_contracts.reporting untraced.
     Maps to core/scripts/frd_validator.py _demo() FAIL case: score 88, coverage_ok=False, eligible=False.
     Proof-bearing excerpts only — the lever vs frd_pass.md is the data_contracts.reporting topic. -->
<!-- pinned_brd: v1 -->

# Functional Requirements — Mastercard 2026 routing mandate

## Data contracts

### Message format

Field-level wire-format contract for the Mastercard routing message: the brand-routing indicator
field is added; types and required/optional flags per the brand spec, with conformance acceptance
criteria.

**Acceptance criteria**
- The routing-indicator field is present and typed per CRT-2026.2 on every Mastercard message.

<!-- traces: {data_contracts.message_format: [business_context.brand_rules, business_context.mandate]} -->

### Reporting

<!-- DEFECT (the lever): this topic's behavior is drafted, but its traces_to is MISSING and it
     carries NO acceptance criteria. success_metrics.reporting is therefore left untraced, and it is
     NOT in the out_of_scope set below. -->
The change emits a settlement-reconciliation record downstream, but the record fields, destination,
and the BRD success-metric this satisfies are `[TBD — unsourced]`.

<!-- traces: {} -->

## Traceability

<!-- traces: {
  actor_flows.transaction_flow: [scope_objectives.card_brand, code_impact.routing],
  system_behaviors.routing:     [code_impact.routing, scope_objectives.card_brand],
  system_behaviors.brand_rules: [business_context.brand_rules, business_context.mandate],
  system_behaviors.settlement:  [code_impact.settlement],
  data_contracts.message_format:[business_context.brand_rules, business_context.mandate],
  error_states.error_handling:  [code_impact.routing, code_impact.settlement],
  nfrs.certification:           [requirements.certification],
  out_of_scope:                 [requirements.interchange_fees, constraints_assumptions.compliance_deadline]
} -->

<!-- data_contracts.reporting is absent above (untraced); success_metrics.reporting appears in NO
     topic's traces_to and is NOT in out_of_scope → the §9.3 hard rule is broken. -->

**Validator verdict:** traceability = 7/8 = 0.875, testability = 7/8 = 0.875 → score = 88 (clears the
85 bar), **but** `success_metrics.reporting` is neither traced nor out-of-scope → `coverage_ok=False`
→ **G2 ineligible**. A G2 accept is refused; the operator reopens → FRD v2, and `frd_author` adds the
`data_contracts.reporting` trace + acceptance criteria (or marks the requirement out-of-scope).
