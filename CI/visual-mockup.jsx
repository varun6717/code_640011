import React, { useState, useMemo, useEffect, useRef, useCallback } from "react";
import {
  Play, CheckCircle2, Clock, AlertTriangle, AlertOctagon, AlertCircle,
  ChevronDown, ChevronRight, X, ArrowLeft, Download, ZoomIn, ZoomOut,
  ExternalLink, Search, Filter, FolderOpen, RefreshCw, RotateCw,
  FileText, Layers, Activity as ActivityIcon, ListTree, Bell, User,
  Plus, Settings2, Circle, Loader2, Maximize2, Send, GripVertical,
  ChevronUp, Eye, Hash, MapPin, ArrowUpRight,
} from "lucide-react";

/* =====================================================================
   ci_ui — Phase 4 Visual Mockup
   Aesthetic: deep oceanic / liquid glass
   Typography: General Sans (Fontshare) + JetBrains Mono (Google Fonts)
   ===================================================================== */

/* ---------- Sample data (anchored to actual pipeline schemas) ---------- */

const SAMPLE_RUNS = [
  {
    id: "intuit_20260514_124300",
    merchant: "Intuit",
    timestamp: "2026-05-14 12:43",
    state: "pre-approval",
    maids: ["1411424", "1411425", "1411426", "1411427"],
    jiraEpic: null,
    jiraStory: null,
    issuesCount: 1,
    ownedByMe: true,
  },
  {
    id: "kroger_20260514_115215",
    merchant: "Kroger",
    timestamp: "2026-05-14 11:52",
    state: "mid-staged",
    maids: ["1408506", "1408507"],
    jiraEpic: null,
    jiraStory: null,
    issuesCount: 0,
    ownedByMe: false,
  },
  {
    id: "walmart_20260513_163040",
    merchant: "Walmart",
    timestamp: "2026-05-13 16:30",
    state: "submitted",
    maids: ["1502341", "1502342", "1502343"],
    jiraEpic: "CMRPEE-12340",
    jiraStory: "CMRPEE-12341",
    issuesCount: 0,
    ownedByMe: false,
  },
  {
    id: "target_20260513_103022",
    merchant: "Target",
    timestamp: "2026-05-13 10:30",
    state: "submitted",
    maids: ["1382911", "1382912"],
    jiraEpic: "CMRPEE-12338",
    jiraStory: "CMRPEE-12339",
    issuesCount: 0,
    ownedByMe: true,
  },
  {
    id: "costco_20260512_141815",
    merchant: "Costco",
    timestamp: "2026-05-12 14:18",
    state: "pre-approval",
    maids: ["1294511"],
    jiraEpic: null,
    jiraStory: null,
    issuesCount: 3,
    ownedByMe: false,
  },
  {
    id: "homedepot_20260511_092145",
    merchant: "Home Depot",
    timestamp: "2026-05-11 09:21",
    state: "submitted",
    maids: ["1467223", "1467224"],
    jiraEpic: "CMRPEE-12335",
    jiraStory: "CMRPEE-12336",
    issuesCount: 0,
    ownedByMe: false,
  },
  {
    id: "bestbuy_20260510_175533",
    merchant: "Best Buy",
    timestamp: "2026-05-10 17:55",
    state: "failed-staged",
    maids: ["1318877"],
    jiraEpic: null,
    jiraStory: null,
    issuesCount: 2,
    ownedByMe: true,
  },
  {
    id: "cvs_20260509_134420",
    merchant: "CVS",
    timestamp: "2026-05-09 13:44",
    state: "stale",
    maids: ["1208844"],
    jiraEpic: null,
    jiraStory: null,
    issuesCount: 0,
    ownedByMe: false,
  },
  {
    id: "walgreens_20260508_111200",
    merchant: "Walgreens",
    timestamp: "2026-05-08 11:12",
    state: "submitted",
    maids: ["1198765", "1198766"],
    jiraEpic: "CMRPEE-12331",
    jiraStory: "CMRPEE-12332",
    issuesCount: 0,
    ownedByMe: false,
  },
  {
    id: "wholefoods_20260507_152910",
    merchant: "Whole Foods",
    timestamp: "2026-05-07 15:29",
    state: "pre-approval",
    maids: ["1453390"],
    jiraEpic: null,
    jiraStory: null,
    issuesCount: 0,
    ownedByMe: false,
  },
];

const BASE_TABLE_ROWS_INTUIT = [
  {
    matchTag: "IT-A1", jiraKey: null,
    action: "Add", mnemonic: "VS2-CONS",
    description: "VS Consumer Credit Premium Tier — Intuit",
    maid: "1411424", ird: "VS", timeliness: "Same Day",
    regulated: "N", posEntry: "Mag/Chip", mcc: "5734",
    breakeven: "LE 120.00", transType: "Sale",
    afs: "Premium", region: "US Region",
    currentRate: "N/A", newRate: "1.85% + $0.10",
    deltas: "New record",
  },
  {
    matchTag: "IT-A2", jiraKey: null,
    action: "Add", mnemonic: "VS2-CMRC",
    description: "VS Commercial Tier 1 — Intuit",
    maid: "1411424", ird: "VS", timeliness: "Same Day",
    regulated: "N", posEntry: "Card-not-present", mcc: "5734",
    breakeven: "GT 250.00", transType: "Sale",
    afs: "Commercial", region: "US Region",
    currentRate: "N/A", newRate: "2.20% + $0.10",
    deltas: "New record",
  },
  {
    matchTag: "IT-R1", jiraKey: null,
    action: "Rate Update", mnemonic: "MAB7",
    description: "MC MPP Unregulated Consumer Debit Mag Stripe — Intuit",
    maid: "1411425", ird: "MC", timeliness: "Standard",
    regulated: "N", posEntry: "Mag", mcc: "5411",
    breakeven: "LE 120.00", transType: "Sale",
    afs: "Standard", region: "US Region",
    currentRate: "1.05% + $0.15", newRate: "1.15% + $0.15",
    deltas: "InterchangeRates",
  },
  {
    matchTag: "IT-R2", jiraKey: null,
    action: "Rate Update", mnemonic: "MABC",
    description: "MC MPP Regulated Debit — Intuit",
    maid: "1411425", ird: "MC", timeliness: "Standard",
    regulated: "Y", posEntry: "Chip", mcc: "5411",
    breakeven: "—", transType: "Sale",
    afs: "Standard", region: "US Region",
    currentRate: "0.05% + $0.22", newRate: "0.05% + $0.24",
    deltas: "InterchangeRates",
  },
  {
    matchTag: "IT-M1", jiraKey: null,
    action: "MCC Expansion", mnemonic: "MA47",
    description: "MC MPP Consumer Credit World — Intuit",
    maid: "1411426", ird: "MC", timeliness: "Standard",
    regulated: "N", posEntry: "Card-not-present", mcc: "5411, 5621, 5641, 5651, 5661, 5691, 5719, 5732, 5734, 5947, 5999",
    breakeven: "LE 200.00", transType: "Sale",
    afs: "World", region: "US Region",
    currentRate: "1.60% + $0.10", newRate: "1.60% + $0.10",
    deltas: "mcc (4→11)",
  },
  {
    matchTag: "IT-M2", jiraKey: null,
    action: "MCC Expansion", mnemonic: "MA48",
    description: "MC MPP Consumer Credit World Elite — Intuit",
    maid: "1411426", ird: "MC", timeliness: "Standard",
    regulated: "N", posEntry: "Card-not-present", mcc: "5411, 5732, 5734, 5999",
    breakeven: "LE 300.00", transType: "Sale",
    afs: "World Elite", region: "US Region",
    currentRate: "1.85% + $0.10", newRate: "1.85% + $0.10",
    deltas: "mcc (2→4)",
  },
  {
    matchTag: "IT-X1", jiraKey: null,
    action: "Remove", mnemonic: "MA22",
    description: "MC MPP Consumer Debit Mag — Intuit (legacy)",
    maid: "1411427", ird: "MC", timeliness: "Standard",
    regulated: "N", posEntry: "Mag", mcc: "5411",
    breakeven: "—", transType: "Sale",
    afs: "Legacy", region: "US Region",
    currentRate: "0.95% + $0.15", newRate: "N/A",
    deltas: "—",
  },
  {
    matchTag: "IT-A3", jiraKey: null,
    action: "Add", mnemonic: "VS2-PREM",
    description: "VS Premium Rewards Tier — Intuit",
    maid: "1411424", ird: "VS", timeliness: "Same Day",
    regulated: "N", posEntry: "Card-not-present", mcc: "5734",
    breakeven: "GT 500.00", transType: "Sale",
    afs: "Premium Rewards", region: "US Region",
    currentRate: "N/A", newRate: "2.40% + $0.10",
    deltas: "New record",
  },
  {
    matchTag: "IT-R3", jiraKey: null,
    action: "Rate Update", mnemonic: "MA77",
    description: "MC MPP Consumer Credit Standard — Intuit",
    maid: "1411425", ird: "MC", timeliness: "Standard",
    regulated: "N", posEntry: "Chip", mcc: "5411",
    breakeven: "LE 200.00", transType: "Sale",
    afs: "Standard", region: "US Region",
    currentRate: "1.43% + $0.10", newRate: "1.51% + $0.10",
    deltas: "InterchangeRates",
  },
  {
    matchTag: "IT-A4", jiraKey: null,
    action: "Add", mnemonic: "VS2-BUSI",
    description: "VS Business Card Tier — Intuit",
    maid: "1411424", ird: "VS", timeliness: "Standard",
    regulated: "N", posEntry: "Chip", mcc: "5734",
    breakeven: "GT 300.00", transType: "Sale",
    afs: "Business", region: "US Region",
    currentRate: "N/A", newRate: "2.10% + $0.10",
    deltas: "New record",
  },
  {
    matchTag: "IT-A5", jiraKey: null,
    action: "Add", mnemonic: "VS2-CORP",
    description: "VS Corporate Card Tier — Intuit",
    maid: "1411424", ird: "VS", timeliness: "Standard",
    regulated: "N", posEntry: "Chip", mcc: "5734",
    breakeven: "GT 500.00", transType: "Sale",
    afs: "Corporate", region: "US Region",
    currentRate: "N/A", newRate: "2.50% + $0.10",
    deltas: "New record",
  },
  {
    matchTag: "IT-X2", jiraKey: null,
    action: "Remove", mnemonic: "MA31",
    description: "MC MPP Legacy Debit — Intuit (legacy)",
    maid: "1411427", ird: "MC", timeliness: "Standard",
    regulated: "N", posEntry: "Mag", mcc: "5411",
    breakeven: "—", transType: "Sale",
    afs: "Legacy", region: "US Region",
    currentRate: "1.05% + $0.15", newRate: "N/A",
    deltas: "—",
  },
];

const DRAWER_DATA = {
  "IT-A1": {
    fieldDeltas: [],
    isAdd: true,
    etlImpact: [
      { entryType: "ADD", mcc: "5734", mnemonic: "VS2-CONS", maid: "1411424", systemUpdate: "both" },
    ],
    sourceRecord: {
      maid: "1411424", MOP: "CRD", MasterCardSystem: "—", POSEntry: "Mag/Chip",
      pos_entry: "05", TraceID: "T411424", CardProgramID: "VS-CONS-PRM",
      TransactionType: "Sales", Region: "US Region", action: "S",
      credit: "Y", debit: "", prepay: "", business_debit: "",
      enhanced: "", world: "", world_elite: "", high_value: "",
      commercial: "", card_presence: "Y", mag_presence: "Y", durbin: "N",
      mcc: "5734", trans_type: "", low_breakeven_cond: "LE", low_breakeven: "120.00",
      high_breakeven_cond: "", high_breakeven: "", low_bsa_range_cond: "",
      low_bsa_range: "", high_bsa_range_cond: "", high_bsa_range: "",
      pos_em: "05", cat_type: "", filler: "", mpt_bin: "",
      special_1: "PREM_TIER_1", special_2: "", ird: "VS",
      mnemonic: "VS2-CONS", mnemonic_desc: "VS Consumer Credit Premium Tier — Intuit",
      InterchangeRates: "1.85% + $0.10",
    },
  },
  "IT-R1": {
    fieldDeltas: [
      { field: "InterchangeRates", old: "1.05% + $0.15", new: "1.15% + $0.15", correlated: false },
    ],
    isAdd: false,
    etlImpact: [
      { entryType: "PEOPLESOFT_ONLY", mcc: "5411", mnemonic: "MAB7", maid: "1411425", systemUpdate: "peoplesoft" },
    ],
    sourceRecord: {
      maid: "1411425", mnemonic: "MAB7", InterchangeRates: "1.15% + $0.15",
      mcc: "5411", durbin: "N", action: "S",
    },
  },
  "IT-R2": {
    fieldDeltas: [
      { field: "InterchangeRates", old: "0.05% + $0.22", new: "0.05% + $0.24", correlated: false },
    ],
    isAdd: false,
    etlImpact: [
      { entryType: "PEOPLESOFT_ONLY", mcc: "5411", mnemonic: "MABC", maid: "1411425", systemUpdate: "peoplesoft" },
    ],
    sourceRecord: { maid: "1411425", mnemonic: "MABC" },
  },
  "IT-M1": {
    fieldDeltas: [
      { field: "mcc", old: "5411, 5732, 5734, 5999", new: "5411, 5621, 5641, 5651, 5661, 5691, 5719, 5732, 5734, 5947, 5999", correlated: true },
    ],
    isAdd: false,
    truncateReload: { existing: 4, replacement: 11 },
    etlImpact: [
      { entryType: "REMOVE", mcc: "5411", mnemonic: "MA47", maid: "1411426", systemUpdate: "both" },
      { entryType: "REMOVE", mcc: "5732", mnemonic: "MA47", maid: "1411426", systemUpdate: "both" },
      { entryType: "REMOVE", mcc: "5734", mnemonic: "MA47", maid: "1411426", systemUpdate: "both" },
      { entryType: "REMOVE", mcc: "5999", mnemonic: "MA47", maid: "1411426", systemUpdate: "both" },
      { entryType: "ADD", mcc: "5411", mnemonic: "MA47", maid: "1411426", systemUpdate: "both" },
      { entryType: "ADD", mcc: "5621", mnemonic: "MA47", maid: "1411426", systemUpdate: "both" },
      { entryType: "ADD", mcc: "5641", mnemonic: "MA47", maid: "1411426", systemUpdate: "both" },
      { entryType: "ADD", mcc: "5651", mnemonic: "MA47", maid: "1411426", systemUpdate: "both" },
      { entryType: "ADD", mcc: "5661", mnemonic: "MA47", maid: "1411426", systemUpdate: "both" },
      { entryType: "ADD", mcc: "5691", mnemonic: "MA47", maid: "1411426", systemUpdate: "both" },
      { entryType: "ADD", mcc: "5719", mnemonic: "MA47", maid: "1411426", systemUpdate: "both" },
      { entryType: "ADD", mcc: "5732", mnemonic: "MA47", maid: "1411426", systemUpdate: "both" },
      { entryType: "ADD", mcc: "5734", mnemonic: "MA47", maid: "1411426", systemUpdate: "both" },
      { entryType: "ADD", mcc: "5947", mnemonic: "MA47", maid: "1411426", systemUpdate: "both" },
      { entryType: "ADD", mcc: "5999", mnemonic: "MA47", maid: "1411426", systemUpdate: "both" },
    ],
    sourceRecord: { maid: "1411426", mnemonic: "MA47", mcc: "5411, 5621, 5641, 5651, 5661, 5691, 5719, 5732, 5734, 5947, 5999" },
  },
  "IT-X1": {
    fieldDeltas: [
      { field: "action", old: "S", new: "—", correlated: false },
    ],
    isAdd: false,
    etlImpact: [
      { entryType: "REMOVE", mcc: "5411", mnemonic: "MA22", maid: "1411427", systemUpdate: "both" },
    ],
    sourceRecord: { maid: "1411427", mnemonic: "MA22" },
  },
};

