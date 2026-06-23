# Skills Index — PDLC_App_v2

**Project:** PDLC_App_v2
**Owner:** V (Varun Munjal), JPMC Merchant Services AI Automation Team
**Source of truth:** `BUILD_OVERVIEW.md` + `brd_frd_overview.html` (the 5-layer wireframe) + `REQUIREMENTS.md`
**Supersedes:** the v1 platform catalog (`PDLC_Platform_Design_Spec_v1.md`, `pdlc_platform_app.html`, and the prior 8-layer L0–L8 index). Those are **v1 artifacts — not authoritative for v2.**

---

## How to read this index

This catalog lists every skill in the **5-layer agentic pipeline**: Data & context → BRD → FRD → Jira epics → Metrics. The individual skill files (`<skill>.skill.md`, in `core/`) are the instruction modules.

**Execution model.** A skill is loaded and executed **in-session by the selected agent (Claude Code or Copilot)** reading its `.skill.md` file against runtime input — **no direct Claude API call (MVP)** (FR-XS-04). Skills are generic engines; per-domain substance comes from a profile/template (`brd_profile.<domain>.yaml`, etc.). Python is *called by* agents for deterministic plumbing only; it never drives the session.

### Skill types (v2)

- **Authoring (user-invocable)** — an interactive agent that drives a chat with the operator to produce an artifact (BRD, FRD). Its own session/window; the human talks to it directly.
- **Worker (subagent)** — an autonomous, non-interactive subagent invoked by an authoring skill or coordinator (fan-out processing, code mapping, impact assessment). Internal context window; not a chat surface.
- **Validator (subagent)** — checks an artifact for coverage/traceability and returns a score + gap list that feeds a human gate.
- **Adapter** — connector logic at a seam: generic ingestion connectors (per source-type) and the `jpmc_adapters` push/auth seam. The **domain pre-processing adapter** is the swappable domain seam.
- **Plumbing (Python)** — deterministic, non-model steps (clone, ingest, hydrate, `merge_manifest`). Listed for completeness; not generation skills.
- **Runtime utility** — environment/bootstrap helpers applied locally (e.g. `max-autonomy`).

### Cross-cutting patterns every skill respects

- **Two seams only.** Variation is confined to the **domain seam** (adapter / profiles / template / tag vocabulary) and the **runtime-tool seam** (instruction file / wrappers / prompt files). (FR-XS-01)
- **In-session execution, no API.** All generation runs in the Claude Code / Copilot session. (FR-XS-04)
- **Always-selective read.** The manifest (`index.json`) is always loaded; agents pull only section-relevant files. No RAG/vector store. (FR-DC-06)
- **Cite-or-flag.** Every substantive claim is grounded to a source / the `UI_INPUT` frame / an operator answer, or marked `[TBD — unsourced]`. Never fabricated. (FR-BR-06)
- **Human-mediated flag loop.** `code_impact` surfaces scope flags; the operator decides; the agent never auto-applies scope changes. (FR-BR-08)
- **BRD-as-spine.** When `BRD.md` is accepted (BRD vN), FRD and Jira lock to that version; re-opening BRD → vN+1. (FR-XS-14)
- **Human gates G0–G3.** Scaffold checkpoint, BRD acceptance, FRD acceptance, single Jira push gate. (D4)
- **Telemetry → JSONL → metrics.** Every invocation emits events to `telemetry.jsonl`; Layer 5 is computed by scanning them. (D8)

### File naming

Individual skill files follow `<skill_name>.skill.md` in `core/`, with thin per-tool wrappers in each overlay (`.claude/agents/` for Claude Code, `*.agent.md` for Copilot) pointing at the shared skill.

---

# Layer 1 — Data & context

**Configure → ingest → pre-process (domain adapter) → serve.** Processing fans out per source into `context_set/` + `index.json`. (BUILD_OVERVIEW §6)

### Ingestion connectors (generic, per source-type)

- **Type:** Adapter
- **Consumes:** source URL/path + auth (from `UI_INPUT.yaml` + `jpmc_adapters`)
- **Produces:** raw fetched content per source (for code: `git clone` the repo by SEAL ID into `repo/`)
- **Rules:** Domain-agnostic, **keyed by source-type** (Confluence / SharePoint / Bitbucket), reused across every domain; a new source type is a new generic connector, never a domain fork. (FR-DC-02, FR-DC-11)

### Domain pre-processing adapter (the domain seam)

- **Type:** Adapter (swappable per domain)
- **Consumes:** raw source content
- **Produces:** provenance-tagged `context_set/` slices + manifest entries (docs → extract / summarize / classify-assess; code → hands to `code_map_build`)
- **Rules:** This is the per-domain seam. Tags drawn **only** from the domain's canonical vocabulary; every required profile topic has a producing adapter. (FR-DC-03, FR-DC-08/09)

### source_processor

