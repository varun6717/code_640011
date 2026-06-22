<!-- provenance: source=pdf · url=fixtures/pdf/mastercard_mandate_part1_2026.pdf -->
<!-- pipeline: pdf_extract (structure) → article_summarize (summary + topics) → change_type_assess (change_type + topics) -->

# Article Summary (article_summarize)

**Mastercard brand mandate MCS-2026-R3, Part 1 of 2** (Mandate Overview, Brand Rules &
Certification). Issued by Mastercard International Incorporated; binding on all Mastercard-licensed
acquirers including JPMC Merchant Services. Requires acquirers to support **MDES token-based
transactions**, revised interchange qualification, and enhanced Banknet routing for Debit Mastercard
and Maestro. Supersedes circular MCS-2024-R7 for MDES token routing and interchange qualification.

- **Mandate:** MCS-2026-R3 (Approved-Final, v1.2). **Compliance deadline: 2026-09-30.**
- **Affected card brands:** Mastercard Credit (all tiers), Debit Mastercard, Maestro, Mastercard
  Commercial. Prepaid excluded from MDES token requirements. In-scope BINs 510000–559999,
  600000–699999; token BINs 520000–529999.
- **Brand rules (BR-01–BR-05):** no acquirer de-tokenization (BR-01); preserve TRID in DE 48.66 (BR-02);
  contactless CVM per MCK C-3 above USD 100 (BR-03); Banknet timeout/STIP fallback at 4000ms (BR-04);
  Response Code 55 now = "Token Assurance Level insufficient" on token BINs (BR-05).
- **Certification:** Mastercard Acquirer Certification (MAC) **Level 2** required before the deadline —
  Gate C1 functional (MTS v8.4), Gate C2 interoperability, Gate C3 60-day production validation.
  Non-achievement by 2026-09-30 → downgrade to Standard non-qualified interchange + 90-day remediation.

_Topics (article_summarize): brand_rules, mandate. Part 2 (MCS-2026-R3-T) carries the message-format,
interchange, and routing detail._

---

# Mastercard International Incorporated — Brand Implementation Mandate (structural extraction)

- **Mandate ID:** MCS-2026-R3 — Part 1 of 2: Mandate Overview, Brand Rules & Certification
- **Applicable Card Brand:** Mastercard (incl. Maestro, Debit Mastercard)
- **Version:** 1.2 · **Status:** Approved-Final · **Compliance Deadline:** 2026-09-30

## 1. Mandate Summary

Part 1 of 2 for Mastercard brand mandate MCS-2026-R3 — covers rationale, brand rules, and
certification. Part 2 (MCS-2026-R3-T) contains the technical implementation specification (ISO 8583
message-format changes, revised interchange fee schedules, Banknet routing updates). Both parts are a
single binding requirement.

Issued under the Mastercard Rules and the Mastercard Security Rules and Procedures; binding on all
Mastercard-licensed acquirers, including JPMC Merchant Services. Requires support for Mastercard
Digital Enablement Service (MDES) token-based transactions, revised interchange qualification criteria,
and enhanced Banknet routing logic for Debit Mastercard and Maestro. Full compliance by 2026-09-30.
Supersedes circular MCS-2024-R7 for MDES token routing and interchange qualification.

## 2. Scope and Affected Card Brands

- Mastercard Credit — all tiers (Standard, World, World Elite, Corporate)
- Debit Mastercard — US and international debit products
- Maestro — PIN debit, international card-present
- Mastercard Commercial — purchasing, fleet, and business cards

Prepaid Mastercard excluded from MDES token requirements (still subject to Part 2 interchange/routing
changes). In-scope BIN ranges: 510000–559999 (Credit/Debit), 600000–699999 (Maestro); token BINs
520000–529999 in scope for MDES token processing.

## 3. Brand Rules and Operational Constraints

- **BR-01 — MDES token handling.** Acquirers MUST NOT de-tokenize MDES tokens before forwarding auth
  to Banknet; de-tokenization is MDES's responsibility at the Banknet gateway. Stripping/substituting
  tokens → decline Response Code 14 ("Invalid card number").
- **BR-02 — TRID preservation.** Token Requestor IDs MUST be preserved in DE 48.66 through the full
  auth chain. Mobile-wallet sources (Apple/Google/Samsung Pay) MUST populate DE 48.66 + DE 48.77.
- **BR-03 — Cardholder verification.** Contactless above USD 100.00 MUST request CVM per EMV
  Contactless Kernel C-3 (MCK). CVM priority: Online PIN → Offline Enciphered PIN → Signature. NOCVM
  only for transit/toll MCCs 4111/4121/4131/7523. CVM result in DE 55 Tag 9F34.
- **BR-04 — Authorization timeout/fallback.** Primary Banknet no-response within 4000ms → MAY attempt
  secondary endpoint; fallback logged with reason code T. On secondary timeout, MUST forward to STIP
  rather than decline at the acquiring host.
- **BR-05 — Decline reason code updates.** Response Code 55 on MDES token transactions (BIN
  520000–529999) now = "Token Assurance Level insufficient" (legacy: "Incorrect PIN"). Host + decline
  engines MUST display "Unable to process — please retry with chip card".

## 4. Certification and Conformance Requirements

MAC **Level 2** required for MDES token processing before the deadline; administered by the Mastercard
Certification Authority via Mastercard Connect. Three gates:

- **Gate C1 — Functional Test Suite:** MTS v8.4 against UAT + Simulator. Pass rate 100% Category A,
  85% Category B. ~4 weeks.
- **Gate C2 — Interoperability Testing:** 1,000 end-to-end traces (≥300 MDES token, ≥100 fallback chip,
  ≥50 Reg II debit), submitted via Mastercard Testing API in JSONL (MTS Integration Guide v8.4 App D).
- **Gate C3 — Production Validation:** 60-day monitoring of token decline rates, TRID population, DE
  48.77 coverage via Mastercard Settlement Services. Alert breach → remediation review in 5 business
  days; MAC L2 revoked if not remediated within 30 calendar days.

Acquirers not achieving MAC L2 by 2026-09-30 → all Mastercard/Maestro transactions downgraded to the
Standard non-qualified interchange tier + 90-day remediation (Mastercard Rules §9.3.2).

## 5. Compliance Deadline and Milestones

| Milestone | Target Date | Owner |
|---|---|---|
| MTS v8.4 test harness provisioned | 2026-04-15 | JPMC Merchant Tech |
| Gate C1 functional tests complete | 2026-06-15 | JPMC QA |
| Gate C2 interoperability submission | 2026-07-31 | JPMC + MCA |
| Production deployment (UAT → PROD) | 2026-09-01 | JPMC Ops |
| Gate C3 monitoring period begins | 2026-09-01 | MCA |
| **COMPLIANCE DEADLINE (MCS-2026-R3)** | **2026-09-30** | **All parties** |

## 6. Normative References

- Mastercard Rules, April 2026 edition, §9.3
- Mastercard Security Rules and Procedures v2026-Q1
- MDES Acquirer Implementation Guide v5.2
- Mastercard Test Suite (MTS) v8.4 Acquirer Script Package
- EMV Contactless Kernel C-3 (MCK) v3.1
- Prior mandate: MCS-2024-R7 (superseded)
- Part 2: MCS-2026-R3-T (Technical Specification)
