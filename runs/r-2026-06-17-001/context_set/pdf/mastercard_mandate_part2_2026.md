<!-- provenance: source=pdf · url=fixtures/pdf/mastercard_mandate_part2_2026.pdf -->
<!-- pipeline: pdf_extract (structure) → article_summarize (summary + topics) → change_type_assess (change_type + topics) -->

# Article Summary (article_summarize)

**Mastercard mandate MCS-2026-R3-T, Part 2 of 2** (Message Formats, Interchange & Routing) — the
normative technical specification for MCS-2026-R3. **Network effective date: 2026-07-01**; JPMC
internal compliance deadline 2026-09-30.

- **ISO 8583 message format:** new conditional DEs 48.66 (Token Requestor ID), 48.77 (Digital Wallet
  Indicator), 48.78 (Token Assurance Level), 48.79 (Device Type); modified DEs 61.8 (Soft POS),
  104 (length 25→40 + ASCII→UTF-8), 55 (new mandatory EMV tag 9F6E), 48.10 (extended to EU/EEA Maestro).
- **Interchange fees:** revised consumer credit tiers with a "Token Enhanced" rate applied when DE 48.78
  Token Assurance Level ≥ 50 (e.g. MC World Elite CP 2.10%→1.95%). Acquirers MUST populate DE 48.78 or
  the Standard rate is assessed; no retroactive adjustments.
- **Routing:** Banknet endpoint selection via BIN-first MBT v2026-Q2 lookup, routing immutable except on
  ≥4000ms primary timeout; Regulation II (Durbin) two-unaffiliated-network requirement for US Debit
  Mastercard/Maestro; MDES token BINs 520000–529999 routed exclusively to MCB-MDES-01 (else hard
  decline RC 58).
- **Reporting:** Daily Settlement Report format changes (4-char product code, Token Flag, wallet
  breakdown); Regulation II quarterly compliance report; monthly MDES token coverage report (first due
  2026-10-05).

_Topics (article_summarize): message_format, interchange_fees, reporting._

---

# Mastercard International Incorporated — Technical Implementation Specification (structural extraction)

- **Mandate ID:** MCS-2026-R3-T — Part 2 of 2: Message Formats, Interchange & Routing
- **Applicable Card Brand:** Mastercard (incl. Maestro, Debit Mastercard)
- **Version:** 1.2 · **Status:** Approved-Final · **Network Effective Date:** 2026-07-01 · **Compliance
  Deadline:** 2026-09-30

## 1. Introduction

Part 2 of 2 for MCS-2026-R3; normative technical specification, read with Part 1 (overview, brand rules,
certification). Changes effective on the Mastercard network 2026-07-01; JPMC internal compliance
deadline 2026-09-30.

## 2. ISO 8583 Message Format Changes

### 2.1 New Data Elements (MTI 0100/0110 auth, 0200/0210 financial; effective 2026-07-01)

| DE | Field Name | Type/Length | Presence | Description |
|---|---|---|---|---|
| DE 48.66 | Token Requestor ID | N-11 | Conditional | TRID assigned by MDES to wallet/device; required when DE 2 is an MDES token |
| DE 48.77 | Digital Wallet Indicator | AN-2 | Conditional | 01=Apple Pay, 02=Google Pay, 03=Samsung Pay, 04=Masterpass… |
| DE 48.78 | Token Assurance Level | N-2 | Conditional | Integer 00–99 from MDES vault; strength of token binding |
| DE 48.79 | Device Type | AN-2 | Optional | 00=POS, 01=Mobile, 02=Wearable, 03=IoT, 04=Browser… |

### 2.2 Modified Data Elements

| DE | Field Name | Change | Detail |
|---|---|---|---|
| DE 61.8 | POS Environment | Value extended | Bit 3 value '3' now = Soft POS (COTS certified payment app) |
| DE 104 | Transaction Description | Length + encoding | Max 25→40 bytes; ASCII→UTF-8; truncate at 40 bytes |
| DE 55 | ICC System-Related Data | New mandatory tag | EMV tag 9F6E (Enhanced Contactless Reader Capabilities, 4 bytes) now mandatory |
| DE 48.10 | Mastercard Assigned ID | Scope extended | Now required on Maestro transactions in EU/EEA |

