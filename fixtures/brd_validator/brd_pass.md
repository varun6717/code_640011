<!-- brd_validator fixture: PASS case (TASK-043). Every required topic satisfied.
     Maps to core/scripts/brd_validator.py _demo() PASS case: score 100, eligible=True.
     Substantive claims: 25 total, 25 cited. No undispositioned code_impact flag. -->

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

The mandate affects the **authorization-routing service and the Mastercard brand-handler dispatch
flow** [src: bitbucket/stratus-c/routing/brand_dispatch.c]; the change is **medium scale** — the
routing-table lookup and handler selection paths — and **medium risk** given the certification
dependency [src: bitbucket/stratus-c/routing/brand_dispatch.c]. A shared-dependency ripple into the
settlement reconciler was surfaced and **dispositioned as out-of-scope** by the operator [operator].
(All code-impact flags are resolved in `decisions.jsonl`.)

<!-- coverage: {routing: source, settlement: operator} -->

## Success metrics

Routing-conformance pass rate and post-cutover authorization approval rate are the success signals
[src: confluence/metrics_2026.md].

<!-- coverage: {reporting: source} -->

## Constraints & assumptions

Delivery is bounded by the **2026-10-01** compliance date; the certification window opens 2026-08
[src: sharepoint/mastercard_mandate_part1_2026.md].

<!-- coverage: {compliance_deadline: source} -->

## Out of scope

Consumer prepaid routing and non-Mastercard brands are out of scope [frame].

## Executive summary

This BRD covers the Mastercard 2026 routing-mandate implementation for commercial credit/debit,
gated by a 2026-10-01 compliance deadline and brand recertification [src:
sharepoint/mastercard_mandate_part1_2026.md]. The code-impact routing scope is grounded to the
brand-dispatch service and the one shared-dependency ripple is dispositioned [operator].
