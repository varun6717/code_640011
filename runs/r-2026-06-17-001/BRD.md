<!-- BRD.md — run r-2026-06-17-001 · domain payment_brand · ACCEPTED BRD v2 -->
<!-- gate G1: {outcome: accept, version: 2} — v1 was reopened to bring the settlement
     shared-dependency ripple in scope (material flag, GF); see ledger/decisions.jsonl -->
<!-- section order = D2 merged baseline+profile plan; executive_summary drafted LAST -->

## Business context

This work is triggered by the **Mastercard brand mandate MCS-2026-R3** (Approved-Final v1.2)
[src: sharepoint/mastercard_mandate_part1_2026.md], which is binding on all Mastercard-licensed
acquirers including JPMC Merchant Services and requires support for **MDES token-based
transactions**, revised interchange qualification, and enhanced Banknet routing
[src: sharepoint/mastercard_mandate_part1_2026.md]. It supersedes circular MCS-2024-R7 for MDES
token routing and interchange qualification [src: sharepoint/mastercard_mandate_part1_2026.md]. The
hard **compliance deadline is 2026-09-30** [src: sharepoint/mastercard_mandate_part1_2026.md]. The
mandate carries five binding brand rules (BR-01–BR-05): no acquirer de-tokenization of MDES tokens
(BR-01), preservation of the Token Requestor ID in DE 48.66 through the auth chain (BR-02),
contactless CVM per EMV Kernel C-3 above USD 100 (BR-03), a 4000 ms Banknet timeout with STIP
fallback (BR-04), and a redefined Response Code 55 on token BINs (BR-05)
[src: sharepoint/mastercard_mandate_part1_2026.md].

<!-- coverage: {mandate: source, brand_rules: source} -->

## Scope & objectives

The change concerns the **Mastercard** card brand — Mastercard Credit (all tiers), Debit Mastercard,
Maestro, and Mastercard Commercial [src: sharepoint/mastercard_mandate_part1_2026.md]. In-scope BIN
ranges are 510000–559999 and 600000–699999, with token BINs 520000–529999 in scope for MDES token
processing [src: sharepoint/mastercard_mandate_part1_2026.md]. **Prepaid Mastercard is excluded** from
the MDES token requirements [src: sharepoint/mastercard_mandate_part1_2026.md]. The objective is to
make the in-scope Mastercard products conformant with MCS-2026-R3 end-to-end before the deadline
[frame].

<!-- coverage: {card_brand: source} -->

## Stakeholders

Payments Engineering owns the routing and settlement changes; Brand Compliance owns the Mastercard
certification relationship [frame]. JPMC Merchant Tech, QA, and Ops carry the milestone deliverables
named in the mandate timeline [src: sharepoint/mastercard_mandate_part1_2026.md]. The requestor is
Varun Munjal (Merchant Services) [operator].

## Current state

Today the merchant-routing-svc dispatches authorization traffic to brand handlers and reconciles
settled transactions without MDES token-aware routing or the MCS-2026-R3 message-format additions
[operator]. The service is a single Stratus C repository (`merchant-routing-svc`, SEAL-PBI-0001) with
routing, settlement, transaction, messaging, errors, and config modules [src: code_map.json].

## Requirements

The implementation must pass **Mastercard Acquirer Certification (MAC) Level 2** before the deadline,
across three gates: C1 functional (MTS v8.4), C2 interoperability (1,000 end-to-end traces), and C3
60-day production validation [src: sharepoint/mastercard_mandate_part1_2026.md]. Non-achievement of
MAC L2 by 2026-09-30 downgrades all Mastercard/Maestro transactions to the Standard non-qualified
interchange tier with a 90-day remediation window [src: sharepoint/mastercard_mandate_part1_2026.md].
The mandate revises **interchange qualification** with token-enhanced rate tiers that the in-scope
products must qualify for [src: sharepoint/mastercard_mandate_part2_2026.md].

<!-- coverage: {certification: source, interchange_fees: source} -->

## Code impact

Business-framed assessment from the `code_impact` subagent over the pinned repo (SEAL-PBI-0001 @
e94c70d) [src: code_map.json]. The mandate's routing changes land in the **routing** module — the
brand-handler dispatch and routing tables that select a handler per card brand
[src: code_map.json]. The change surface is moderate (the routing module plus its shared
configuration) and the risk is medium: routing is on the live authorization path
[src: code_map.json].

The deep pass surfaced one **material shared-dependency ripple**: brand routing is statically wired to
**settlement reconciliation** — the router invokes settlement reconciliation on the settle path, so a
change to a card-brand routing path also exercises settlement [src: code_map.json]. This was raised as
a scope-ripple flag (GF), and the operator decided to **bring settlement into scope** for this release
[operator]; the impact assessment was re-run over the expanded routing+settlement surface
[operator]. Settlement impact is therefore in scope: the reconciliation path must remain correct and
idempotent for the new Mastercard routing path [src: code_map.json]. (File- and function-level detail
is carried forward to the FRD, not stated here.)

<!-- coverage: {routing: source, settlement: source} -->

## Success metrics

Success is confirmed by the mandate's reporting obligations: Dispute Settlement Reporting (DSR) and
Reg II reporting must reflect the new token and routing behavior
[src: sharepoint/mastercard_mandate_part2_2026.md]. Measurable signals are MAC L2 gate pass rates
(Gate C1 100% Category A / 85% Category B) and the Gate C3 token decline-rate and DE 48.77 coverage
monitors [src: sharepoint/mastercard_mandate_part1_2026.md].

<!-- coverage: {reporting: source} -->

## Constraints & assumptions

The hard **compliance deadline is 2026-09-30**; all milestones (MTS harness 2026-04-15, Gate C1
2026-06-15, Gate C2 2026-07-31, PROD 2026-09-01, Gate C3 start 2026-09-01) are constrained by it
[src: sharepoint/mastercard_mandate_part1_2026.md]. It is assumed the MTS v8.4 test harness and
Mastercard Connect access are provisioned on schedule [src: sharepoint/mastercard_mandate_part1_2026.md].

<!-- coverage: {compliance_deadline: source} -->

## Out of scope

Prepaid Mastercard MDES token processing is out of scope [src: sharepoint/mastercard_mandate_part1_2026.md].
Non-Mastercard card brands are out of scope for this mandate [frame]. No Jira epic creation is in scope
for this slice — this run produces BRD and FRD only [operator].

## Executive summary

Mastercard mandate **MCS-2026-R3** requires JPMC Merchant Services to make its in-scope Mastercard
products (Credit, Debit Mastercard, Maestro, Commercial) conformant with MDES token-based processing,
revised interchange qualification, and enhanced Banknet routing, and to achieve **MAC Level 2**
certification by the hard **2026-09-30** deadline [src: sharepoint/mastercard_mandate_part1_2026.md].
The change lands primarily in the routing module and — per the code-impact flag loop — also brings
**settlement reconciliation** in scope because brand routing is statically wired to it
[src: code_map.json]. Failure to certify in time downgrades Mastercard volume to non-qualified
interchange [src: sharepoint/mastercard_mandate_part1_2026.md], making on-time delivery the dominant
business driver [frame].