const ACTIVITY_EVENTS = [
  { id: 1, type: "run_started", phase: "staged", label: "Run started", sub: "Pipeline · staged · skip_jira=true", ts: "12:43:00", state: "complete" },
  { id: 2, type: "step_started", step: 1, label: "Step 1 — Vision extraction", sub: "Decomposing agreement images into raw pricing points", ts: "12:43:02", state: "complete", duration: "1m 42s" },
  { id: 3, type: "page_processed", step: 1, label: "Page 1 of 6 processed", sub: "extracted 11 raw pricing points", ts: "12:43:18", state: "complete", nested: true },
  { id: 4, type: "page_processed", step: 1, label: "Page 2 of 6 processed", sub: "extracted 8 raw pricing points", ts: "12:43:32", state: "complete", nested: true },
  { id: 5, type: "page_processed", step: 1, label: "Page 3 of 6 processed", sub: "extracted 14 raw pricing points", ts: "12:43:48", state: "complete", nested: true },
  { id: 6, type: "page_processed", step: 1, label: "Page 4 of 6 processed", sub: "extracted 9 raw pricing points", ts: "12:44:02", state: "complete", nested: true },
  { id: 7, type: "page_processed", step: 1, label: "Page 5 of 6 processed", sub: "extracted 12 raw pricing points", ts: "12:44:24", state: "complete", nested: true },
  { id: 8, type: "page_processed", step: 1, label: "Page 6 of 6 processed", sub: "extracted 7 raw pricing points", ts: "12:44:42", state: "complete", nested: true },
  { id: 9, type: "step_completed", step: 1, label: "Step 1 complete", sub: "61 raw points · 1m 42s", ts: "12:44:44", state: "complete" },
  { id: 10, type: "step_started", step: 2, label: "Step 2 — Field normalization", sub: "Applying field-spec mapping rules", ts: "12:44:45", state: "complete", duration: "48s" },
  { id: 11, type: "step_completed", step: 2, label: "Step 2 complete", sub: "34-field records produced for 61 mnemonics", ts: "12:45:33", state: "complete" },
  { id: 12, type: "step_started", step: 3, label: "Step 3 — Comparison engine", sub: "Joining against prior ETL state", ts: "12:45:34", state: "complete", duration: "1m 12s" },
  { id: 13, type: "step_completed", step: 3, label: "Step 3 complete", sub: "12 deltas identified · 5 Add · 3 Rate Update · 2 MCC Expansion · 2 Remove", ts: "12:46:46", state: "complete" },
  { id: 14, type: "validation_failure", step: 3, label: "Validation warning", sub: "MAID 1411424 / VS2-PREM — breakeven extraction confidence low", ts: "12:46:48", state: "warning", severity: "ERROR" },
  { id: 15, type: "step_started", step: 4, label: "Step 4 — Classification", sub: "Assigning change types and system_update flags", ts: "12:46:49", state: "complete", duration: "22s" },
  { id: 16, type: "step_completed", step: 4, label: "Step 4 complete", sub: "All 12 records classified", ts: "12:47:11", state: "complete" },
  { id: 17, type: "step_started", step: 6, label: "Step 6 — ETL row generation", sub: "Applying truncate-and-reload patterns", ts: "12:47:12", state: "complete", duration: "34s" },
  { id: 18, type: "step_completed", step: 6, label: "Step 6 complete", sub: "etl_summary_NO_JIRA written · 19 records", ts: "12:47:46", state: "complete" },
  { id: 19, type: "step_started", step: 7, label: "Step 7 — Mod file generation", sub: "Building PeopleSoft Add/Remove tabs", ts: "12:47:47", state: "complete", duration: "8s" },
  { id: 20, type: "step_completed", step: 7, label: "Step 7 complete", sub: "mod_file.xlsx written", ts: "12:47:55", state: "complete" },
  { id: 21, type: "step_started", step: 8, label: "Step 8 — Artifact summary", sub: "Writing display_fields and mod_file_entries", ts: "12:47:56", state: "complete", duration: "4s" },
  { id: 22, type: "step_completed", step: 8, label: "Step 8 complete", sub: "mod_file_entries.json · delta_report.json written", ts: "12:48:00", state: "complete" },
  { id: 23, type: "run_state_changed", label: "State → Pre-approval", sub: "Staged run complete · awaiting operator approval", ts: "12:48:00", state: "complete" },
];

const APPROVAL_EVENTS = [
  { id: 30, type: "run_started", phase: "approval", label: "Approval started", sub: "submit_to_jira invoked", ts: "12:51:14", state: "complete" },
  { id: 31, type: "step_started", step: 5, label: "Step 5 — Jira + SharePoint", sub: "Creating Epic, Story, SharePoint folder tree", ts: "12:51:15", state: "complete", duration: "18s" },
  { id: 32, type: "jira_artifact_created", label: "Jira Epic created", sub: "CMRPEE-12340 · Intuit Q2 Interchange Refresh", ts: "12:51:26", state: "complete", nested: true },
  { id: 33, type: "jira_artifact_created", label: "Jira Story created", sub: "CMRPEE-12341 · 12 subtasks queued", ts: "12:51:30", state: "complete", nested: true },
  { id: 34, type: "jira_artifact_created", label: "SharePoint folder created", sub: "/sites/CI/Intuit/CMRPEE-12341", ts: "12:51:33", state: "complete", nested: true },
  { id: 35, type: "step_completed", step: 5, label: "Step 5 complete", sub: "All downstream artifacts provisioned", ts: "12:51:33", state: "complete" },
  { id: 36, type: "step_started", step: 6, label: "Step 6 — ETL re-emission", sub: "Re-writing with real Jira keys attached", ts: "12:51:34", state: "complete", duration: "12s" },
  { id: 37, type: "step_completed", step: 6, label: "Step 6 complete", sub: "etl_summary_CMRPEE-12341 written", ts: "12:51:46", state: "complete" },
  { id: 38, type: "run_state_changed", label: "State → Submitted", sub: "Approval phase complete", ts: "12:51:46", state: "complete" },
];

const SAMPLE_ISSUES = [
  {
    id: "iss-1", severity: "CRITICAL",
    message: "Vision validation failed for record after 3 retries",
    detail: "Field `lBreakeven` could not be extracted with sufficient confidence. Manual review required before approval.",
    scope: { maid: "1411424", mnemonic: "VS2-PREM", matchTag: "IT-A3" },
    remediation: "Open the source agreement PDF and verify the breakeven threshold for VS2-PREM. Re-run from scratch if extraction is recoverable.",
  },
  {
    id: "iss-2", severity: "ERROR",
    message: "Classification confidence low",
    detail: "Multiple candidate mnemonics for MAID 1411425 / VS2-CONS had match scores within 4 percentage points. Engine picked highest but flagged for review.",
    scope: { maid: "1411425", mnemonic: "VS2-CONS", matchTag: null },
    remediation: "Spot-check the assignment against the agreement before approving.",
  },
  {
    id: "iss-3", severity: "ERROR",
    message: "Snowflake old-state query returned 0 rows for MAID",
    detail: "Comparison engine could not locate prior ETL state for MAID 1411426. Treated as net-new but verify this is correct.",
    scope: { maid: "1411426", mnemonic: null, matchTag: null },
    remediation: "Confirm whether this MAID has been onboarded previously. If yes, investigate the Snowflake lookup path.",
  },
  {
    id: "iss-4", severity: "WARNING", cosmetic: true,
    message: "Region field hardcoded to 'US Region'",
    detail: "Pipeline currently emits a constant `US Region` value for all rows. Confirm before approval if regional segmentation matters for this merchant.",
    scope: null,
    remediation: null,
  },
  {
    id: "iss-5", severity: "WARNING", cosmetic: true,
    message: "Timestamp formatter dropped trailing milliseconds",
    detail: "Minor cosmetic discrepancy between pipeline timestamps and Jira-recorded timestamps. Does not affect downstream behavior.",
    scope: null,
    remediation: null,
  },
];

/* ---------- Style block ---------- */

