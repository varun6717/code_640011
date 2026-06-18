"""
Generate synthetic Payment Brand PDF fixtures for PDLC_App_v2.

Produces:
  visa_brand_mandate_2026.pdf   — mandate/compliance/brand-rules/certification-heavy
  mastercard_interchange_spec_2026.pdf — interchange/routing/message-format/reporting-heavy

Together they exercise all 9 acceptance-required tags:
  mandate, compliance_deadline, brand_rules, card_brand, certification,
  routing, message_format, interchange_fees, reporting
"""
import os
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

OUT_DIR = os.path.dirname(os.path.abspath(__file__))


def _styles():
    ss = getSampleStyleSheet()
    h1 = ParagraphStyle("H1", parent=ss["Heading1"], fontSize=16, spaceAfter=6, spaceBefore=12)
    h2 = ParagraphStyle("H2", parent=ss["Heading2"], fontSize=13, spaceAfter=4, spaceBefore=10)
    h3 = ParagraphStyle("H3", parent=ss["Heading3"], fontSize=11, spaceAfter=3, spaceBefore=8)
    body = ParagraphStyle("Body", parent=ss["Normal"], fontSize=10, leading=14, spaceAfter=6, alignment=TA_JUSTIFY)
    cover = ParagraphStyle("Cover", parent=ss["Normal"], fontSize=11, alignment=TA_CENTER, spaceAfter=4)
    label = ParagraphStyle("Label", parent=ss["Normal"], fontSize=9, textColor=colors.HexColor("#555555"), spaceAfter=2)
    return h1, h2, h3, body, cover, label


def _doc(filename, title):
    path = os.path.join(OUT_DIR, filename)
    doc = SimpleDocTemplate(path, pagesize=LETTER,
                            leftMargin=1.1*inch, rightMargin=1.1*inch,
                            topMargin=1*inch, bottomMargin=1*inch,
                            title=title)
    return doc, path


