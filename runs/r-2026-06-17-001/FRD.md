<!-- FRD.md — run r-2026-06-17-001 · domain payment_brand -->
<!-- pinned_brd: v2 -->
<!-- gate G2: {outcome: accept, version: 2} — pinned to accepted BRD v2 -->

# Functional Requirements — Mastercard mandate MCS-2026-R3 (routing + settlement)

Authored against **accepted BRD v2** and the deep code-impact pass. Carries the file/function-level
technical detail forward (FR-FR-03); the BRD stayed business-framed. Every functional topic traces to
a real BRD anchor (machine-checked at G2).

<!-- traces: {
  actor_flows.transaction_flow: [scope_objectives.card_brand, code_impact.routing],
  system_behaviors.routing: [code_impact.routing, scope_objectives.card_brand],
  system_behaviors.brand_rules: [business_context.brand_rules, business_context.mandate],
  system_behaviors.settlement: [code_impact.settlement],
  data_contracts.message_format: [business_context.brand_rules, business_context.mandate],
  data_contracts.reporting: [success_metrics.reporting],
  error_states.error_handling: [code_impact.routing, code_impact.settlement],
  nfrs.certification: [requirements.certification]
} -->
<!-- out_of_scope: [requirements.interchange_fees, constraints_assumptions.compliance_deadline] -->

## Actor flows

### Transaction lifecycle for in-scope Mastercard products (`transaction_flow`)

End-to-end lifecycle for an in-scope Mastercard transaction (auth → capture → settle), driven by
`src/transaction/txn_lifecycle.c` and the phase state machine in `src/transaction/txn_state.c`. The
auth phase (`auth_handler.c`) tags the transaction with its card brand and routes it; capture
(`capture_handler.c`) and settle (`settle_handler.c`) carry the brand through to settlement. Actors:
cardholder/terminal, acquiring host, Banknet, MDES gateway, settlement.

**Acceptance criteria**
- An in-scope Mastercard transaction traverses auth → capture → settle with the brand preserved at
  each phase transition.
- A token (BIN 520000–529999) transaction carries its TRID through to settlement unchanged.
- A non-Mastercard transaction follows the existing lifecycle with no behavioral change (no regression).

## System behaviors

### Per-brand routing behavior (`routing`)

Transactions are routed to the brand handler by **`src/routing/brand_router.c`** via the
routing-table lookup in `src/routing/route_table.c` / `route_table.h`, with handlers registered in
`src/routing/brand_registry.c` and dispatched through `src/routing/dispatch.c`. The new MDES
token-aware Mastercard path is added to handler selection: inputs = the brand-tagged (and possibly
tokenized) transaction; outputs = the routed handler invocation. The lookup is idempotent for a given
transaction id. Brand rule BR-01 (no acquirer de-tokenization) is enforced at the routing boundary —
the router forwards the token to Banknet without de-tokenizing.

**Acceptance criteria**
- A Mastercard token transaction is routed to the Mastercard MDES-aware handler with the token intact
  (no de-tokenization at the acquirer).
- Handler selection is idempotent: re-routing the same transaction id yields the same handler.
- A configuration with an unknown brand falls through to the existing default with no crash.

### Brand-rule enforcement (`brand_rules`)

The brand rules BR-01–BR-05 are enforced across `src/config/brand_rules.c` / `brand_rules.h` (rule
tables and macro-generated handlers) and the routing path. BR-03 contactless CVM and BR-05 Response
Code 55 redefinition are enforced where the relevant fields are evaluated. Each rule maps to an
enforcing component with an observable outcome.

**Acceptance criteria**
- BR-02: DE 48.66 (TRID) is present and unchanged on every token auth leaving the host.
- BR-05: a token-BIN decline surfaces Response Code 55 = "Token Assurance Level insufficient" with the
  cardholder message "Unable to process — please retry with chip card".

### Settlement reconciliation behavior (`settlement`)

The shared-dependency ripple the BRD brought in scope: on the settle path, `brand_router.c` calls
**`reconcile_txn()`** in `src/settlement/reconciler.c`, exercising the
`routing/brand_router → settlement/reconciler` edge. Settlement batching (`settlement_batch.c`) and
ledger posting (`ledger_post.c`) must remain correct for the new Mastercard routing path. Inputs = the
settled transaction; processing = reconciliation + batch + ledger post; outputs = the reconciled
ledger entry.

**Acceptance criteria**
- On `TXN_SETTLE`, `reconcile_txn()` is invoked exactly once per transaction id (idempotent under
  retry).
- A Mastercard token transaction reconciles to the correct ledger account with the TRID retained on the
  settlement record.

## Data contracts

### ISO 8583 message-format contract (`message_format`)

Field-level wire-format changes from MCS-2026-R3 Part 2, implemented in `src/messaging/iso8583.c`,
`field_codec.c`, and `formatter.c` against `codec.h`. New/changed data elements: **DE 48.66** (Token
Requestor ID), **DE 48.77** (wallet/device data), **DE 48.78** (token assurance data). The codec adds
encode/decode for these subfields; existing fields are unchanged.

**Acceptance criteria**
- DE 48.66/48.77/48.78 encode and decode round-trip losslessly for a token transaction.
- A non-token transaction serializes byte-identically to the pre-change codec (no regression).

### Reporting / downstream data contract (`reporting`)

DSR and Reg II reporting records emitted downstream must include the token and routing attributes
required by the mandate. Fields: brand, token indicator, TRID, routed handler, settlement disposition;
destination = the DSR/Reg II reporting sink; timing = per existing settlement batch cadence.

**Acceptance criteria**
- Every settled in-scope Mastercard transaction emits a DSR record carrying the token indicator and
  routed handler.
- Reg II debit records reflect the routing decision for dual-routed debit transactions.

## Error states

### Failure modes for the changed paths (`error_handling`)

Failure handling for the routing and settlement changes, implemented in `src/errors/error_codes.c`,
`retry.c`, and `fallback.c`. BR-04: a primary Banknet no-response within 4000 ms triggers a secondary
endpoint attempt (logged reason code T); a secondary timeout forwards to STIP rather than declining at
the host. Reconciliation failures on the settle path surface a retryable error without double-posting.

**Acceptance criteria**
- A primary Banknet timeout at 4000 ms attempts the secondary endpoint, then STIP — never an immediate
  host decline.
- A `reconcile_txn()` failure is retried without producing a duplicate ledger entry (idempotent retry).
- A token-assurance failure returns Response Code 55 with the BR-05 cardholder message.

## NFRs

### Certification / conformance target (`certification`)

Mastercard Acquirer Certification **MAC Level 2** is the measurable conformance target. **Measurable
target:** Gate C1 functional pass rate **100% Category A and ≥85% Category B** on MTS v8.4; Gate C2
**1,000** end-to-end interoperability traces accepted (≥300 MDES token, ≥100 fallback chip, ≥50 Reg II
debit); Gate C3 **60-day** production validation with token decline-rate and DE 48.77 coverage within
Mastercard thresholds. Target completion before **2026-09-30**.

## Traceability

Every BRD requirement is either traced by a functional topic above or explicitly out of scope:

- Traced: `business_context.mandate`, `business_context.brand_rules`, `scope_objectives.card_brand`,
  `requirements.certification`, `code_impact.routing`, `code_impact.settlement`,
  `success_metrics.reporting`.
- **Out of scope** (pure BRD business/compliance facts with no functional behavior):
  `requirements.interchange_fees` (interchange qualification is a business/fee fact, no system
  behavior in this service) and `constraints_assumptions.compliance_deadline` (a date constraint, not
  a function).