function GlobalStyle() {
  return (
    <style>{`
      @import url('https://api.fontshare.com/v2/css?f[]=general-sans@200,300,400,500,600,700&display=swap');
      @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600;700&display=swap');

      :root {
        --bg: #06090f;
        --bg-soft: #0a0f18;
        --bg-elev: #0e141f;
        --ink: #e6ecf5;
        --ink-soft: rgba(230, 236, 245, 0.78);
        --ink-mute: rgba(230, 236, 245, 0.52);
        --ink-dim: rgba(230, 236, 245, 0.32);
        --ink-faint: rgba(230, 236, 245, 0.14);

        --cyan: #7dd3fc;
        --cyan-soft: rgba(125, 211, 252, 0.18);
        --teal: #5eead4;
        --amber: #f7d28f;
        --amber-soft: rgba(247, 210, 143, 0.16);

        --glass: rgba(255, 255, 255, 0.035);
        --glass-strong: rgba(255, 255, 255, 0.06);
        --glass-stroke: rgba(255, 255, 255, 0.08);
        --glass-stroke-strong: rgba(255, 255, 255, 0.14);
        --glass-highlight: rgba(255, 255, 255, 0.18);

        --add: #6ee7a0;
        --add-bg: rgba(110, 231, 160, 0.14);
        --rate: #facc6b;
        --rate-bg: rgba(250, 204, 107, 0.14);
        --mcc: #93c5fd;
        --mcc-bg: rgba(147, 197, 253, 0.14);
        --remove: #fca5a5;
        --remove-bg: rgba(252, 165, 165, 0.14);

        --nochange: #94a3b8;
        --nochange-bg: rgba(148, 163, 184, 0.12);
        --psonly: #c4b5fd;
        --psonly-bg: rgba(196, 181, 253, 0.14);

        --state-pre: #f7d28f;
        --state-sub: #6ee7a0;
        --state-stale: #94a3b8;
        --state-prog: #7dd3fc;
        --state-fail: #fca5a5;

        --crit: #f87171;
        --err: #fb923c;
        --warn: #facc15;

        --radius-sm: 6px;
        --radius: 10px;
        --radius-lg: 14px;
        --radius-xl: 20px;

        --font-sans: 'General Sans', ui-sans-serif, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        --font-mono: 'JetBrains Mono', ui-monospace, 'SF Mono', monospace;
      }

      *, *::before, *::after { box-sizing: border-box; }

      html, body, #root { height: 100%; }

      body {
        margin: 0;
        background: var(--bg);
        color: var(--ink);
        font-family: var(--font-sans);
        font-weight: 400;
        font-feature-settings: "ss01", "ss02", "cv01";
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
        letter-spacing: -0.005em;
        line-height: 1.5;
      }

      .ci-root {
        position: relative;
        min-height: 100vh;
        overflow-x: hidden;
        font-family: var(--font-sans);
        color: var(--ink);
      }

      /* ---- Atmospheric background ---- */
      .ci-bg {
        position: fixed;
        inset: 0;
        z-index: 0;
        background: var(--bg);
        overflow: hidden;
      }
      .ci-bg::before {
        content: "";
        position: absolute;
        inset: -30%;
        background:
          radial-gradient(ellipse at 18% 22%, rgba(125, 211, 252, 0.10), transparent 42%),
          radial-gradient(ellipse at 82% 78%, rgba(94, 234, 212, 0.07), transparent 46%),
          radial-gradient(ellipse at 60% 10%, rgba(247, 210, 143, 0.04), transparent 50%);
        filter: blur(8px);
        animation: ciDrift 36s ease-in-out infinite alternate;
      }
      .ci-bg::after {
        content: "";
        position: absolute;
        inset: 0;
        background-image:
          radial-gradient(circle, rgba(125, 211, 252, 0.055) 0.8px, transparent 0.8px);
        background-size: 28px 28px;
        opacity: 0.55;
        mix-blend-mode: screen;
        pointer-events: none;
      }
      .ci-grain {
        position: fixed;
        inset: 0;
        z-index: 1;
        pointer-events: none;
        opacity: 0.07;
        mix-blend-mode: overlay;
        background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='240' height='240'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2' stitchTiles='stitch'/></filter><rect width='100%' height='100%' filter='url(%23n)' opacity='0.45'/></svg>");
      }

      @keyframes ciDrift {
        0%   { transform: translate3d(-2%, -1%, 0) scale(1); }
        50%  { transform: translate3d(2%, 1%, 0) scale(1.04); }
        100% { transform: translate3d(-1%, 2%, 0) scale(1); }
      }

      /* ---- Glass primitives ---- */
      .glass {
        background: var(--glass);
        backdrop-filter: blur(22px) saturate(140%) brightness(108%);
        -webkit-backdrop-filter: blur(22px) saturate(140%) brightness(108%);
        border: 1px solid var(--glass-stroke);
        border-top-color: var(--glass-stroke-strong);
        box-shadow:
          0 8px 32px rgba(0, 0, 0, 0.35),
          inset 0 1px 0 rgba(255, 255, 255, 0.05);
        border-radius: var(--radius-lg);
      }
      .glass-strong {
        background: var(--glass-strong);
        backdrop-filter: blur(28px) saturate(150%) brightness(110%);
        -webkit-backdrop-filter: blur(28px) saturate(150%) brightness(110%);
        border: 1px solid var(--glass-stroke-strong);
        border-top-color: var(--glass-highlight);
        box-shadow:
          0 10px 40px rgba(0, 0, 0, 0.45),
          inset 0 1px 0 rgba(255, 255, 255, 0.07);
        border-radius: var(--radius-lg);
      }
      .glass-flat {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid var(--glass-stroke);
        border-radius: var(--radius);
      }
      .glass-bar {
        background: rgba(10, 15, 24, 0.55);
        backdrop-filter: blur(24px) saturate(140%);
        -webkit-backdrop-filter: blur(24px) saturate(140%);
        border-bottom: 1px solid var(--glass-stroke);
      }

      /* ---- Typography utilities ---- */
      .mono { font-family: var(--font-mono); font-feature-settings: "tnum", "ss01"; }
      .num { font-family: var(--font-mono); font-variant-numeric: tabular-nums; }

      .h-display {
        font-family: var(--font-sans);
        font-weight: 500;
        letter-spacing: -0.02em;
      }
      .h-label {
        font-family: var(--font-mono);
        font-weight: 500;
        font-size: 10.5px;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: var(--ink-mute);
      }

      /* ---- Buttons ---- */
      .btn {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 8px 14px;
        font-family: var(--font-sans);
        font-weight: 500;
        font-size: 13px;
        letter-spacing: 0.005em;
        color: var(--ink);
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid var(--glass-stroke);
        border-top-color: var(--glass-stroke-strong);
        border-radius: 8px;
        backdrop-filter: blur(12px);
        cursor: pointer;
        transition: all 180ms cubic-bezier(0.2, 0.7, 0.2, 1);
      }
      .btn:hover:not(:disabled) {
        background: rgba(255, 255, 255, 0.07);
        border-color: var(--glass-stroke-strong);
        transform: translateY(-1px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
      }
      .btn:active:not(:disabled) {
        transform: translateY(0);
      }
      .btn:disabled {
        opacity: 0.4;
        cursor: not-allowed;
      }
      .btn-primary {
        background: linear-gradient(180deg, rgba(125, 211, 252, 0.22), rgba(94, 234, 212, 0.12));
        border-color: rgba(125, 211, 252, 0.36);
        box-shadow:
          0 0 0 1px rgba(125, 211, 252, 0.10) inset,
          0 8px 24px rgba(125, 211, 252, 0.12);
        color: #e8f6ff;
      }
      .btn-primary:hover:not(:disabled) {
        background: linear-gradient(180deg, rgba(125, 211, 252, 0.30), rgba(94, 234, 212, 0.16));
        box-shadow:
          0 0 0 1px rgba(125, 211, 252, 0.18) inset,
          0 12px 32px rgba(125, 211, 252, 0.20);
      }
      .btn-warm {
        background: linear-gradient(180deg, rgba(247, 210, 143, 0.20), rgba(247, 210, 143, 0.06));
        border-color: rgba(247, 210, 143, 0.32);
        color: #fff3dc;
      }
      .btn-warm:hover:not(:disabled) {
        background: linear-gradient(180deg, rgba(247, 210, 143, 0.28), rgba(247, 210, 143, 0.10));
      }
      .btn-ghost {
        background: transparent;
        border-color: var(--glass-stroke);
      }
      .btn-ghost:hover:not(:disabled) {
        background: rgba(255, 255, 255, 0.04);
      }
      .btn-sm { padding: 5px 10px; font-size: 12px; }

      /* ---- Inputs ---- */
      .input {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 8px 12px;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid var(--glass-stroke);
        border-radius: 8px;
        color: var(--ink);
        font-family: var(--font-sans);
        font-size: 13px;
        outline: none;
        transition: all 200ms cubic-bezier(0.2, 0.7, 0.2, 1);
      }
      .input:focus-within {
        border-color: rgba(125, 211, 252, 0.45);
        box-shadow:
          0 0 0 3px rgba(125, 211, 252, 0.08),
          0 0 24px rgba(125, 211, 252, 0.12);
        background: rgba(255, 255, 255, 0.05);
      }
      .input input {
        flex: 1;
        background: transparent;
        border: none;
        outline: none;
        color: var(--ink);
        font-family: inherit;
        font-size: inherit;
      }
      .input input::placeholder {
        color: var(--ink-dim);
      }

      /* ---- Pills / badges ---- */
      .pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 3px 9px;
        border-radius: 999px;
        font-family: var(--font-mono);
        font-size: 10.5px;
        font-weight: 600;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        border: 1px solid transparent;
      }
      .pill-add { background: var(--add-bg); color: var(--add); border-color: rgba(110, 231, 160, 0.32); }
      .pill-rate { background: var(--rate-bg); color: var(--rate); border-color: rgba(250, 204, 107, 0.32); }
      .pill-mcc { background: var(--mcc-bg); color: var(--mcc); border-color: rgba(147, 197, 253, 0.32); }
      .pill-remove { background: var(--remove-bg); color: var(--remove); border-color: rgba(252, 165, 165, 0.32); }

      .pill-state-pre { background: var(--amber-soft); color: var(--state-pre); border-color: rgba(247, 210, 143, 0.32); }
      .pill-state-sub { background: var(--add-bg); color: var(--state-sub); border-color: rgba(110, 231, 160, 0.32); }
      .pill-state-stale { background: rgba(148, 163, 184, 0.12); color: var(--state-stale); border-color: rgba(148, 163, 184, 0.28); }
      .pill-state-prog { background: var(--cyan-soft); color: var(--state-prog); border-color: rgba(125, 211, 252, 0.36); }
      .pill-state-fail { background: var(--remove-bg); color: var(--state-fail); border-color: rgba(252, 165, 165, 0.32); }

      .pill-crit { background: rgba(248, 113, 113, 0.16); color: var(--crit); border-color: rgba(248, 113, 113, 0.36); }
      .pill-err { background: rgba(251, 146, 60, 0.16); color: var(--err); border-color: rgba(251, 146, 60, 0.32); }
      .pill-warn { background: rgba(250, 204, 21, 0.14); color: var(--warn); border-color: rgba(250, 204, 21, 0.28); }

      /* ---- Status dot ---- */
      .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 999px;
        position: relative;
        flex-shrink: 0;
      }
      .status-dot::after {
        content: "";
        position: absolute;
        inset: -3px;
        border-radius: 999px;
        animation: ciPulse 2.4s ease-in-out infinite;
      }
      .status-dot.dot-cyan { background: var(--cyan); box-shadow: 0 0 12px var(--cyan); }
      .status-dot.dot-cyan::after { background: var(--cyan); opacity: 0.35; }
      .status-dot.dot-amber { background: var(--amber); box-shadow: 0 0 10px var(--amber); }
      .status-dot.dot-amber::after { background: var(--amber); opacity: 0.3; }
      .status-dot.dot-mute { background: var(--ink-dim); }
      .status-dot.dot-mute::after { display: none; }

      @keyframes ciPulse {
        0%, 100% { transform: scale(1); opacity: 0.35; }
        50%      { transform: scale(2.2); opacity: 0; }
      }

      /* ---- Reveal animation ---- */
      .reveal {
        opacity: 0;
        transform: translateY(8px);
        filter: blur(6px);
        animation: ciReveal 600ms cubic-bezier(0.2, 0.7, 0.2, 1) forwards;
      }
      @keyframes ciReveal {
        to { opacity: 1; transform: translateY(0); filter: blur(0); }
      }

      .stagger > * { opacity: 0; animation: ciReveal 600ms cubic-bezier(0.2, 0.7, 0.2, 1) forwards; }
      .stagger > *:nth-child(1) { animation-delay: 0ms; }
      .stagger > *:nth-child(2) { animation-delay: 60ms; }
      .stagger > *:nth-child(3) { animation-delay: 120ms; }
      .stagger > *:nth-child(4) { animation-delay: 180ms; }
      .stagger > *:nth-child(5) { animation-delay: 240ms; }
      .stagger > *:nth-child(6) { animation-delay: 300ms; }
      .stagger > *:nth-child(7) { animation-delay: 360ms; }
      .stagger > *:nth-child(8) { animation-delay: 420ms; }
      .stagger > *:nth-child(9) { animation-delay: 480ms; }
      .stagger > *:nth-child(10) { animation-delay: 540ms; }

      /* ---- Segmented control ---- */
      .seg {
        display: inline-flex;
        padding: 3px;
        background: rgba(0, 0, 0, 0.3);
        border: 1px solid var(--glass-stroke);
        border-radius: 999px;
        backdrop-filter: blur(12px);
      }
      .seg-item {
        padding: 6px 16px;
        border-radius: 999px;
        font-family: var(--font-sans);
        font-size: 12.5px;
        font-weight: 500;
        letter-spacing: 0.01em;
        color: var(--ink-mute);
        cursor: pointer;
        transition: all 200ms cubic-bezier(0.2, 0.7, 0.2, 1);
      }
      .seg-item:hover { color: var(--ink-soft); }
      .seg-item.active {
        color: var(--ink);
        background: linear-gradient(180deg, rgba(125, 211, 252, 0.20), rgba(94, 234, 212, 0.08));
        box-shadow:
          0 0 0 1px rgba(125, 211, 252, 0.22) inset,
          0 4px 16px rgba(125, 211, 252, 0.10);
      }

      /* ---- Chip ---- */
      .chip {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 5px 12px;
        font-family: var(--font-sans);
        font-size: 12px;
        font-weight: 500;
        color: var(--ink-soft);
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid var(--glass-stroke);
        border-radius: 999px;
        cursor: pointer;
        transition: all 200ms;
      }
      .chip:hover {
        background: rgba(255, 255, 255, 0.05);
        color: var(--ink);
      }
      .chip.active {
        background: rgba(125, 211, 252, 0.10);
        border-color: rgba(125, 211, 252, 0.36);
        color: var(--cyan);
      }

      /* ---- Table ---- */
      .ci-table {
        width: 100%;
        border-collapse: collapse;
        font-family: var(--font-sans);
        font-size: 12.5px;
      }
      .ci-table thead th {
        font-family: var(--font-mono);
        font-size: 10.5px;
        font-weight: 500;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: var(--ink-mute);
        text-align: left;
        padding: 12px 14px 10px;
        background: rgba(255, 255, 255, 0.02);
        border-bottom: 1px solid var(--glass-stroke);
        position: sticky;
        top: 0;
        backdrop-filter: blur(10px);
        z-index: 2;
        white-space: nowrap;
      }
      .ci-table tbody tr {
        border-bottom: 1px solid rgba(255, 255, 255, 0.04);
        cursor: pointer;
        transition: background 160ms;
      }
      .ci-table tbody tr:hover {
        background: rgba(125, 211, 252, 0.04);
      }
      .ci-table tbody tr.selected {
        background: rgba(125, 211, 252, 0.08);
        box-shadow: inset 2px 0 0 var(--cyan);
      }
      .ci-table td {
        padding: 11px 14px;
        color: var(--ink-soft);
        white-space: nowrap;
        vertical-align: middle;
      }
      .ci-table td.mono { font-family: var(--font-mono); color: var(--ink); }
      .ci-table td.mute { color: var(--ink-mute); }

      /* ---- Timeline ---- */
      .timeline {
        position: relative;
        padding-left: 28px;
      }
      .timeline::before {
        content: "";
        position: absolute;
        left: 7px;
        top: 4px;
        bottom: 4px;
        width: 1px;
        background: linear-gradient(180deg, var(--glass-stroke-strong) 0%, var(--glass-stroke) 30%, var(--glass-stroke) 70%, transparent 100%);
      }
      .timeline-node {
        position: absolute;
        left: -28px;
        top: 14px;
        width: 14px;
        height: 14px;
        border-radius: 999px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: var(--bg);
        border: 1px solid var(--glass-stroke-strong);
        z-index: 1;
      }
      .timeline-event {
        position: relative;
        margin-bottom: 10px;
      }
      .timeline-event.nested {
        margin-left: 24px;
      }
      .timeline-event.nested::before {
        content: "";
        position: absolute;
        left: -16px;
        top: 22px;
        width: 12px;
        height: 1px;
        background: var(--glass-stroke);
      }

      /* ---- Drawer ---- */
      .drawer-overlay {
        position: absolute;
        inset: 0;
        background: rgba(0, 0, 0, 0.2);
        backdrop-filter: blur(2px);
        z-index: 30;
        animation: ciFade 200ms ease-out;
      }
      @keyframes ciFade { from { opacity: 0; } to { opacity: 1; } }
      .drawer {
        position: absolute;
        top: 0;
        right: 0;
        bottom: 0;
        width: min(720px, 92%);
        z-index: 40;
        background: rgba(11, 16, 24, 0.86);
        backdrop-filter: blur(36px) saturate(150%);
        -webkit-backdrop-filter: blur(36px) saturate(150%);
        border-left: 1px solid var(--glass-stroke-strong);
        box-shadow: -24px 0 48px rgba(0, 0, 0, 0.4);
        overflow-y: auto;
        animation: ciSlideIn 320ms cubic-bezier(0.2, 0.7, 0.2, 1);
      }
      @keyframes ciSlideIn {
        from { transform: translateX(40px); opacity: 0; filter: blur(8px); }
        to   { transform: translateX(0); opacity: 1; filter: blur(0); }
      }

      /* ---- Modal ---- */
      .modal-overlay {
        position: fixed; inset: 0;
        background: rgba(0, 0, 0, 0.55);
        backdrop-filter: blur(8px);
        z-index: 80;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 32px;
        animation: ciFade 200ms ease-out;
      }
      .modal {
        width: min(720px, 100%);
        max-height: 80vh;
        overflow-y: auto;
        animation: ciReveal 300ms cubic-bezier(0.2, 0.7, 0.2, 1) forwards;
      }

      /* ---- Toast ---- */
      .toast {
        position: fixed;
        top: 80px;
        right: 24px;
        z-index: 70;
        min-width: 320px;
        max-width: 380px;
        padding: 14px 16px;
        animation: ciToastIn 360ms cubic-bezier(0.2, 0.7, 0.2, 1);
        cursor: pointer;
      }
      @keyframes ciToastIn {
        from { transform: translateX(20px) translateY(-8px); opacity: 0; filter: blur(8px); }
        to   { transform: translateX(0) translateY(0); opacity: 1; filter: blur(0); }
      }

      /* ---- Divider for split pane ---- */
      .split-divider {
        width: 8px;
        background: transparent;
        cursor: col-resize;
        position: relative;
        flex-shrink: 0;
        z-index: 5;
        transition: background 180ms;
      }
      .split-divider:hover, .split-divider.dragging {
        background: rgba(125, 211, 252, 0.10);
      }
      .split-divider::after {
        content: "";
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 1px;
        height: 100%;
        background: var(--glass-stroke);
      }

      /* ---- Scrollbars ---- */
      ::-webkit-scrollbar { width: 10px; height: 10px; }
      ::-webkit-scrollbar-track { background: transparent; }
      ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.08);
        border-radius: 999px;
        border: 2px solid transparent;
        background-clip: content-box;
      }
      ::-webkit-scrollbar-thumb:hover { background: rgba(255, 255, 255, 0.16); background-clip: content-box; }

      /* ---- Utility ---- */
      .focus-ring:focus-visible {
        outline: none;
        box-shadow: 0 0 0 3px rgba(125, 211, 252, 0.32);
      }

      /* ---- Tabs ---- */
      .tab-bar {
        display: flex;
        gap: 4px;
        border-bottom: 1px solid var(--glass-stroke);
        padding: 0 4px;
      }
      .tab {
        position: relative;
        padding: 12px 18px;
        font-family: var(--font-sans);
        font-size: 13px;
        font-weight: 500;
        color: var(--ink-mute);
        cursor: pointer;
        transition: color 200ms;
        display: inline-flex;
        align-items: center;
        gap: 8px;
      }
      .tab:hover { color: var(--ink-soft); }
      .tab.active { color: var(--ink); }
      .tab.active::after {
        content: "";
        position: absolute;
        left: 12px; right: 12px; bottom: -1px; height: 1px;
        background: linear-gradient(90deg, transparent, var(--cyan), transparent);
        box-shadow: 0 0 12px var(--cyan);
      }
      .tab-count {
        font-family: var(--font-mono);
        font-size: 10px;
        font-weight: 600;
        padding: 1px 6px;
        border-radius: 999px;
        background: rgba(252, 165, 165, 0.16);
        color: var(--remove);
        border: 1px solid rgba(252, 165, 165, 0.3);
      }

      /* ---- ETL row backgrounds ---- */
      .etl-row-add { background: var(--add-bg); border-left: 2px solid var(--add); }
      .etl-row-remove { background: var(--remove-bg); border-left: 2px solid var(--remove); }
      .etl-row-nochange { background: var(--nochange-bg); border-left: 2px solid var(--nochange); }
      .etl-row-psonly { background: var(--psonly-bg); border-left: 2px solid var(--psonly); }
    `}</style>
  );
}