def make_visa_mandate():
    doc, path = _doc("visa_brand_mandate_2026.pdf",
                     "Visa Merchant Services Brand Mandate VMS-2026-0147")
    h1, h2, h3, body, cover, label = _styles()
    story = []

    # --- Cover block ---
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("VISA INC. — MERCHANT SERVICES DIVISION", cover))
    story.append(Paragraph("<b>Brand Implementation Mandate</b>", cover))
    story.append(Paragraph("Mandate ID: <b>VMS-2026-0147</b>", cover))
    story.append(Paragraph("Revision: 2.1 | Classification: Confidential", cover))
    story.append(Paragraph("Effective Date: 2026-01-15 | <b>Compliance Deadline: 2026-09-30</b>", cover))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1A1F7C"), spaceAfter=12))
    story.append(Spacer(1, 0.1*inch))

    # --- 1. Mandate Summary ---
    story.append(Paragraph("1. Mandate Summary", h1))
    story.append(Paragraph(
        "This document constitutes a binding brand mandate issued by Visa Inc. to all "
        "participating Merchant Acquirers and their processing partners under the Visa Core Rules "
        "and Visa Product and Service Rules (VCRPS). Mandate <b>VMS-2026-0147</b> requires "
        "implementors to update transaction processing pathways to comply with enhanced Visa "
        "routing rules for card-present and card-not-present transactions across all <b>card_brand: Visa</b> "
        "product lines, including Visa Classic, Visa Gold, Visa Infinite, and Visa Business. "
        "Non-compliance by the stated compliance deadline of <b>2026-09-30</b> will result in "
        "interchange downgrades, chargeback liability shifts, and potential program suspension per "
        "Section 12.4 of the Visa Merchant Agreement.", body))
    story.append(Paragraph(
        "This mandate supersedes circular VMS-2024-0089 (routing table v4) and must be "
        "implemented in coordination with the Merchant Services Certification Program described "
        "in Section 6 of this document. All affected endpoints must pass Visa Certification "
        "Suite v11.2 prior to production deployment.", body))

    # --- 2. Scope ---
    story.append(Paragraph("2. Scope and Applicability", h1))
    story.append(Paragraph(
        "This mandate applies to JPMC Merchant Services processing the following Visa card "
        "product families: <b>Visa Classic</b>, <b>Visa Gold</b>, <b>Visa Infinite</b>, "
        "<b>Visa Business Debit</b>, and <b>Visa Corporate</b>. Debit transactions routed via "
        "Interlink and PLUS networks are out of scope; those networks are governed by separate "
        "mandates. The primary routing change concerns the Brand Authorization Endpoint (BAE) "
        "selector logic, which must correctly identify and forward transactions to the Visa "
        "Certified Authorization Platform (VCAP) based on BIN range, product ID, and usage code.", body))

    # --- 3. Brand Rules ---
    story.append(Paragraph("3. Brand Rules and Operational Constraints", h1))
    story.append(Paragraph("3.1 Routing Decision Logic", h2))
    story.append(Paragraph(
        "All transactions bearing Visa BIN ranges 4000000–4999999 MUST be routed through the "
        "primary Visa authorization path. The brand routing decision MUST occur within 50ms of "
        "transaction receipt and MUST be logged to the audit ledger with a routing reason code. "
        "Dual-message transactions must retain the authorization hold and settlement record in the "
        "same processing session. Fallback routing to the secondary VCAP endpoint is permitted "
        "only upon a verified primary endpoint timeout (≥ 3000ms) and MUST be flagged in the "
        "authorization response with Response Code 91 ('Issuer or switch is inoperative').", body))
    story.append(Paragraph("3.2 Card Verification Requirements", h2))
    story.append(Paragraph(
        "Contactless transactions above USD 100.00 MUST request Cardholder Verification Method "
        "(CVM) results as defined in EMV Contactless Kernel C-2 (Visa payWave). The brand rules "
        "for CVM processing are: (a) Online PIN preferred for transactions above USD 250.00; "
        "(b) Signature acceptable as fallback at attended terminals; (c) No CVM permitted only "
        "for transit/toll scenarios whitelisted in the merchant category code (MCC) table. "
        "The CVM result byte must be populated in DE 55 (ICC Data) of the authorization request.", body))
    story.append(Paragraph("3.3 Token Service Provider (TSP) Rules", h2))
    story.append(Paragraph(
        "Transactions originating from Visa Token Service (VTS) must preserve the Token "
        "Requestor ID (TRID) and Token Reference ID (TRID) through the full authorization chain. "
        "The merchant acquirer MUST NOT substitute the token for a PAN prior to forwarding to "
        "VCAP. De-tokenization is the exclusive responsibility of the Visa Token Service Operator "
        "as mandated in Visa VTS Implementation Guide v7.3.", body))

    # --- 4. Certification Requirements ---
    story.append(Paragraph("4. Certification and Conformance Requirements", h1))
    story.append(Paragraph(
        "All implementations governed by mandate VMS-2026-0147 MUST obtain Visa Merchant "
        "Certification (VMC) Level 3 prior to the compliance deadline. The certification process "
        "comprises three phases:", body))
    story.append(Paragraph(
        "<b>Phase 1 — Pre-certification Testing:</b> Acquirer submits test vectors from the Visa "
        "Certification Suite (VCS) v11.2 test harness. Minimum pass rate: 98% of mandatory test "
        "cases, 80% of optional test cases.", body))
    story.append(Paragraph(
        "<b>Phase 2 — Integration Validation:</b> End-to-end transaction trace submitted to Visa "
        "Certification Authority (VCA) via the Visa Resolve Online (VROL) portal. Must include "
        "at least 500 production-representative transactions spanning all product families in scope.", body))
    story.append(Paragraph(
        "<b>Phase 3 — Production Monitoring:</b> 30-day post-deployment monitoring period with "
        "daily metrics submission to Visa Risk Operations. Any authorization decline rate increase "
        "exceeding 0.5 percentage points above the 90-day baseline triggers an automatic hold "
        "pending Visa review. Certification status must be renewed annually.", body))
    story.append(Paragraph(
        "Failure to achieve VMC Level 3 by 2026-09-30 results in automatic interchange "
        "downgrade to unqualified rate tier (currently 1.95% + USD 0.15 per transaction) "
        "and chargeback liability shift to the acquiring bank.", body))

    # --- 5. Compliance Timeline ---
    story.append(Paragraph("5. Compliance Deadline and Milestones", h1))
    tdata = [
        ["Milestone", "Target Date", "Owner"],
        ["Technical design review complete", "2026-03-31", "JPMC Merchant Tech"],
        ["VCS v11.2 test harness integration", "2026-05-31", "JPMC QA"],
        ["Phase 1 certification submitted", "2026-06-30", "JPMC Merchant Tech"],
        ["Phase 2 integration validation", "2026-08-15", "JPMC + Visa VCA"],
        ["Production deployment (UAT → PROD)", "2026-09-15", "JPMC Ops"],
        ["COMPLIANCE DEADLINE (VMS-2026-0147)", "2026-09-30", "All parties"],
    ]
    t = Table(tdata, colWidths=[3.2*inch, 1.5*inch, 2.0*inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1A1F7C")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#FFF3CD")),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#F5F5F5")]),
        ("ALIGN", (1, 0), (1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.1*inch))

    # --- 6. References ---
    story.append(Paragraph("6. Normative References", h1))
    story.append(Paragraph(
        "• Visa Core Rules and Visa Product and Service Rules (VCRPS), April 2026 edition<br/>"
        "• Visa Certification Suite (VCS) v11.2 Test Specification<br/>"
        "• EMV Contactless Kernel C-2 Specification v2.9 (Visa payWave)<br/>"
        "• Visa Token Service (VTS) Implementation Guide v7.3<br/>"
        "• Prior Mandate: VMS-2024-0089 (superseded by this document)<br/>"
        "• Visa Merchant Agreement, Section 12.4", body))

    doc.build(story)
    return path


