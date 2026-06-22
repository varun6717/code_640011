<!-- frd_author fixture: expected FRD.md excerpts (TASK-044).
     Authored against accepted BRD v1 (fixtures/brd_validator/brd_pass.md) + deep detail
     (fixtures/code_impact/expected_deep_flags.md). Proof-bearing sections only — not a full FRD. -->
<!-- pinned_brd: v1 -->

# Functional Requirements — Mastercard 2026 routing mandate

<!-- (header pins the accepted BRD: G1 gate record {outcome: accept, version: 1}) -->

## System behaviors

### Routing (per-brand routing behavior)

Transactions for the in-scope Mastercard commercial credit/debit products are routed to the brand
handler by **`src/routing/brand_router.c`**: the router reads the brand path and selects the handler
via the routing-table lookup. On the settle path (`TXN_SETTLE`) `brand_router.c` calls
**`reconcile_txn()`**, exercising the `routing/brand_router → settlement/reconciler` dependency — the
shared-dependency ripple the BRD agreed to bring in scope. The new Mastercard routing path is added to
the handler-selection logic; inputs = the brand-tagged transaction, outputs = the routed handler
invocation; the lookup is idempotent for a given transaction id.

**Acceptance criteria**
- A Mastercard commercial transaction is routed to the Mastercard brand handler (no fallback path).
- On `TXN_SETTLE`, `reconcile_txn()` is invoked exactly once per transaction (idempotent).
- An unchanged (non-Mastercard) transaction routes exactly as before (no regression).

<!-- traces: {system_behaviors.routing: [code_impact.routing, scope_objectives.card_brand]} -->

### Settlement (reconciliation behavior)

`settlement/reconciler.c` `reconcile_txn()` processes the settle path pulled in by the routing change;
the brand-routing change exercises reconciliation for the new path. Inputs = the settled transaction;
outputs = the reconciliation record. Shared-dependency ripple carried forward from code-impact.

**Acceptance criteria**
- Each Mastercard settled transaction produces exactly one reconciliation record.
- A reconciliation failure does not drop the routing result (see Error states).

<!-- traces: {system_behaviors.settlement: [code_impact.settlement]} -->

## Error states

On the changed routing+settlement path: a brand-handler selection failure returns
`ROUTE_ERR_NO_HANDLER` (no silent fallback); a `reconcile_txn()` failure on `TXN_SETTLE` returns
`SETTLE_ERR_RECONCILE` and the transaction is retried per the existing retry policy, with the routing
result preserved. Observable signal: both error codes are emitted to the routing log.

**Acceptance criteria**
- A missing Mastercard handler yields `ROUTE_ERR_NO_HANDLER`, never a default-handler route.
- A reconcile failure yields `SETTLE_ERR_RECONCILE` and a retry; the routed handler result is not lost.

<!-- traces: {error_states.error_handling: [code_impact.routing, code_impact.settlement]} -->

## NFRs

### Certification (measurable conformance target)

The implementation MUST pass **brand certification suite CRT-2026.2** at the brand's published pass
threshold (100% of mandatory conformance cases), and the routing-path change triggers
**recertification** of the routing conformance profile before cutover.

**Measurable target:** CRT-2026.2 mandatory-case pass rate = 100%; recertification completed before
the 2026-10-01 compliance date. *(nfr → measurable target, not acceptance criteria, per §9.3.)*

<!-- traces: {nfrs.certification: [requirements.certification]} -->

## Traceability

<!-- traces: {
  actor_flows.transaction_flow: [scope_objectives.card_brand, code_impact.routing],
  system_behaviors.routing:     [code_impact.routing, scope_objectives.card_brand],
  system_behaviors.brand_rules: [business_context.brand_rules, business_context.mandate],
  system_behaviors.settlement:  [code_impact.settlement],
  data_contracts.message_format:[business_context.brand_rules, business_context.mandate],
  data_contracts.reporting:     [success_metrics.reporting],
  error_states.error_handling:  [code_impact.routing, code_impact.settlement],
  nfrs.certification:           [requirements.certification],
  out_of_scope:                 [requirements.interchange_fees, constraints_assumptions.compliance_deadline]
} -->

Every BRD requirement is traced by ≥1 FRD topic, except `interchange_fees` and `compliance_deadline`
— pure business/compliance facts with no functional behavior — explicitly marked **out-of-scope**
(satisfying the §9.3 G2 hard rule). `mandate` and `card_brand` have no FRD section of their own but
are **traced-from** (anchors above), so they are covered.