## 3. Interchange Fee Schedule

Interchange remitted acquirer-to-issuer via the Mastercard Interchange System (MIS). "Token Enhanced"
applies when DE 48.78 Token Assurance Level ≥ 50.

| Product | Transaction Type | Standard Rate | Token Enhanced Rate | Effective |
|---|---|---|---|---|
| MC World Elite | Card-Present | 2.10% + $0.10 | 1.95% + $0.10 | 2026-07-01 |
| MC World Elite | Card-Not-Present | 2.40% + $0.10 | 2.15% + $0.10 | 2026-07-01 |
| MC World | Card-Present | 1.90% + $0.10 | 1.75% + $0.10 | 2026-07-01 |
| MC World | Card-Not-Present | 2.20% + $0.10 | 1.95% + $0.10 | 2026-07-01 |
| MC Standard | Card-Present | 1.65% + $0.15 | 1.65% + $0.15 | 2026-07-01 |
| MC Standard | Card-Not-Present | 1.85% + $0.15 | 1.85% + $0.15 | 2026-07-01 |
| Debit MC | PIN Debit | 0.05% + $0.21 | 0.05% + $0.21 | 2026-07-01 |
| Maestro | PIN Debit | 0.05% + $0.21 | 0.05% + $0.21 | 2026-07-01 |

Acquirers MUST populate DE 48.78 to receive the Token Enhanced rate; otherwise Standard rate is
assessed regardless of actual assurance. Retroactive adjustments are not processed.

## 4. Transaction Routing Rules

- **4.1 Banknet Endpoint Selection.** BIN-first lookup in MBT v2026-Q2: extract 6-digit BIN from DE 2 →
  resolve network ID + product type → select Banknet endpoint (primary or STIP) by product type + Reg II
  preference. Routing immutable once made (no mid-transaction re-routing except documented ≥4000ms
  primary timeout). Network ID + reason code written to audit record within 200ms.
- **4.2 Regulation II (Durbin) routing for Debit Mastercard.** US Debit Mastercard/Maestro under Reg II
  (12 CFR Part 235): ≥2 unaffiliated networks for PIN debit; routing evaluates merchant preference →
  issuer preference → cost optimization; no exclusivity. Rationale retained ≥3 years for Federal Reserve.
- **4.3 MDES token routing.** Token BINs 520000–529999 routed exclusively to Banknet MDES gateway
  (MCB-MDES-01); MUST NOT route to acquirer-side/alternate debit networks. Bypass → hard decline
  Response Code 58 ("Transaction not permitted to terminal").

## 5. Reporting and Downstream Data Obligations

- **5.1 Daily Settlement Report (DSR):** effective 2026-07-01, submit to Mastercard Settlement Services
  by 06:00 UTC — Product Code 2→4 chars (MBT v2026-Q2), new Token Flag (Y/N from DE 48.77), wallet-type
  breakdown when token transactions present. Format-failing files rejected → settlement hold.
- **5.2 Regulation II quarterly compliance report:** due 15th after each quarter end (Apr/Jul/Oct/Jan
  15). Transaction count + interchange by network, routing override count + justifications, CCO
  certification. Feeds Mastercard analytics; subject to Federal Reserve audit.
- **5.3 MDES token coverage reporting:** monthly by the 5th for the prior month — total + token
  transaction counts, assurance-level distribution, DE 48.66 TRID population rate. First report due
  2026-10-05 (covering September 2026).

## 6. Effective Dates and JPMC Internal Deadlines

Network effective date: 2026-07-01. JPMC internal UAT sign-off: 2026-06-20. Full compliance (MAC L2 +
Gate C3): 2026-09-30.

## 7. Normative References

- Mastercard Rules, April 2026 edition, §§5.7, 9.3
- ISO 8583:2003 — interchange message specifications
- MDES Acquirer Implementation Guide v5.2
- Mastercard BIN Table (MBT) v2026-Q2
- Mastercard Settlement Services DSR Format Guide v2026-07
- Regulation II (12 CFR Part 235)
- EMV Contactless Kernel C-3 (MCK) v3.1
- Part 1: MCS-2026-R3 (Mandate Overview, Brand Rules & Certification)