def make_mastercard_spec():
    doc, path = _doc("mastercard_interchange_spec_2026.pdf",
                     "Mastercard Interchange & Routing Specification Update MCS-2026-R3")
    h1, h2, h3, body, cover, label = _styles()
    story = []

    # --- Cover block ---
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("MASTERCARD INTERNATIONAL INCORPORATED", cover))
    story.append(Paragraph("<b>Interchange & Routing Technical Specification</b>", cover))
    story.append(Paragraph("Document: <b>MCS-2026-R3</b>  |  Applicable Card Brand: <b>Mastercard</b>", cover))
    story.append(Paragraph("Version: 3.0.1 | Status: Approved-Final | Date: 2026-04-01", cover))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#EB001B"), spaceAfter=12))
    story.append(Spacer(1, 0.1*inch))

    # --- 1. Overview ---
    story.append(Paragraph("1. Overview", h1))
    story.append(Paragraph(
        "This specification defines the updated interchange fee schedules, transaction routing "
        "rules, message format changes, and reporting obligations applicable to all acquirers "
        "processing <b>Mastercard</b> and <b>Maestro</b> branded transactions on the Mastercard "
        "Banknet network effective 2026-07-01. This revision (MCS-2026-R3) supersedes "
        "MCS-2025-R4 in its entirety and introduces changes in three areas: (1) interchange "
        "fee table restructuring to reflect enhanced rewards tiers; (2) ISO 8583:2003 field "
        "additions for digital wallet indicators; (3) mandatory reporting changes for real-time "
        "payment flows via the Mastercard Send platform.", body))

    # --- 2. Interchange Fee Schedule ---
    story.append(Paragraph("2. Interchange Fee Schedule Updates", h1))
    story.append(Paragraph("2.1 Revised Fee Tiers", h2))
    story.append(Paragraph(
        "Interchange fees are assessed per transaction and remitted by the acquirer to the "
        "issuer via the Mastercard Interchange System (MIS). MCS-2026-R3 restructures the "
        "consumer credit interchange tiers as follows:", body))
    fee_data = [
        ["Product Category", "Transaction Type", "Rate (% + USD)", "Effective"],
        ["Mastercard World Elite", "Card-Present", "2.10% + $0.10", "2026-07-01"],
        ["Mastercard World Elite", "Card-Not-Present", "2.40% + $0.10", "2026-07-01"],
        ["Mastercard World", "Card-Present", "1.90% + $0.10", "2026-07-01"],
        ["Mastercard World", "Card-Not-Present", "2.20% + $0.10", "2026-07-01"],
        ["Mastercard Standard", "Card-Present", "1.65% + $0.15", "2026-07-01"],
        ["Mastercard Standard", "Card-Not-Present", "1.85% + $0.15", "2026-07-01"],
        ["Maestro Debit", "PIN Debit", "0.05% + $0.21", "2026-07-01"],
        ["Maestro Debit", "Signature Debit", "0.80% + $0.15", "2026-07-01"],
    ]
    ft = Table(fee_data, colWidths=[2.2*inch, 1.6*inch, 1.5*inch, 1.2*inch])
    ft.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EB001B")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#FFF5F5")]),
        ("ALIGN", (2, 0), (3, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(ft)
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph(
        "Acquirers MUST update their interchange fee calculation engines to apply the new rates "
        "as of the first transaction processed on 2026-07-01 00:00:00 UTC. Retroactive "
        "adjustments will not be processed by Mastercard Settlement Services. "
        "Misclassified interchange will be subject to a USD 0.05 per-transaction correction fee "
        "assessed in the following settlement cycle.", body))

    # --- 3. Routing Rules ---
    story.append(Paragraph("3. Transaction Routing Updates", h1))
    story.append(Paragraph("3.1 Banknet Routing Selection", h2))
    story.append(Paragraph(
        "Transaction routing to Mastercard Banknet MUST follow the BIN-first routing table "
        "published in the Mastercard BIN Table (MBT) v2026-Q2. The routing handler MUST "
        "inspect DE 2 (Primary Account Number) for the 6-digit BIN prefix, look up the "
        "associated network ID and product type in MBT, and forward to the appropriate "
        "Banknet authorization endpoint. Routing decisions MUST be immutable after the "
        "initial selection — mid-transaction re-routing is not permitted under Mastercard "
        "network rules except in documented timeout failover scenarios.", body))
    story.append(Paragraph("3.2 Debit Routing Compliance (Regulation II)", h2))
    story.append(Paragraph(
        "US debit transactions on Mastercard-branded cards are subject to Regulation II "
        "(Durbin Amendment) routing requirements. Acquirers MUST offer at least two unaffiliated "
        "networks for PIN debit routing. JPMC systems MUST configure the routing decision logic "
        "to evaluate: (1) merchant preference flag from the terminal, (2) issuer routing "
        "preference from DE 55 ICC data, (3) cost optimization by interchange tier. The routing "
        "selection must be logged with the selected network ID and reason code in the "
        "transaction audit record for regulatory examination purposes.", body))

    # --- 4. Message Format Changes ---
    story.append(Paragraph("4. ISO 8583 Message Format Changes", h1))
    story.append(Paragraph("4.1 New and Modified Data Elements", h2))
    story.append(Paragraph(
        "MCS-2026-R3 introduces the following changes to the ISO 8583:2003 message format "
        "for Mastercard authorization (MTI 0100/0110) and financial request (MTI 0200/0210) "
        "messages:", body))
    msg_data = [
        ["DE", "Field Name", "Change Type", "Description"],
        ["DE 48.77", "Digital Wallet Indicator", "NEW", "2-byte code identifying wallet type (Apple Pay=01, Google Pay=02, Samsung Pay=03, Masterpass=04)"],
        ["DE 48.78", "Token Assurance Level", "NEW", "1-byte integer (0-99) from Mastercard MDES token vault; required if DE 2 is a MDES token"],
        ["DE 61.8", "POS Environment", "MODIFIED", "Bit 3 extended: value '3' now indicates Soft POS (COTS device); previously undefined"],
        ["DE 104", "Transaction Description", "MODIFIED", "Max length increased from 25 to 40 bytes; UTF-8 encoding now required (was ASCII)"],
        ["DE 55", "ICC System-Related Data", "MODIFIED", "Tag 9F6E (Enhanced Contactless Reader Capabilities) now mandatory for contactless transactions above USD 50"],
    ]
    mt = Table(msg_data, colWidths=[0.6*inch, 1.8*inch, 1.0*inch, 3.1*inch])
    mt.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#FF5F00")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#FFF8F0")]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("WORDWRAP", (3, 0), (3, -1), True),
    ]))
    story.append(mt)
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph(
        "All implementations must be capable of parsing and forwarding DE 48.77 and DE 48.78 "
        "by the effective date. Transactions presenting MDES tokens (identifiable by BIN prefix "
        "520000–529999) MUST include DE 48.78; absence will result in Response Code 55 "
        "('Incorrect PIN / PIN tries exceeded') being returned, which is a processing error "
        "indicator distinct from its literal PIN meaning in this context.", body))

    # --- 5. Reporting Obligations ---
    story.append(Paragraph("5. Reporting and Downstream Data Obligations", h1))
    story.append(Paragraph("5.1 Daily Settlement Reporting", h2))
    story.append(Paragraph(
        "Acquirers must submit the Daily Settlement Report (DSR) to Mastercard Settlement "
        "Services by 06:00 UTC for the prior processing day. The DSR format changes effective "
        "2026-07-01: (a) The 'Product Code' column must use the new 4-character product codes "
        "from MBT v2026-Q2 (previously 2-character); (b) Digital wallet transactions "
        "(DE 48.77 present) must be reported in a separate 'Digital' subsection with "
        "wallet-type breakdown. Failure to comply with the reporting format will result in "
        "settlement holds on the affected batch.", body))
    story.append(Paragraph("5.2 Regulatory and Compliance Reporting", h2))
    story.append(Paragraph(
        "For US debit transactions, acquirers must provide quarterly Regulation II compliance "
        "reports to Mastercard Compliance by the 15th of the month following each quarter end. "
        "Reports must include: total transaction count by network, interchange paid by network, "
        "and routing override counts with justification codes. These reports feed Mastercard's "
        "downstream analytics platform and are subject to audit by the Federal Reserve under "
        "Regulation II enforcement authority.", body))
    story.append(Paragraph("5.3 Real-Time Payment Reporting (Mastercard Send)", h2))
    story.append(Paragraph(
        "Transactions processed via Mastercard Send (push payment) platform must be reported "
        "in real time to the Mastercard Real-Time Monitoring System (RTMS) via a dedicated "
        "API endpoint. Each push transaction must include a correlation ID, disbursement amount, "
        "recipient BIN, and funding source indicator. The RTMS feed is used for fraud "
        "surveillance and regulatory reporting to FinCEN under the Bank Secrecy Act.", body))

    # --- 6. Effective Dates ---
    story.append(Paragraph("6. Effective Dates and Compliance", h1))
    story.append(Paragraph(
        "All changes in MCS-2026-R3 are effective <b>2026-07-01</b>. Systems not updated by "
        "this date will receive processing exceptions for transactions using the new DE 48.77 "
        "and DE 48.78 fields, and interchange will be assessed at the Standard (non-tiered) "
        "rate. The compliance deadline for all JPMC Merchant Services systems is "
        "<b>2026-06-20</b> (internal UAT sign-off required 10 days prior to network effective "
        "date). Questions regarding this specification should be directed to "
        "Mastercard-Acquirer-Relations@mastercard.com.", body))

    doc.build(story)
    return path


if __name__ == "__main__":
    p1 = make_visa_mandate()
    print(f"Created: {p1}")
    p2 = make_mastercard_spec()
    print(f"Created: {p2}")
