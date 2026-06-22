<!-- brd_validator fixture: FAIL case (TASK-043). routing required topic left `open`.
     Maps to core/scripts/brd_validator.py _demo() FAIL case: score 84, eligible=False.
     Substantive claims: 25 total, 23 cited (two `[TBD — unsourced]`). -->

## Business context

This work is triggered by the **Mastercard 2026 routing mandate (ID MC-2026-ROUTE)** [src:
sharepoint/mastercard_mandate_part1_2026.md], with a hard compliance deadline of **2026-10-01**
[src: sharepoint/mastercard_mandate_part1_2026.md]. The mandate constrains how authorization
traffic is routed to brand handlers and requires conformance to the brand's updated routing rules
[src: confluence/brand_rules_routing_2026.md].

<!-- coverage: {mandate: source, brand_rules: source} -->

## Scope & objectives

The change concerns **Mastercard credit and debit** products across the commercial segment [src:
confluence/scope_2026.md]; consumer prepaid is out of scope for this release [frame].

<!-- coverage: {card_brand: source} -->

## Requirements

The implementation must pass **brand certification suite CRT-2026.2** and triggers a
**recertification** of the routing path [src: confluence/cert_requirements_2026.md]. Interchange
qualification criteria are unchanged by this mandate [src: confluence/cert_requirements_2026.md].

<!-- coverage: {certification: frame, interchange_fees: source} -->

## Code impact

The mandate touches the transaction-routing surface, but the **specific affected brand-handler
flows, their scale, and the change risk are not yet established** — the code-impact pass returned
candidate areas only and the routing detail remains `[TBD — unsourced]`. Settlement behavior is
unaffected `[TBD — unsourced]`.

<!-- coverage: {routing: open, settlement: open} -->

## Success metrics

Routing-conformance pass rate and post-cutover authorization approval rate are the success signals
[src: confluence/metrics_2026.md].

<!-- coverage: {reporting: source} -->

## Constraints & assumptions

Delivery is bounded by the **2026-10-01** compliance date; the assumption is that the brand's
certification window opens by 2026-08 [src: sharepoint/mastercard_mandate_part1_2026.md].

<!-- coverage: {compliance_deadline: source} -->

## Out of scope

Consumer prepaid routing and non-Mastercard brands are out of scope [frame].

## Executive summary

This BRD covers the Mastercard 2026 routing-mandate implementation for commercial credit/debit,
gated by a 2026-10-01 compliance deadline and brand recertification [src:
sharepoint/mastercard_mandate_part1_2026.md]. **The code-impact routing scope is still open and
must be grounded before G1.**