/* ---------- State labels and helpers ---------- */

const STATE_LABELS = {
  "pre-run": { label: "Pre-run", pill: "pill-state-stale", dot: "dot-mute" },
  "mid-staged": { label: "In progress", pill: "pill-state-prog", dot: "dot-cyan" },
  "pre-approval": { label: "Pre-approval", pill: "pill-state-pre", dot: "dot-amber" },
  "mid-approval": { label: "Approving", pill: "pill-state-prog", dot: "dot-cyan" },
  "submitted": { label: "Submitted", pill: "pill-state-sub", dot: "dot-mute" },
  "stale": { label: "Stale", pill: "pill-state-stale", dot: "dot-mute" },
  "failed-staged": { label: "Failed (staged)", pill: "pill-state-fail", dot: "dot-mute" },
  "failed-approval": { label: "Failed (approval)", pill: "pill-state-fail", dot: "dot-mute" },
};

const ACTION_PILL = {
  "Add": "pill-add",
  "Rate Update": "pill-rate",
  "MCC Expansion": "pill-mcc",
  "Remove": "pill-remove",
};

function StateBadge({ state, size = "md" }) {
  const s = STATE_LABELS[state] || STATE_LABELS["stale"];
  return (
    <span className={`pill ${s.pill}`} style={size === "sm" ? { fontSize: 9.5, padding: "2px 7px" } : null}>
      <span className={`status-dot ${s.dot}`} style={{ width: size === "sm" ? 5 : 6, height: size === "sm" ? 5 : 6 }} />
      {s.label}
    </span>
  );
}

function ActionPill({ action }) {
  const cls = ACTION_PILL[action] || "pill-mcc";
  return <span className={`pill ${cls}`}>{action}</span>;
}

/* ---------- App Shell ---------- */