- **Type:** Worker (subagent, fan-out)
- **Consumes:** one source (one instance per source, run in parallel)
- **Produces:** that source's `context_set/` slice + its manifest entries
- **Rules:** One reusable definition instantiated per source; split at the source boundary, never per file; failure-isolated (one source failing doesn't fail the batch). (FR-DC-05)

### code_map_build

- **Type:** Worker (subagent)
- **Consumes:** the cloned repo
- **Produces:** coarse `code_map.json` (`commit_sha`-keyed, cached; rebuilt only on SHA change)
- **Rules:** Map, don't copy (reference by path, never inline code); capture both dependency directions; per-file honest `coverage`; tags from the domain vocabulary. (FR-DC-10)

### merge_manifest

- **Type:** Plumbing (Python — not a generation skill)
- **Consumes:** per-source manifest entries from the fan-out
- **Produces:** `context_set/index.json` (deterministic fan-in)

---

# Layer 2 — BRD generation

Chat-driven authoring + validation → `BRD.md` (gated at G1). (BUILD_OVERVIEW §7–§8, §10)

### brd_author

- **Type:** Authoring (user-invocable, interactive)
- **Consumes:** `UI_INPUT.yaml` · `brd_profile.<domain>.yaml` · `context_set/index.json` · `code_map.json`
- **Produces:** `BRD.md` · **Delegates:** `code_impact`
- **Rules:** Generic engine (no domain content); short framing discovery then section-by-section; always-selective read; cite-or-flag; human-mediated flag loop at the code-impact section; executive summary drafted last; shared memory (never re-ask). (FR-BR-01…09)

### code_impact (code_impact_assess)

- **Type:** Worker (subagent)
- **Consumes:** `code_map.json` + the requirement/section context (reads actual code only for the flagged slice — deep mode)
- **Produces:** business-framed impact assessment + a **required Flags output** (scope_ripple / complexity / constraint / infeasible, each with severity)
- **Rules:** Emits the Flags section on **every** run (even "no flags"); recommends, never decides; never auto-applies scope changes. (FR-BR-07/08, FR-BR-12/13)

### brd_validator

- **Type:** Validator (subagent)
- **Consumes:** `BRD.md` + profile + source artifacts + the code surface
- **Produces:** completion score + section-level gap suggestions for in-chat fill-in
- **Rules:** Feeds the **G1 BRD acceptance gate**; soft-gate (informs, never auto-advances). (FR-BR-09, D4)

---

# Layer 3 — FRD generation

Functional translation + validation → `FRD.md` (gated at G2). (BUILD_OVERVIEW §2, §10)

### frd_author

- **Type:** Authoring (user-invocable, interactive)
- **Consumes:** **accepted `BRD.md` (primary)** · `frd_profile.<domain>.yaml` · `context_set/`
- **Produces:** `FRD.md`
- **Rules:** Same engine pattern as BRD; decomposes into actor flows / system behaviors / data contracts / error states / NFRs; carries the **detailed technical code impact** forward (BRD stays business-framed); every FRD topic `traces_to` a BRD anchor; inquiry mode + modify-via-chat with diff preview. (FR-FR-01…04)

### frd_validator

- **Type:** Validator (subagent)
- **Consumes:** `FRD.md` + `BRD.md`
- **Produces:** completion score + BRD→FRD traceability + testability/acceptance-criteria coverage
- **Rules:** Feeds the **G2 FRD acceptance gate**. (FR-FR-05, D4)

---

# Layer 4 — Jira epic creation

Decompose the accepted FRD into epics, validate traceability, single human gate, push via the adapter seam. **Epic-only for MVP** (stories later). (BUILD_OVERVIEW §9)

### jira_author

- **Type:** Authoring (subagent or user-invocable)
- **Consumes:** `jira_template.<domain>.yaml` · **accepted `FRD.md` (primary)** · `BRD.md` (business context)
- **Produces:** `jira_plan.json` (**no write to Jira**)
- **Rules:** Cluster the FRD into epics by functional area; map to template fields incl. JPMC controls; link each epic to its source FRD requirements. (FR-JR-01…03)

### jira_validator

- **Type:** Validator (subagent)
- **Consumes:** `jira_plan.json` + `FRD.md`
- **Produces:** bidirectional traceability + required/controls field completeness + coverage score
- **Rules:** Feeds the **single G3 push gate** (validation review + push authorization combined). (FR-JR-04/05, D4)

### jpmc_adapters

- **Type:** Adapter (push/auth seam)
- **Consumes:** approved `jira_plan.json`
- **Produces:** pushed epics + `jira_trace.json` (epic keys)
- **Rules:** The **only external mutation**; idempotent re-push (updates by key, never duplicates); all auth isolated here. (FR-JR-06, NFR-04/09)

---

# Layer 5 — Metrics

- **Type:** Derived (no skill)
- **Consumes:** `telemetry.jsonl` events (schema in REQUIREMENTS D8a-1)
- **Produces:** the MVP metric set ($/BRD, $/FRD, completion score, first-pass acceptance, docs/month, BRD→FRD cycle time, latency p95, FRD→epic coverage, epics/FRD, push success)
- **Rules:** Auto-computed by scanning telemetry; **no metric is hand-entered**. (FR-MX-01, D8)

---

# Runtime / Bootstrap

Cross-cutting environment setup for the runtime-tool seam — applied locally, not artifact generation.

### max-autonomy

- **Type:** Runtime utility (user-invocable; a contract the agent applies locally — not a generation skill)
- **Consumes:** operator's chosen mode (`maximum` / `balanced` / `safe default` / `add <command>`) + VS Code **USER** `settings.json`
- **Produces:** updated user `settings.json` (Copilot terminal auto-approval) + one backup
- **Rules:** User scope only; three presets are an exact contract; treat as JSONC + back up + validate after write + refuse a broken file; `maximum` must surface the risk statement; production allow-list is provisioned centrally (FR-XS-26).

---

*End of Skills Index. Source: `pdlc_handoff.zip` (`BUILD_OVERVIEW.md`, `brd_frd_overview.html`) + `REQUIREMENTS.md`. v1 (`PDLC_Platform_Design_Spec_v1.md`) is superseded.*