function AppShell({ children, currentScreen, onToggle, onBellClick, toastVisible }) {
  return (
    <>
      <header className="glass-bar" style={{
        position: "sticky", top: 0, zIndex: 50,
        padding: "12px 28px", display: "flex", alignItems: "center", justifyContent: "space-between",
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <div style={{
              width: 22, height: 22, borderRadius: 6,
              background: "linear-gradient(135deg, rgba(125, 211, 252, 0.4), rgba(94, 234, 212, 0.25))",
              border: "1px solid rgba(125, 211, 252, 0.5)",
              boxShadow: "0 0 16px rgba(125, 211, 252, 0.25), inset 0 1px 0 rgba(255,255,255,0.2)",
              display: "flex", alignItems: "center", justifyContent: "center",
            }}>
              <Layers size={11} color="#e8f6ff" strokeWidth={2.4} />
            </div>
            <div style={{ display: "flex", flexDirection: "column", lineHeight: 1.1 }}>
              <span className="h-display" style={{ fontSize: 14, fontWeight: 600, letterSpacing: "-0.01em" }}>
                Custom Interchange
              </span>
              <span className="mono" style={{ fontSize: 10, color: "var(--ink-mute)", letterSpacing: "0.06em" }}>
                CI · pipeline operator
              </span>
            </div>
          </div>
        </div>

        <div className="seg">
          <span
            className={`seg-item ${currentScreen !== "runs-list" ? "active" : ""}`}
            onClick={() => onToggle("run")}
          >
            Run
          </span>
          <span
            className={`seg-item ${currentScreen === "runs-list" ? "active" : ""}`}
            onClick={() => onToggle("all-runs")}
          >
            All Runs
          </span>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <button className="btn btn-ghost btn-sm" onClick={onBellClick} title="Demo a toast">
            <Bell size={13} />
            {toastVisible && (
              <span style={{
                width: 6, height: 6, borderRadius: 999,
                background: "var(--amber)", boxShadow: "0 0 8px var(--amber)",
              }} />
            )}
          </button>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <div style={{
              width: 26, height: 26, borderRadius: 999,
              background: "linear-gradient(135deg, rgba(247, 210, 143, 0.35), rgba(252, 165, 165, 0.2))",
              border: "1px solid rgba(247, 210, 143, 0.32)",
              display: "flex", alignItems: "center", justifyContent: "center",
              fontFamily: "var(--font-mono)", fontSize: 10.5, fontWeight: 600,
              color: "#fff3dc",
            }}>
              VR
            </div>
          </div>
        </div>
      </header>
      <main style={{ position: "relative", zIndex: 2 }}>
        {children}
      </main>
    </>
  );
}

/* ---------- State Controller (dev panel) ---------- */

function StateController({ open, onClose, state, dispatch }) {
  if (!open) return null;
  const Section = ({ title, children }) => (
    <div style={{ marginBottom: 12 }}>
      <div className="h-label" style={{ marginBottom: 6 }}>{title}</div>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 4 }}>{children}</div>
    </div>
  );
  const Btn = ({ active, onClick, children }) => (
    <button
      onClick={onClick}
      className="chip"
      style={{ fontSize: 10.5, padding: "3px 8px", ...(active ? { background: "rgba(125, 211, 252, 0.16)", borderColor: "rgba(125, 211, 252, 0.5)", color: "var(--cyan)" } : null) }}
    >
      {children}
    </button>
  );
  return (
    <div className="glass-strong" style={{
      position: "fixed", top: 76, right: 24, zIndex: 60,
      width: 320, padding: 16, maxHeight: "80vh", overflowY: "auto",
    }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 12 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <Settings2 size={13} color="var(--cyan)" />
          <span className="h-display" style={{ fontSize: 12.5, fontWeight: 600 }}>Mockup State</span>
        </div>
        <button className="btn btn-ghost btn-sm" style={{ padding: 4 }} onClick={onClose}>
          <X size={12} />
        </button>
      </div>
      <p style={{ fontSize: 11, color: "var(--ink-mute)", margin: "0 0 14px", lineHeight: 1.5 }}>
        Walk through every state. Not part of the production UI.
      </p>

      <Section title="Screen">
        <Btn active={state.screen === "run-detail"} onClick={() => dispatch({ type: "screen", screen: "run-detail" })}>Run Detail</Btn>
        <Btn active={state.screen === "runs-list"} onClick={() => dispatch({ type: "screen", screen: "runs-list" })}>Runs List</Btn>
        <Btn active={state.screen === "artifact-preview"} onClick={() => dispatch({ type: "screen", screen: "artifact-preview" })}>Artifact Preview</Btn>
      </Section>

      <Section title="Run State">
        {Object.keys(STATE_LABELS).map(s => (
          <Btn key={s} active={state.runState === s} onClick={() => dispatch({ type: "runState", runState: s })}>
            {STATE_LABELS[s].label}
          </Btn>
        ))}
      </Section>

      <Section title="Tab (Run Detail)">
        <Btn active={state.tab === "activity"} onClick={() => dispatch({ type: "tab", tab: "activity" })}>Activity</Btn>
        <Btn active={state.tab === "results"} onClick={() => dispatch({ type: "tab", tab: "results" })}>Results</Btn>
        <Btn active={state.tab === "issues"} onClick={() => dispatch({ type: "tab", tab: "issues" })}>Issues</Btn>
      </Section>

      <Section title="Concurrency simulation">
        <Btn active={state.runLockHeld} onClick={() => dispatch({ type: "toggle", key: "runLockHeld" })}>Run lock held</Btn>
        <Btn active={state.approvalLockHeld} onClick={() => dispatch({ type: "toggle", key: "approvalLockHeld" })}>Approval lock held</Btn>
      </Section>

      <Section title="Issues">
        <Btn active={state.showCosmetic} onClick={() => dispatch({ type: "toggle", key: "showCosmetic" })}>Show cosmetic warnings</Btn>
      </Section>

      <div style={{ paddingTop: 8, borderTop: "1px solid var(--glass-stroke)", marginTop: 4 }}>
        <div className="h-label" style={{ marginBottom: 6 }}>Status</div>
        <div className="mono" style={{ fontSize: 10.5, color: "var(--ink-mute)", lineHeight: 1.6 }}>
          screen: {state.screen}<br />
          runState: {state.runState}<br />
          tab: {state.tab}
        </div>
      </div>
    </div>
  );
}

/* ---------- Run-context strip (used in Run Detail & Artifact Preview) ---------- */

function RunContextStrip({ run, state, runLock, approvalLock, onApprove, onArtifact, dispatch }) {
  const inApproval = state === "mid-approval";
  const isPreApproval = state === "pre-approval";
  const isSubmitted = state === "submitted";
  const isFailed = state === "failed-staged" || state === "failed-approval";

  const approveBlocked = approvalLock && !inApproval;

  return (
    <div className="glass" style={{
      margin: "16px 28px 0", padding: "14px 18px",
      display: "flex", alignItems: "center", justifyContent: "space-between",
      gap: 16, flexWrap: "wrap",
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: 14, flexWrap: "wrap" }}>
        <div style={{ display: "flex", flexDirection: "column", lineHeight: 1.2 }}>
          <span className="h-display" style={{ fontSize: 18, fontWeight: 500, letterSpacing: "-0.015em" }}>
            {run.merchant}
          </span>
          <span className="mono" style={{ fontSize: 11, color: "var(--ink-mute)", letterSpacing: "0.04em", marginTop: 2 }} title={run.id}>
            {run.timestamp} · {run.id}
          </span>
        </div>
        <StateBadge state={state} />
        {run.maids.length > 0 && (
          <div style={{ display: "flex", alignItems: "center", gap: 6, color: "var(--ink-mute)" }}>
            <Hash size={11} />
            <span className="mono" style={{ fontSize: 11.5 }}>
              {run.maids.slice(0, 3).join(", ")}{run.maids.length > 3 && ` +${run.maids.length - 3}`}
            </span>
          </div>
        )}
      </div>

      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
        {isSubmitted && (
          <>
            {/* Production wiring: href={`https://${JPMC_JIRA_HOST}/browse/${run.jiraEpic}`} target="_blank" rel="noopener noreferrer" */}
            <a
              className="btn btn-sm"
              style={{ textDecoration: "none" }}
              href="#"
              onClick={(e) => e.preventDefault()}
              title="Open Jira Epic in a new tab"
            >
              <ExternalLink size={12} />
              <span className="mono">Epic · {run.jiraEpic || "CMRPEE-12340"}</span>
            </a>
            <a
              className="btn btn-sm"
              style={{ textDecoration: "none" }}
              href="#"
              onClick={(e) => e.preventDefault()}
              title="Open Jira Story in a new tab"
            >
              <ExternalLink size={12} />
              <span className="mono">Story · {run.jiraStory || "CMRPEE-12341"}</span>
            </a>
          </>
        )}
        {isPreApproval && (
          <button
            className="btn btn-warm"
            disabled={approveBlocked}
            onClick={onApprove}
            title={approveBlocked ? "An approval is in progress" : "Submit to Jira and SharePoint"}
          >
            <CheckCircle2 size={13} />
            Approve
          </button>
        )}
        {inApproval && (
          <button className="btn btn-warm" disabled>
            <Loader2 size={13} className="ci-spin" style={{ animation: "ciSpin 1.2s linear infinite" }} />
            Approving…
          </button>
        )}
        {isFailed && state === "failed-approval" && (
          <button className="btn btn-warm" disabled={approveBlocked} onClick={onApprove}>
            <RotateCw size={13} />
            Retry Approve
          </button>
        )}
        <button className="btn btn-ghost btn-sm" onClick={onArtifact} title="Open Artifact Preview">
          <Maximize2 size={12} />
          PDF
        </button>
      </div>
      <style>{`@keyframes ciSpin { from { transform: rotate(0); } to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}

/* ---------- Tab bar ---------- */

function TabBar({ tab, setTab, issuesCount, runState }) {
  const tabsVisible = runState !== "pre-run";
  return (
    <div className="tab-bar" style={{ margin: "16px 28px 0" }}>
      <div className={`tab ${tab === "activity" ? "active" : ""}`} onClick={() => setTab("activity")}>
        <ActivityIcon size={13} />
        Activity
      </div>
      {tabsVisible && (
        <>
          <div className={`tab ${tab === "results" ? "active" : ""}`} onClick={() => setTab("results")}>
            <ListTree size={13} />
            Results
          </div>
          <div className={`tab ${tab === "issues" ? "active" : ""}`} onClick={() => setTab("issues")}>
            <AlertTriangle size={13} />
            Issues
            {issuesCount > 0 && <span className="tab-count">{issuesCount}</span>}
          </div>
        </>
      )}
    </div>
  );
}

/* ---------- Activity Tab ---------- */

function ActivityTab({ runState, runLock }) {
  if (runState === "pre-run") return <ActivityPreRun runLock={runLock} />;
  if (runState === "stale") return <ActivityStale />;

  // Determine which events to show
  let events = [];
  let activeStepId = null;
  if (runState === "mid-staged") {
    events = ACTIVITY_EVENTS.slice(0, 17);
    activeStepId = 17;
  } else if (runState === "pre-approval") {
    events = ACTIVITY_EVENTS;
  } else if (runState === "mid-approval") {
    events = [...ACTIVITY_EVENTS, ...APPROVAL_EVENTS.slice(0, 4)];
    activeStepId = APPROVAL_EVENTS[3].id;
  } else if (runState === "submitted") {
    events = [...ACTIVITY_EVENTS, ...APPROVAL_EVENTS];
  } else if (runState === "failed-staged") {
    events = [
      ...ACTIVITY_EVENTS.slice(0, 13),
      { id: 99, type: "step_failed", step: 4, label: "Step 4 failed", sub: "Classification engine threw on MAID 1411424 / VS2-PREM — see Issues tab", ts: "12:47:02", state: "failed" },
      { id: 100, type: "run_failed", label: "Run failed", sub: "Pipeline halted at Step 4 · partial artifacts available", ts: "12:47:02", state: "failed" },
    ];
  } else if (runState === "failed-approval") {
    events = [
      ...ACTIVITY_EVENTS,
      ...APPROVAL_EVENTS.slice(0, 3),
      { id: 199, type: "step_failed", step: 5, label: "Step 5 failed", sub: "Snowflake authentication popup timeout — see Issues tab", ts: "12:51:48", state: "failed" },
      { id: 200, type: "run_failed", label: "Approval failed", sub: "Staged artifacts intact · Retry Approve is available", ts: "12:51:48", state: "failed" },
    ];
  }

  return (
    <div style={{ padding: "20px 28px 40px" }}>
      <div className="timeline stagger">
        {events.map((e, idx) => (
          <TimelineEvent
            key={e.id}
            event={e}
            active={activeStepId === e.id}
          />
        ))}
        {activeStepId && (
          <div className="timeline-event reveal" style={{ animationDelay: `${events.length * 60}ms` }}>
            <div className="timeline-node" style={{
              background: "var(--cyan)",
              boxShadow: "0 0 0 4px rgba(125,211,252,0.16), 0 0 16px rgba(125,211,252,0.4)",
              borderColor: "var(--cyan)",
            }}>
              <Loader2 size={8} color="#06090f" style={{ animation: "ciSpin 1s linear infinite" }} />
            </div>
            <div className="glass-flat" style={{
              padding: "12px 14px",
              borderColor: "rgba(125,211,252,0.32)",
              boxShadow: "0 0 24px rgba(125,211,252,0.10)",
            }}>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 12 }}>
                <div>
                  <div style={{ fontSize: 13, fontWeight: 500, color: "var(--cyan)" }}>
                    Currently running
                  </div>
                  <div style={{ fontSize: 12, color: "var(--ink-mute)", marginTop: 2 }}>
                    Awaiting next event…
                  </div>
                </div>
                <span className="mono" style={{ fontSize: 11, color: "var(--ink-dim)" }}>live</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function TimelineEvent({ event, active }) {
  const isWarn = event.state === "warning";
  const isFail = event.state === "failed";
  const isNested = !!event.nested;
  const nodeStyle = isFail
    ? { background: "rgba(252,165,165,0.18)", borderColor: "var(--remove)" }
    : isWarn
      ? { background: "rgba(250,204,21,0.18)", borderColor: "var(--warn)" }
      : { background: "rgba(110,231,160,0.14)", borderColor: "rgba(110,231,160,0.4)" };
  const NodeIcon = isFail ? AlertOctagon : isWarn ? AlertTriangle : CheckCircle2;
  const nodeColor = isFail ? "var(--remove)" : isWarn ? "var(--warn)" : "var(--add)";

  return (
    <div className={`timeline-event ${isNested ? "nested" : ""}`}>
      <div className="timeline-node" style={nodeStyle}>
        <NodeIcon size={8} color={nodeColor} strokeWidth={2.6} />
      </div>
      <div className="glass-flat" style={{
        padding: isNested ? "8px 12px" : "10px 14px",
        background: isFail ? "rgba(252, 165, 165, 0.04)" : isWarn ? "rgba(250, 204, 21, 0.04)" : undefined,
        borderColor: isFail ? "rgba(252, 165, 165, 0.18)" : isWarn ? "rgba(250, 204, 21, 0.18)" : undefined,
      }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 12 }}>
          <div style={{ minWidth: 0, flex: 1 }}>
            <div style={{
              fontSize: isNested ? 12 : 13,
              fontWeight: isNested ? 400 : 500,
              color: isFail ? "var(--remove)" : isWarn ? "var(--warn)" : "var(--ink)",
            }}>
              {event.label}
            </div>
            <div style={{
              fontSize: 11.5, color: "var(--ink-mute)", marginTop: 2,
              overflow: "hidden", textOverflow: "ellipsis",
            }}>
              {event.sub}
            </div>
          </div>
          <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 2 }}>
            <span className="mono" style={{ fontSize: 10.5, color: "var(--ink-dim)" }}>
              {event.ts}
            </span>
            {event.duration && (
              <span className="mono" style={{ fontSize: 10, color: "var(--ink-mute)" }}>
                {event.duration}
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function ActivityPreRun({ runLock }) {
  const folders = ["input/Intuit", "input/Kroger", "input/Walmart", "input/Target", "input/Costco"];
  const [selected, setSelected] = useState(folders[0]);
  return (
    <div style={{ padding: "32px 28px 60px", display: "flex", justifyContent: "center" }}>
      <div className="glass" style={{ width: "100%", maxWidth: 640, padding: 28 }}>
        <div className="h-label" style={{ marginBottom: 8 }}>Start a new run</div>
        <h2 className="h-display" style={{ fontSize: 22, fontWeight: 500, margin: "0 0 8px", letterSpacing: "-0.015em" }}>
          Select an agreement folder
        </h2>
        <p style={{ fontSize: 13, color: "var(--ink-mute)", margin: "0 0 24px", lineHeight: 1.6 }}>
          Pick a merchant input folder from the allowlist. The pipeline runs through Steps 1–4, 6–8 and stages outputs for your review before any Jira or downstream side effects.
        </p>

        <div className="h-label" style={{ marginBottom: 8 }}>Allowlisted folders</div>
        <div style={{ display: "flex", flexDirection: "column", gap: 6, marginBottom: 24 }}>
          {folders.map(f => (
            <button
              key={f}
              onClick={() => setSelected(f)}
              className="glass-flat focus-ring"
              style={{
                padding: "10px 14px",
                display: "flex", alignItems: "center", gap: 10,
                background: selected === f ? "rgba(125, 211, 252, 0.08)" : "rgba(255, 255, 255, 0.02)",
                borderColor: selected === f ? "rgba(125, 211, 252, 0.36)" : "var(--glass-stroke)",
                cursor: "pointer",
                transition: "all 180ms",
              }}
            >
              <FolderOpen size={14} color={selected === f ? "var(--cyan)" : "var(--ink-mute)"} />
              <span className="mono" style={{
                fontSize: 12.5,
                color: selected === f ? "var(--ink)" : "var(--ink-soft)",
              }}>
                {f}
              </span>
              {selected === f && (
                <span className="mono" style={{ marginLeft: "auto", fontSize: 10.5, color: "var(--cyan)" }}>
                  selected
                </span>
              )}
            </button>
          ))}
        </div>

        <button
          className="btn btn-primary"
          disabled={runLock}
          title={runLock ? "An active run is in progress" : "Run the staged pipeline"}
          style={{ width: "100%", justifyContent: "center", padding: "12px 14px", fontSize: 13.5 }}
        >
          <Play size={14} fill="currentColor" />
          {runLock ? "An active run is in progress" : "Run staged pipeline"}
        </button>

        <div style={{
          display: "flex", alignItems: "flex-start", gap: 8,
          marginTop: 18, padding: "10px 12px",
          background: "rgba(125,211,252,0.04)",
          border: "1px solid rgba(125,211,252,0.14)",
          borderRadius: 8,
        }}>
          <Circle size={6} color="var(--cyan)" fill="var(--cyan)" style={{ marginTop: 6, flexShrink: 0 }} />
          <p style={{ fontSize: 11.5, color: "var(--ink-mute)", margin: 0, lineHeight: 1.55 }}>
            Approval happens after review. Once the staged run completes, you'll review the 18-column output and click Approve to push to Jira and SharePoint.
          </p>
        </div>
      </div>
    </div>
  );
}

function ActivityStale() {
  return (
    <div style={{ padding: "32px 28px 60px", display: "flex", justifyContent: "center" }}>
      <div className="glass" style={{ width: "100%", maxWidth: 540, padding: 28, textAlign: "center" }}>
        <Clock size={28} color="var(--ink-mute)" style={{ marginBottom: 12 }} />
        <h2 className="h-display" style={{ fontSize: 18, fontWeight: 500, margin: "0 0 8px" }}>
          This run predates the new gated-approval build
        </h2>
        <p style={{ fontSize: 13, color: "var(--ink-mute)", margin: 0, lineHeight: 1.6 }}>
          Event history is not available for this run. The output folder is preserved on disk for audit purposes.
        </p>
        <div className="mono" style={{ marginTop: 16, fontSize: 11, color: "var(--ink-dim)" }}>
          output/cvs_20260509_134420/
        </div>
      </div>
    </div>
  );
}

/* ---------- Results Tab ---------- */

function ResultsTab({ runState, openRow, setOpenRow, dispatch }) {
  if (runState === "pre-run") {
    return (
      <EmptyState
        icon={ListTree}
        title="Run not started"
        body="Results populate as the pipeline produces its staged outputs."
      />
    );
  }
  if (runState === "stale") {
    return (
      <EmptyState
        icon={Clock}
        title="No results available for this older run"
        body="This folder predates the gated-approval build. Results cannot be rendered."
      />
    );
  }

  const [filters, setFilters] = useState({ action: null, afs: null });
  const rows = useMemo(() => {
    let r = BASE_TABLE_ROWS_INTUIT;
    if (runState === "mid-staged") r = r.slice(0, 5);
    if (filters.action) r = r.filter(x => x.action === filters.action);
    if (filters.afs) r = r.filter(x => x.afs === filters.afs);
    return r;
  }, [runState, filters]);

  const isFailed = runState === "failed-staged" || runState === "failed-approval";

  return (
    <div style={{ padding: "16px 28px 40px" }}>
      {isFailed && (
        <div className="glass-flat reveal" style={{
          padding: "10px 14px", marginBottom: 12,
          background: "rgba(252, 165, 165, 0.05)",
          borderColor: "rgba(252, 165, 165, 0.18)",
          display: "flex", alignItems: "center", gap: 10,
        }}>
          <AlertOctagon size={14} color="var(--remove)" />
          <span style={{ fontSize: 12.5, color: "var(--ink-soft)" }}>
            This run failed during execution. Partial results are shown — review the <strong style={{ color: "var(--remove)" }}>Issues</strong> tab for context.
          </span>
        </div>
      )}

      {runState === "mid-staged" && (
        <div className="glass-flat reveal" style={{
          padding: "10px 14px", marginBottom: 12,
          background: "rgba(125, 211, 252, 0.04)",
          borderColor: "rgba(125, 211, 252, 0.18)",
          display: "flex", alignItems: "center", gap: 10,
        }}>
          <Loader2 size={13} color="var(--cyan)" style={{ animation: "ciSpin 1.2s linear infinite" }} />
          <span style={{ fontSize: 12.5, color: "var(--ink-soft)" }}>
            Pipeline is still running. Rows populate progressively as Step 3 outputs land.
          </span>
        </div>
      )}

      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 14, gap: 12, flexWrap: "wrap" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 6, flexWrap: "wrap" }}>
          <span className="h-label" style={{ marginRight: 4 }}>Filter</span>
          {["Add", "Rate Update", "MCC Expansion", "Remove"].map(a => (
            <span
              key={a}
              className={`chip ${filters.action === a ? "active" : ""}`}
              onClick={() => setFilters(f => ({ ...f, action: f.action === a ? null : a }))}
            >
              {a}
            </span>
          ))}
          <span style={{ width: 1, height: 16, background: "var(--glass-stroke)", margin: "0 6px" }} />
          {["Premium", "Standard", "Commercial"].map(a => (
            <span
              key={a}
              className={`chip ${filters.afs === a ? "active" : ""}`}
              onClick={() => setFilters(f => ({ ...f, afs: f.afs === a ? null : a }))}
            >
              {a}
            </span>
          ))}
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <span className="mono" style={{ fontSize: 11, color: "var(--ink-mute)" }}>
            {rows.length} of {BASE_TABLE_ROWS_INTUIT.length} rows
          </span>
          <button className="btn btn-ghost btn-sm" onClick={() => dispatch({ type: "screen", screen: "artifact-preview" })}>
            <Maximize2 size={12} />
            View with PDF
          </button>
        </div>
      </div>

      <div className="glass" style={{ position: "relative", overflow: "hidden" }}>
        <div style={{ overflowX: "auto", maxHeight: "calc(100vh - 360px)" }}>
          <table className="ci-table" style={{ minWidth: 1700 }}>
            <thead>
              <tr>
                <th>Jira Key</th>
                <th>Action</th>
                <th>Mnemonic</th>
                <th>Description</th>
                <th>MAID</th>
                <th>IRD</th>
                <th>Timeliness</th>
                <th>Regulated</th>
                <th>POS Entry</th>
                <th>MCC</th>
                <th>Break Even</th>
                <th>Transaction Type</th>
                <th>AFS</th>
                <th>Region</th>
                <th>Current Rate</th>
                <th>New Rate</th>
                <th>Deltas</th>
                <th>Match Tag</th>
              </tr>
            </thead>
            <tbody>
              {rows.map(r => (
                <tr
                  key={r.matchTag}
                  className={openRow === r.matchTag ? "selected" : ""}
                  onClick={() => setOpenRow(openRow === r.matchTag ? null : r.matchTag)}
                >
                  <td className="mono mute">{r.jiraKey || "—"}</td>
                  <td><ActionPill action={r.action} /></td>
                  <td className="mono">{r.mnemonic}</td>
                  <td style={{ maxWidth: 280, overflow: "hidden", textOverflow: "ellipsis" }}>{r.description}</td>
                  <td className="mono">{r.maid}</td>
                  <td className="mono">{r.ird}</td>
                  <td>{r.timeliness}</td>
                  <td>{r.regulated}</td>
                  <td>{r.posEntry}</td>
                  <td className="mono">{r.mcc}</td>
                  <td className="mono">{r.breakeven}</td>
                  <td>{r.transType}</td>
                  <td>{r.afs}</td>
                  <td className="mute">{r.region}</td>
                  <td className="mono">{r.currentRate}</td>
                  <td className="mono">{r.newRate}</td>
                  <td className="mute">{r.deltas}</td>
                  <td className="mono mute">{r.matchTag}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function EmptyState({ icon: Icon, title, body }) {
  return (
    <div style={{ padding: "60px 28px", display: "flex", justifyContent: "center" }}>
      <div style={{ textAlign: "center", maxWidth: 380 }}>
        <Icon size={28} color="var(--ink-dim)" style={{ marginBottom: 10 }} />
        <h3 className="h-display" style={{ fontSize: 15, fontWeight: 500, margin: "0 0 6px", color: "var(--ink-soft)" }}>
          {title}
        </h3>
        <p style={{ fontSize: 13, color: "var(--ink-mute)", margin: 0, lineHeight: 1.55 }}>
          {body}
        </p>
      </div>
    </div>
  );
}

/* ---------- Drawer ---------- */

function Drawer({ matchTag, onClose, onOpenJson, container = "screen" }) {
  const data = DRAWER_DATA[matchTag] || DRAWER_DATA["IT-R1"];
  const row = BASE_TABLE_ROWS_INTUIT.find(r => r.matchTag === matchTag);

  const etlCounts = {
    total: data.etlImpact.length,
    adds: data.etlImpact.filter(r => r.entryType === "ADD").length,
    removes: data.etlImpact.filter(r => r.entryType === "REMOVE").length,
    psonly: data.etlImpact.filter(r => r.entryType === "PEOPLESOFT_ONLY").length,
    nochange: data.etlImpact.filter(r => r.entryType === "NO_CHANGE").length,
  };
  const etlSubtitleParts = [];
  if (etlCounts.adds) etlSubtitleParts.push(`${etlCounts.adds} ADD`);
  if (etlCounts.removes) etlSubtitleParts.push(`${etlCounts.removes} REMOVE`);
  if (etlCounts.psonly) etlSubtitleParts.push(`${etlCounts.psonly} PEOPLESOFT_ONLY`);
  if (etlCounts.nochange) etlSubtitleParts.push(`${etlCounts.nochange} NO_CHANGE`);
  const etlSubtitle = `${etlCounts.total} row${etlCounts.total === 1 ? "" : "s"}` + (etlSubtitleParts.length ? ` · ${etlSubtitleParts.join(" · ")}` : "");

  // For Artifact Preview the drawer sits inside the artifact pane only;
  // for Results tab the drawer sits over the page-level table area.
  return (
    <>
      <div className="drawer-overlay" onClick={onClose} />
      <div className="drawer">
        <div style={{ padding: "20px 24px", borderBottom: "1px solid var(--glass-stroke)" }}>
          <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: 12 }}>
            <div style={{ minWidth: 0 }}>
              <div className="h-label" style={{ marginBottom: 4 }}>Record</div>
              <div className="h-display" style={{ fontSize: 17, fontWeight: 500, letterSpacing: "-0.015em" }}>
                <span className="mono">{row?.mnemonic}</span>
                <span style={{ color: "var(--ink-dim)", margin: "0 8px" }}>·</span>
                <span className="mono">{row?.maid}</span>
              </div>
              <div style={{ fontSize: 12, color: "var(--ink-mute)", marginTop: 4 }}>
                {row?.description}
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: 8, marginTop: 10 }}>
                <ActionPill action={row?.action} />
                <span className="mono" style={{ fontSize: 11, color: "var(--ink-dim)" }}>
                  match_tag: {matchTag}
                </span>
              </div>
            </div>
            <button className="btn btn-ghost btn-sm" style={{ padding: 6 }} onClick={onClose}>
              <X size={14} />
            </button>
          </div>
        </div>

        <DrawerPanel title="Field Deltas" subtitle="One row per changed field">
          {data.isAdd ? (
            <div style={{ padding: "10px 14px", color: "var(--ink-mute)", fontSize: 13, fontStyle: "italic" }}>
              No prior record — full add.
            </div>
          ) : data.fieldDeltas.length === 0 ? (
            <div style={{ padding: "10px 14px", color: "var(--ink-mute)", fontSize: 13 }}>
              No field-level changes.
            </div>
          ) : (
            <div style={{ overflowX: "auto" }}>
              <table className="ci-table" style={{ width: "100%" }}>
                <thead>
                  <tr>
                    <th>Field</th>
                    <th>Old</th>
                    <th>New</th>
                  </tr>
                </thead>
                <tbody>
                  {data.fieldDeltas.map((d, i) => (
                    <tr key={i} style={{ cursor: "default" }}>
                      <td className="mono">{d.field}</td>
                      <td className="mono mute">{d.old}</td>
                      <td className="mono" style={{ color: "var(--cyan)" }}>{d.new}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </DrawerPanel>

        <DrawerPanel title="ETL Impact" subtitle={etlSubtitle}>
          {data.truncateReload && (
            <div style={{
              padding: "10px 14px",
              borderBottom: "1px solid var(--glass-stroke)",
              fontSize: 12.5, color: "var(--ink-soft)",
              background: "rgba(247, 210, 143, 0.05)",
            }}>
              <strong style={{ color: "var(--amber)" }}>Truncate-and-reload:</strong>{" "}
              {data.truncateReload.existing} existing MCC rows replaced with {data.truncateReload.replacement} new rows.
            </div>
          )}
          <div style={{ maxHeight: 360, overflow: "auto" }}>
            <table className="ci-table" style={{ minWidth: 1480 }}>
              <thead>
                <tr>
                  <th>Entry Type</th>
                  <th>IRD</th>
                  <th>MAID</th>
                  <th>Mnemonic</th>
                  <th>MCC</th>
                  <th>Reg</th>
                  <th>POS Entry</th>
                  <th>Trans Type</th>
                  <th>Break Even</th>
                  <th>Rate</th>
                  <th>Region</th>
                  <th>System Update</th>
                </tr>
              </thead>
              <tbody>
                {data.etlImpact.map((r, i) => {
                  const rate = r.entryType === "REMOVE" ? row?.currentRate : row?.newRate;
                  return (
                    <tr key={i} style={{ cursor: "default" }} className={`etl-row-${r.entryType.toLowerCase().replace("_", "")}`}>
                      <td className="mono"><EntryPill type={r.entryType} /></td>
                      <td className="mono">{row?.ird || "—"}</td>
                      <td className="mono">{r.maid}</td>
                      <td className="mono">{r.mnemonic}</td>
                      <td className="mono">{r.mcc}</td>
                      <td>{row?.regulated || "—"}</td>
                      <td>{row?.posEntry || "—"}</td>
                      <td>{row?.transType || "—"}</td>
                      <td className="mono">{row?.breakeven || "—"}</td>
                      <td className="mono">{rate || "—"}</td>
                      <td className="mute">{row?.region || "—"}</td>
                      <td className="mono mute">{r.systemUpdate}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </DrawerPanel>

        <div style={{ padding: "18px 24px 28px" }}>
          <button className="btn btn-ghost btn-sm" onClick={onOpenJson}>
            <Eye size={12} />
            View raw extract JSON
          </button>
          <p style={{ fontSize: 11, color: "var(--ink-dim)", margin: "8px 0 0", lineHeight: 1.5 }}>
            Shows the 34-field vision extract that produced this row. Debug-only.
          </p>
        </div>
      </div>
    </>
  );
}

function DrawerPanel({ title, subtitle, children }) {
  return (
    <div style={{ borderBottom: "1px solid var(--glass-stroke)" }}>
      <div style={{ padding: "16px 24px 12px" }}>
        <div className="h-label">{title}</div>
        <div style={{ fontSize: 11.5, color: "var(--ink-dim)", marginTop: 2 }}>{subtitle}</div>
      </div>
      {children}
    </div>
  );
}

function EntryPill({ type }) {
  const map = {
    "ADD": { color: "var(--add)", bg: "rgba(110,231,160,0.16)", border: "rgba(110,231,160,0.3)" },
    "REMOVE": { color: "var(--remove)", bg: "rgba(252,165,165,0.16)", border: "rgba(252,165,165,0.3)" },
    "NO_CHANGE": { color: "var(--nochange)", bg: "rgba(148,163,184,0.16)", border: "rgba(148,163,184,0.3)" },
    "PEOPLESOFT_ONLY": { color: "var(--psonly)", bg: "rgba(196,181,253,0.16)", border: "rgba(196,181,253,0.3)" },
  };
  const s = map[type] || map.ADD;
  return (
    <span style={{
      display: "inline-block",
      padding: "2px 7px",
      borderRadius: 4,
      fontFamily: "var(--font-mono)",
      fontSize: 10.5,
      fontWeight: 600,
      letterSpacing: "0.05em",
      color: s.color,
      background: s.bg,
      border: `1px solid ${s.border}`,
    }}>{type}</span>
  );
}

/* ---------- Raw JSON modal ---------- */

function RawJsonModal({ matchTag, onClose }) {
  const data = DRAWER_DATA[matchTag] || DRAWER_DATA["IT-R1"];
  const row = BASE_TABLE_ROWS_INTUIT.find(r => r.matchTag === matchTag);
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="glass-strong modal" onClick={e => e.stopPropagation()}>
        <div style={{ padding: "18px 22px", borderBottom: "1px solid var(--glass-stroke)", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <div>
            <div className="h-label" style={{ marginBottom: 4 }}>Raw vision extract</div>
            <div className="h-display" style={{ fontSize: 15, fontWeight: 500 }}>
              <span className="mono">{row?.mnemonic}</span>
              <span style={{ color: "var(--ink-dim)", margin: "0 6px" }}>·</span>
              <span className="mono">{row?.maid}</span>
            </div>
          </div>
          <button className="btn btn-ghost btn-sm" style={{ padding: 6 }} onClick={onClose}>
            <X size={14} />
          </button>
        </div>
        <pre style={{
          margin: 0,
          padding: "18px 22px 24px",
          fontFamily: "var(--font-mono)",
          fontSize: 11.5,
          lineHeight: 1.7,
          color: "var(--ink-soft)",
          whiteSpace: "pre-wrap",
          wordBreak: "break-word",
        }}>
{JSON.stringify(data.sourceRecord, null, 2)}
        </pre>
      </div>
    </div>
  );
}

/* ---------- Issues Tab ---------- */

function IssuesTab({ runState, showCosmetic, dispatch }) {
  if (runState === "pre-run") {
    return <EmptyState icon={AlertTriangle} title="No issues" body="Issues populate during run execution." />;
  }
  if (runState === "stale") {
    return <EmptyState icon={Clock} title="Issues data not available" body="This run predates the gated-approval build." />;
  }
  const isFailed = runState === "failed-staged" || runState === "failed-approval";
  let issues = SAMPLE_ISSUES;
  if (!showCosmetic) issues = issues.filter(i => !i.cosmetic);
  if (runState === "mid-staged") issues = issues.slice(0, 1);
  if (!isFailed && runState === "submitted") issues = issues.filter(i => i.severity !== "CRITICAL");

  return (
    <div style={{ padding: "16px 28px 40px" }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 16, gap: 12, flexWrap: "wrap" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <span className="h-label">Issues</span>
          <span className="mono" style={{ fontSize: 11.5, color: "var(--ink-mute)" }}>
            {issues.length} visible
          </span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
          <ToggleSwitch
            checked={showCosmetic}
            onChange={() => dispatch({ type: "toggle", key: "showCosmetic" })}
            label="Show known cosmetic warnings"
          />
          {isFailed && (
            <>
              <button className="btn btn-sm">
                <RotateCw size={12} />
                Re-run from scratch
              </button>
              {runState === "failed-approval" && (
                <button className="btn btn-warm btn-sm">
                  <RefreshCw size={12} />
                  Retry Approve
                </button>
              )}
            </>
          )}
        </div>
      </div>

      {issues.length === 0 ? (
        <EmptyState icon={CheckCircle2} title="No issues for this run" body={showCosmetic ? "Nothing to surface." : "Toggle on to see cosmetic warnings."} />
      ) : (
        <div className="stagger" style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          {issues.map(iss => <IssueCard key={iss.id} issue={iss} dispatch={dispatch} />)}
        </div>
      )}
    </div>
  );
}

function IssueCard({ issue, dispatch }) {
  const sevMap = {
    CRITICAL: { Icon: AlertOctagon, cls: "pill-crit", color: "var(--crit)" },
    ERROR: { Icon: AlertCircle, cls: "pill-err", color: "var(--err)" },
    WARNING: { Icon: AlertTriangle, cls: "pill-warn", color: "var(--warn)" },
  };
  const { Icon, cls, color } = sevMap[issue.severity];
  const handleClick = issue.scope?.matchTag
    ? () => dispatch({ type: "deepLinkToResults", matchTag: issue.scope.matchTag })
    : undefined;

  return (
    <div
      className="glass"
      style={{
        padding: 16,
        cursor: handleClick ? "pointer" : "default",
        transition: "border-color 200ms",
      }}
      onClick={handleClick}
      onMouseEnter={e => handleClick && (e.currentTarget.style.borderColor = "rgba(125,211,252,0.36)")}
      onMouseLeave={e => handleClick && (e.currentTarget.style.borderColor = "var(--glass-stroke)")}
    >
      <div style={{ display: "flex", alignItems: "flex-start", gap: 12 }}>
        <div style={{
          width: 28, height: 28, borderRadius: 6,
          display: "flex", alignItems: "center", justifyContent: "center",
          background: cls === "pill-crit" ? "rgba(248,113,113,0.12)" :
                       cls === "pill-err" ? "rgba(251,146,60,0.12)" :
                       "rgba(250,204,21,0.10)",
          flexShrink: 0,
        }}>
          <Icon size={14} color={color} />
        </div>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 6 }}>
            <span className={`pill ${cls}`}>{issue.severity}</span>
            {issue.scope && (
              <span className="mono" style={{ fontSize: 10.5, color: "var(--ink-mute)" }}>
                {issue.scope.maid && `MAID ${issue.scope.maid}`}
                {issue.scope.mnemonic && ` · ${issue.scope.mnemonic}`}
              </span>
            )}
            {handleClick && (
              <span style={{
                marginLeft: "auto",
                display: "flex", alignItems: "center", gap: 4,
                fontSize: 11, color: "var(--cyan)",
              }}>
                Open in Results
                <ArrowUpRight size={11} />
              </span>
            )}
          </div>
          <div style={{ fontSize: 13.5, fontWeight: 500, color: "var(--ink)", marginBottom: 4 }}>
            {issue.message}
          </div>
          <div style={{ fontSize: 12.5, color: "var(--ink-mute)", lineHeight: 1.55 }}>
            {issue.detail}
          </div>
          {issue.remediation && (
            <div style={{
              marginTop: 10, padding: "8px 11px",
              background: "rgba(125,211,252,0.05)",
              borderRadius: 6,
              borderLeft: "2px solid rgba(125,211,252,0.4)",
              fontSize: 12, color: "var(--ink-soft)",
              lineHeight: 1.55,
            }}>
              <span className="h-label" style={{ display: "block", marginBottom: 2, color: "var(--cyan)", fontSize: 9.5 }}>
                Remediation
              </span>
              {issue.remediation}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function ToggleSwitch({ checked, onChange, label }) {
  return (
    <label style={{ display: "inline-flex", alignItems: "center", gap: 8, cursor: "pointer", userSelect: "none" }}>
      <span style={{
        position: "relative",
        width: 30, height: 16, borderRadius: 999,
        background: checked ? "rgba(125,211,252,0.32)" : "rgba(255,255,255,0.08)",
        border: "1px solid",
        borderColor: checked ? "rgba(125,211,252,0.5)" : "var(--glass-stroke)",
        transition: "all 200ms",
      }}>
        <span style={{
          position: "absolute",
          top: 1,
          left: checked ? 15 : 1,
          width: 12, height: 12, borderRadius: 999,
          background: checked ? "var(--cyan)" : "var(--ink-mute)",
          boxShadow: checked ? "0 0 8px rgba(125,211,252,0.5)" : "none",
          transition: "all 200ms cubic-bezier(0.2, 0.7, 0.2, 1)",
        }} />
      </span>
      <span style={{ fontSize: 12, color: "var(--ink-soft)" }}>{label}</span>
      <input type="checkbox" checked={checked} onChange={onChange} style={{ display: "none" }} />
    </label>
  );
}

/* ---------- Run Detail Screen ---------- */

function RunDetailScreen({ state, dispatch }) {
  const run = SAMPLE_RUNS.find(r => r.id === state.currentRunId) || SAMPLE_RUNS[0];
  const runState = state.runState;

  return (
    <div className="reveal" style={{ position: "relative" }}>
      <RunContextStrip
        run={run}
        state={runState}
        runLock={state.runLockHeld}
        approvalLock={state.approvalLockHeld}
        onApprove={() => dispatch({ type: "runState", runState: "mid-approval" })}
        onArtifact={() => dispatch({ type: "screen", screen: "artifact-preview" })}
        dispatch={dispatch}
      />
      <TabBar
        tab={state.tab}
        setTab={t => dispatch({ type: "tab", tab: t })}
        issuesCount={runState === "pre-run" || runState === "stale" ? 0 :
                      runState === "submitted" ? 0 :
                      runState === "mid-staged" ? 1 :
                      state.showCosmetic ? 5 : 3}
        runState={runState}
      />
      <div style={{ position: "relative" }}>
        {state.tab === "activity" && <ActivityTab runState={runState} runLock={state.runLockHeld} />}
        {state.tab === "results" && runState !== "pre-run" && (
          <ResultsTab
            runState={runState}
            openRow={state.drawerOpenMatchTag}
            setOpenRow={mt => dispatch({ type: "drawer", matchTag: mt })}
            dispatch={dispatch}
          />
        )}
        {state.tab === "results" && runState === "pre-run" && (
          <EmptyState icon={ListTree} title="Run not started" body="Results populate after Step 3 outputs land." />
        )}
        {state.tab === "issues" && (
          <IssuesTab
            runState={runState}
            showCosmetic={state.showCosmetic}
            dispatch={dispatch}
          />
        )}
        {state.drawerOpenMatchTag && state.tab === "results" && (
          <Drawer
            matchTag={state.drawerOpenMatchTag}
            onClose={() => dispatch({ type: "drawer", matchTag: null })}
            onOpenJson={() => dispatch({ type: "rawJson", open: true })}
          />
        )}
      </div>
    </div>
  );
}

/* ---------- Runs List Screen ---------- */

function RunsListScreen({ state, dispatch }) {
  const [filter, setFilter] = useState("all");
  const [search, setSearch] = useState("");

  const filtered = useMemo(() => {
    let r = SAMPLE_RUNS;
    if (filter !== "all") {
      if (filter === "in-progress") {
        r = r.filter(x => x.state === "mid-staged" || x.state === "mid-approval");
      } else {
        r = r.filter(x => x.state === filter);
      }
    }
    if (search) {
      const s = search.toLowerCase();
      r = r.filter(x => x.merchant.toLowerCase().includes(s) || x.maids.some(m => m.includes(search)));
    }
    return r;
  }, [filter, search]);

  return (
    <div className="reveal" style={{ padding: "16px 28px 40px" }}>
      <div className="glass" style={{ padding: "18px 22px", marginBottom: 16 }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 16, marginBottom: 14, flexWrap: "wrap" }}>
          <div>
            <h1 className="h-display" style={{ fontSize: 20, fontWeight: 500, margin: 0, letterSpacing: "-0.015em" }}>
              Runs
            </h1>
            <p style={{ fontSize: 12, color: "var(--ink-mute)", margin: "4px 0 0" }}>
              All staged and submitted runs across operators · sorted by recency
            </p>
          </div>
          <button
            className="btn btn-primary"
            disabled={state.runLockHeld}
            title={state.runLockHeld ? "An active run is in progress" : ""}
            onClick={() => { dispatch({ type: "screen", screen: "run-detail" }); dispatch({ type: "runState", runState: "pre-run" }); }}
          >
            <Plus size={13} />
            Start New Run
          </button>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 12, flexWrap: "wrap" }}>
          <div className="input" style={{ flex: 1, minWidth: 240, maxWidth: 360 }}>
            <Search size={13} color="var(--ink-mute)" />
            <input
              type="text"
              value={search}
              onChange={e => setSearch(e.target.value)}
              placeholder="Search by MAID or merchant…"
            />
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 6, flexWrap: "wrap" }}>
            {[
              { id: "all", label: "All" },
              { id: "pre-approval", label: "Pre-approval" },
              { id: "submitted", label: "Submitted" },
              { id: "in-progress", label: "In progress" },
              { id: "stale", label: "Stale" },
            ].map(c => (
              <span key={c.id} className={`chip ${filter === c.id ? "active" : ""}`} onClick={() => setFilter(c.id)}>
                {c.label}
              </span>
            ))}
          </div>
        </div>
      </div>

      <div className="glass" style={{ overflow: "hidden" }}>
        {filtered.length === 0 ? (
          <div style={{ padding: 60 }}>
            <EmptyState
              icon={Search}
              title={search ? `No runs found for '${search}'` : "No runs match this filter"}
              body={search ? "Try a different MAID or merchant name." : "Switch to All or start a new run."}
            />
          </div>
        ) : (
          <table className="ci-table">
            <thead>
              <tr>
                <th>Run</th>
                <th>State</th>
                <th>MAIDs</th>
                <th>Started</th>
                <th>Jira</th>
                <th style={{ textAlign: "right" }}>Action</th>
              </tr>
            </thead>
            <tbody className="stagger">
              {filtered.map(r => (
                <tr key={r.id} onClick={() => { dispatch({ type: "screen", screen: "run-detail" }); dispatch({ type: "currentRun", runId: r.id }); dispatch({ type: "runState", runState: r.state }); }}>
                  <td>
                    <div style={{ display: "flex", flexDirection: "column", lineHeight: 1.2 }}>
                      <span style={{ fontWeight: 500, color: "var(--ink)" }}>{r.merchant}</span>
                      <span className="mono" style={{ fontSize: 10.5, color: "var(--ink-dim)", marginTop: 2 }}>{r.id}</span>
                    </div>
                  </td>
                  <td>
                    <StateBadge state={r.state} size="sm" />
                    {r.issuesCount > 0 && (
                      <span className="tab-count" style={{ marginLeft: 6 }}>{r.issuesCount}</span>
                    )}
                  </td>
                  <td className="mono">
                    {r.maids.slice(0, 2).join(", ")}
                    {r.maids.length > 2 && <span className="mute"> +{r.maids.length - 2}</span>}
                  </td>
                  <td className="mono mute">{r.timestamp}</td>
                  <td>
                    {r.jiraEpic ? (
                      <div style={{ display: "flex", flexDirection: "column", lineHeight: 1.3 }}>
                        <span className="mono" style={{ fontSize: 11.5 }}>{r.jiraEpic}</span>
                        <span className="mono" style={{ fontSize: 10.5, color: "var(--ink-mute)" }}>{r.jiraStory}</span>
                      </div>
                    ) : <span className="mute">—</span>}
                  </td>
                  <td style={{ textAlign: "right" }}>
                    <span style={{ display: "inline-flex", alignItems: "center", gap: 4, color: "var(--cyan)", fontSize: 12 }}>
                      View
                      <ChevronRight size={12} />
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
        <div style={{
          padding: "10px 18px",
          borderTop: "1px solid var(--glass-stroke)",
          display: "flex", alignItems: "center", justifyContent: "space-between",
          fontSize: 11.5, color: "var(--ink-mute)",
        }}>
          <span>Showing {filtered.length} of {SAMPLE_RUNS.length}</span>
          <div style={{ display: "flex", gap: 6 }}>
            <button className="btn btn-ghost btn-sm" disabled>‹ Prev</button>
            <button className="btn btn-ghost btn-sm" disabled>Next ›</button>
          </div>
        </div>
      </div>
    </div>
  );
}

/* ---------- Artifact Preview Screen ---------- */

function ArtifactPreviewScreen({ state, dispatch }) {
  const run = SAMPLE_RUNS.find(r => r.id === state.currentRunId) || SAMPLE_RUNS[0];
  const [split, setSplit] = useState(62);
  const draggingRef = useRef(false);
  const containerRef = useRef(null);

  const onMouseDown = (e) => {
    draggingRef.current = true;
    e.preventDefault();
  };
  useEffect(() => {
    const onMove = (e) => {
      if (!draggingRef.current || !containerRef.current) return;
      const rect = containerRef.current.getBoundingClientRect();
      const pct = ((e.clientX - rect.left) / rect.width) * 100;
      setSplit(Math.max(35, Math.min(80, pct)));
    };
    const onUp = () => { draggingRef.current = false; };
    window.addEventListener("mousemove", onMove);
    window.addEventListener("mouseup", onUp);
    return () => {
      window.removeEventListener("mousemove", onMove);
      window.removeEventListener("mouseup", onUp);
    };
  }, []);

  return (
    <div className="reveal" style={{ padding: "16px 28px 28px" }}>
      <div className="glass" style={{
        padding: "12px 18px", display: "flex", alignItems: "center", justifyContent: "space-between",
        marginBottom: 14, gap: 12, flexWrap: "wrap",
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
          <button className="btn btn-ghost btn-sm" onClick={() => dispatch({ type: "screen", screen: "run-detail" })}>
            <ArrowLeft size={12} />
            Back to Run Detail
          </button>
          <div style={{ width: 1, height: 18, background: "var(--glass-stroke)" }} />
          <div style={{ display: "flex", flexDirection: "column", lineHeight: 1.2 }}>
            <span className="h-display" style={{ fontSize: 14, fontWeight: 500 }}>{run.merchant} · Artifact Preview</span>
            <span className="mono" style={{ fontSize: 10.5, color: "var(--ink-mute)" }}>{run.id}</span>
          </div>
          <StateBadge state={state.runState} size="sm" />
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <button className="btn btn-ghost btn-sm">
            <Download size={12} />
            Download PDF
          </button>
        </div>
      </div>

      <div ref={containerRef} style={{
        display: "flex",
        height: "calc(100vh - 180px)",
        minHeight: 540,
        position: "relative",
      }}>
        {/* Artifact pane */}
        <div className="glass" style={{
          flex: `0 0 ${split}%`,
          overflow: "hidden",
          position: "relative",
          display: "flex",
          flexDirection: "column",
        }}>
          <div style={{
            padding: "12px 16px",
            borderBottom: "1px solid var(--glass-stroke)",
            display: "flex", alignItems: "center", justifyContent: "space-between",
          }}>
            <span className="h-label">Pipeline output · base table</span>
            <span className="mono" style={{ fontSize: 11, color: "var(--ink-dim)" }}>
              {BASE_TABLE_ROWS_INTUIT.length} rows
            </span>
          </div>
          <div style={{ overflow: "auto", flex: 1, position: "relative" }}>
            <table className="ci-table" style={{ minWidth: 1200 }}>
              <thead>
                <tr>
                  <th>Action</th>
                  <th>Mnemonic</th>
                  <th>MAID</th>
                  <th>MCC</th>
                  <th>Current Rate</th>
                  <th>New Rate</th>
                  <th>Deltas</th>
                  <th>Match Tag</th>
                </tr>
              </thead>
              <tbody>
                {BASE_TABLE_ROWS_INTUIT.map(r => (
                  <tr
                    key={r.matchTag}
                    className={state.drawerOpenMatchTag === r.matchTag ? "selected" : ""}
                    onClick={() => dispatch({ type: "drawer", matchTag: state.drawerOpenMatchTag === r.matchTag ? null : r.matchTag })}
                  >
                    <td><ActionPill action={r.action} /></td>
                    <td className="mono">{r.mnemonic}</td>
                    <td className="mono">{r.maid}</td>
                    <td className="mono">{r.mcc}</td>
                    <td className="mono">{r.currentRate}</td>
                    <td className="mono">{r.newRate}</td>
                    <td className="mute">{r.deltas}</td>
                    <td className="mono mute">{r.matchTag}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            {state.drawerOpenMatchTag && (
              <Drawer
                matchTag={state.drawerOpenMatchTag}
                onClose={() => dispatch({ type: "drawer", matchTag: null })}
                onOpenJson={() => dispatch({ type: "rawJson", open: true })}
              />
            )}
          </div>
        </div>

        <div
          className="split-divider"
          onMouseDown={onMouseDown}
        >
          <div style={{
            position: "absolute", top: "50%", left: "50%",
            transform: "translate(-50%, -50%)",
            width: 4, height: 36,
            background: "rgba(255,255,255,0.10)",
            borderRadius: 4,
            display: "flex", alignItems: "center", justifyContent: "center",
            pointerEvents: "none",
          }} />
        </div>

        {/* PDF pane */}
        <div className="glass" style={{
          flex: 1,
          overflow: "hidden",
          display: "flex",
          flexDirection: "column",
        }}>
          <div style={{
            padding: "12px 16px",
            borderBottom: "1px solid var(--glass-stroke)",
            display: "flex", alignItems: "center", justifyContent: "space-between",
          }}>
            <span className="h-label">Original agreement · PDF</span>
            <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
              <button className="btn btn-ghost btn-sm" style={{ padding: 4 }}><ZoomOut size={12} /></button>
              <span className="mono" style={{ fontSize: 11, color: "var(--ink-mute)", padding: "0 6px" }}>Page 3 / 6</span>
              <button className="btn btn-ghost btn-sm" style={{ padding: 4 }}><ZoomIn size={12} /></button>
            </div>
          </div>
          <div style={{
            flex: 1, overflow: "auto",
            background: "rgba(0,0,0,0.25)",
            padding: 24,
          }}>
            <MockPdfPage />
          </div>
        </div>
      </div>
    </div>
  );
}

/* ---------- Mock PDF page ---------- */

function MockPdfPage() {
  return (
    <div style={{
      background: "#f4ede0",
      color: "#1a1410",
      padding: "32px 36px",
      maxWidth: 540,
      margin: "0 auto",
      boxShadow: "0 12px 48px rgba(0, 0, 0, 0.5)",
      fontFamily: "'Georgia', 'Times New Roman', serif",
      fontSize: 11,
      lineHeight: 1.55,
      minHeight: 700,
    }}>
      <div style={{ borderBottom: "1px solid #c9bda7", paddingBottom: 12, marginBottom: 16, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <div style={{ fontFamily: "'Helvetica Neue', sans-serif", fontSize: 9, letterSpacing: "0.12em", textTransform: "uppercase", color: "#7a6d5c" }}>
            Mastercard Pricing Program
          </div>
          <div style={{ fontWeight: 700, fontSize: 14, marginTop: 2 }}>
            Intuit — Custom Interchange Agreement
          </div>
        </div>
        <div style={{ fontFamily: "'Helvetica Neue', sans-serif", fontSize: 9, color: "#7a6d5c", textAlign: "right" }}>
          Effective Date<br />
          <strong style={{ fontSize: 11, color: "#1a1410" }}>2026-04-01</strong>
        </div>
      </div>

      <p style={{ marginTop: 0 }}>
        <strong>3.2 Mnemonic Rate Schedule.</strong> The following interchange rates are
        established under this Agreement for the MAIDs listed in Schedule A,
        effective as of the Effective Date stated above:
      </p>

      <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 10, margin: "10px 0 14px" }}>
        <thead>
          <tr style={{ background: "#e6dcc6" }}>
            <th style={{ padding: "6px 8px", textAlign: "left", border: "1px solid #c9bda7" }}>Mnemonic</th>
            <th style={{ padding: "6px 8px", textAlign: "left", border: "1px solid #c9bda7" }}>Description</th>
            <th style={{ padding: "6px 8px", textAlign: "right", border: "1px solid #c9bda7" }}>Rate</th>
            <th style={{ padding: "6px 8px", textAlign: "right", border: "1px solid #c9bda7" }}>Per Item</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td style={{ padding: "5px 8px", border: "1px solid #c9bda7", fontFamily: "monospace" }}>VS2-CONS</td>
            <td style={{ padding: "5px 8px", border: "1px solid #c9bda7" }}>VS Consumer Credit Premium Tier</td>
            <td style={{ padding: "5px 8px", border: "1px solid #c9bda7", textAlign: "right" }}>1.85%</td>
            <td style={{ padding: "5px 8px", border: "1px solid #c9bda7", textAlign: "right" }}>$0.10</td>
          </tr>
          <tr style={{ background: "#f7f0df" }}>
            <td style={{ padding: "5px 8px", border: "1px solid #c9bda7", fontFamily: "monospace" }}>VS2-CMRC</td>
            <td style={{ padding: "5px 8px", border: "1px solid #c9bda7" }}>VS Commercial Tier 1</td>
            <td style={{ padding: "5px 8px", border: "1px solid #c9bda7", textAlign: "right" }}>2.20%</td>
            <td style={{ padding: "5px 8px", border: "1px solid #c9bda7", textAlign: "right" }}>$0.10</td>
          </tr>
          <tr>
            <td style={{ padding: "5px 8px", border: "1px solid #c9bda7", fontFamily: "monospace" }}>MAB7</td>
            <td style={{ padding: "5px 8px", border: "1px solid #c9bda7" }}>MC MPP Unregulated Consumer Debit</td>
            <td style={{ padding: "5px 8px", border: "1px solid #c9bda7", textAlign: "right" }}>1.15%</td>
            <td style={{ padding: "5px 8px", border: "1px solid #c9bda7", textAlign: "right" }}>$0.15</td>
          </tr>
          <tr style={{ background: "#f7f0df" }}>
            <td style={{ padding: "5px 8px", border: "1px solid #c9bda7", fontFamily: "monospace" }}>MA47</td>
            <td style={{ padding: "5px 8px", border: "1px solid #c9bda7" }}>MC MPP Consumer Credit World (MCCs 5411, 5732, 5734)</td>
            <td style={{ padding: "5px 8px", border: "1px solid #c9bda7", textAlign: "right" }}>1.60%</td>
            <td style={{ padding: "5px 8px", border: "1px solid #c9bda7", textAlign: "right" }}>$0.10</td>
          </tr>
        </tbody>
      </table>

      <p>
        <strong>3.3 Breakeven Thresholds.</strong> Breakeven thresholds apply per row
        as set forth in Schedule A. Where a low-breakeven condition is set to
        "LE" with a value of 120.00, transactions of amounts less than or equal
        to USD 120.00 qualify under the applicable mnemonic.
      </p>

      <p>
        <strong>3.4 MCC Expansion.</strong> Effective with this Agreement, the
        following MCCs are added to the qualifying merchant category for
        mnemonic MA47: 5734. The full set of qualifying MCCs is enumerated in
        Schedule B.
      </p>

      <div style={{
        marginTop: 24, paddingTop: 12,
        borderTop: "1px solid #c9bda7",
        display: "flex", justifyContent: "space-between",
        fontFamily: "'Helvetica Neue', sans-serif", fontSize: 9, color: "#7a6d5c",
      }}>
        <span>MAID 1411424–1411427 · Region: US</span>
        <span>Page 3 of 6</span>
      </div>
    </div>
  );
}

/* ---------- Toast ---------- */

function Toast({ visible, onClose, onClick }) {
  if (!visible) return null;
  return (
    <div className="glass-strong toast" onClick={onClick}>
      <div style={{ display: "flex", alignItems: "flex-start", gap: 10 }}>
        <div style={{
          width: 28, height: 28, borderRadius: 8,
          background: "rgba(247,210,143,0.16)",
          border: "1px solid rgba(247,210,143,0.32)",
          display: "flex", alignItems: "center", justifyContent: "center",
          flexShrink: 0,
        }}>
          <Bell size={13} color="var(--amber)" />
        </div>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ fontSize: 12.5, fontWeight: 500, color: "var(--ink)", marginBottom: 2 }}>
            Run ready for approval
          </div>
          <div style={{ fontSize: 11.5, color: "var(--ink-mute)", lineHeight: 1.5 }}>
            <span className="mono">Intuit · 12:43</span> finished staging. Click to review.
          </div>
        </div>
        <button onClick={(e) => { e.stopPropagation(); onClose(); }} style={{
          background: "transparent", border: "none", padding: 2,
          color: "var(--ink-dim)", cursor: "pointer", flexShrink: 0,
        }}>
          <X size={12} />
        </button>
      </div>
    </div>
  );
}

/* ---------- Reducer ---------- */

const INITIAL_STATE = {
  screen: "run-detail",        // 'run-detail' | 'runs-list' | 'artifact-preview'
  currentRunId: "intuit_20260514_124300",
  runState: "pre-approval",    // see STATE_LABELS
  tab: "results",              // 'activity' | 'results' | 'issues'
  drawerOpenMatchTag: null,
  rawJsonOpen: false,
  showCosmetic: false,
  runLockHeld: false,
  approvalLockHeld: false,
  toastVisible: false,
  controllerOpen: true,
};

function reducer(s, a) {
  switch (a.type) {
    case "screen":
      return { ...s, screen: a.screen };
    case "currentRun":
      return { ...s, currentRunId: a.runId };
    case "runState":
      return { ...s, runState: a.runState, drawerOpenMatchTag: null };
    case "tab":
      return { ...s, tab: a.tab };
    case "drawer":
      return { ...s, drawerOpenMatchTag: a.matchTag };
    case "rawJson":
      return { ...s, rawJsonOpen: a.open };
    case "toggle":
      return { ...s, [a.key]: !s[a.key] };
    case "deepLinkToResults":
      return { ...s, tab: "results", drawerOpenMatchTag: a.matchTag };
    case "showToast":
      return { ...s, toastVisible: true };
    case "hideToast":
      return { ...s, toastVisible: false };
    case "controller":
      return { ...s, controllerOpen: !s.controllerOpen };
    default:
      return s;
  }
}

/* ---------- Root ---------- */

export default function App() {
  const [state, dispatch] = React.useReducer(reducer, INITIAL_STATE);

  // Auto-hide toast
  useEffect(() => {
    if (!state.toastVisible) return;
    const t = setTimeout(() => dispatch({ type: "hideToast" }), 6000);
    return () => clearTimeout(t);
  }, [state.toastVisible]);

  // Toggle keyboard for state controller
  useEffect(() => {
    const onKey = (e) => {
      if (e.key === "/" && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        dispatch({ type: "controller" });
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  const handleToggle = (which) => {
    if (which === "all-runs") dispatch({ type: "screen", screen: "runs-list" });
    else dispatch({ type: "screen", screen: "run-detail" });
  };

  return (
    <div className="ci-root">
      <GlobalStyle />
      <div className="ci-bg" />
      <div className="ci-grain" />

      <AppShell
        currentScreen={state.screen}
        onToggle={handleToggle}
        onBellClick={() => dispatch({ type: state.toastVisible ? "hideToast" : "showToast" })}
        toastVisible={state.toastVisible}
      >
        {state.screen === "run-detail" && <RunDetailScreen state={state} dispatch={dispatch} />}
        {state.screen === "runs-list" && <RunsListScreen state={state} dispatch={dispatch} />}
        {state.screen === "artifact-preview" && <ArtifactPreviewScreen state={state} dispatch={dispatch} />}
      </AppShell>

      {/* Floating state controller toggle */}
      {!state.controllerOpen && (
        <button
          className="btn btn-ghost"
          style={{
            position: "fixed", top: 80, right: 24, zIndex: 55,
            padding: "8px 10px",
          }}
          onClick={() => dispatch({ type: "controller" })}
          title="Toggle mockup state controller (⌘/)"
        >
          <Settings2 size={13} />
        </button>
      )}
      <StateController
        open={state.controllerOpen}
        onClose={() => dispatch({ type: "controller" })}
        state={state}
        dispatch={dispatch}
      />

      <Toast
        visible={state.toastVisible}
        onClose={() => dispatch({ type: "hideToast" })}
        onClick={() => {
          dispatch({ type: "hideToast" });
          dispatch({ type: "screen", screen: "run-detail" });
          dispatch({ type: "runState", runState: "pre-approval" });
          dispatch({ type: "tab", tab: "results" });
        }}
      />

      {state.rawJsonOpen && state.drawerOpenMatchTag && (
        <RawJsonModal
          matchTag={state.drawerOpenMatchTag}
          onClose={() => dispatch({ type: "rawJson", open: false })}
        />
      )}
    </div>
  );
}
