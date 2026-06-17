# Requirements — Agentic BRD / FRD / Jira Generation Pipeline

**Project:** PDLC_App_v2 · JPMC Merchant Services · AI Automation
**Document type:** System requirements specification
**Status:** Draft v1 — derived from `BUILD_OVERVIEW.md` (architecture aligned end-to-end); resolves all ten §18 open questions.
**Owner:** V (Varun Munjal)
**Supersedes nothing; precedes:** tech spec → per-tool task lists → UI design.

---

## 0. Document control

### 0.1 Relationship to the build overview

`BUILD_OVERVIEW.md` is the authoritative architecture record. Its §1–§17 are **locked decisions**; this document does not re-open them. It does two jobs:

1. **Restate the locked architecture as testable requirements** (Part A) — each requirement carries an ID, a MoSCoW priority, and a back-reference to the overview section it formalizes.
2. **Resolve the ten §18 open questions in order** (Part B) — each resolution (`D1`…`D10`) produces a ruling, a rationale grounded in the core principles, and a concrete artifact (schema, contract, or table). Resolutions emit new requirement IDs where they tighten the system.

Where this document **refines** an example skill (e.g. dropping the standalone `topics:` field in favor of implicit topics, D1), the refinement is called out explicitly so the skill files can be updated to match.

### 0.2 Conventions

- **Requirement IDs:** `FR-<area>-NN` (functional), `NFR-NN` (non-functional), `D-N` (design decision from §18). Areas: `XS` cross-cutting/system · `DC` data & context · `BR` BRD · `FR` FRD · `JR` Jira · `MX` metrics.
- **Priority (MoSCoW):** **M** must (MVP-blocking) · **S** should · **C** could · **W** won't-for-MVP (recorded, deferred).
- **Schemas** are normative where given as YAML/JSON code blocks; field names are part of the contract.
- **"The session"** = the running Claude Code / Copilot agent session that acts as orchestrator. **"The operator"** = the human in VSCode. **"The agent"** = whichever skill-driven role is active.

### 0.3 Scope (mirrors overview §16)

**In scope (MVP):** five layers; one domain (Payment Brand Implementations); generic per-source-type ingestion; domain-adapter pre-processing; per-source parallel fan-out + deterministic merge; manifest + selective read; code clone + coarse map + coarse/deep impact + human-mediated flag loop; BRD + FRD authoring/validation; Jira **epic** creation with one human gate + adapter push; basic metrics; local VDI; agnostic build (Claude Code + Copilot via the UI switch); AI-session-driven orchestration; stage transitions via prompt files.

**Out of scope (deferred):** Jira stories; sync/freshness; change detection & downstream flagging; semantic retrieval; multi-domain breadth; **multi-system / cross-repo code impact (see C5)**; AWS + Snowflake; the Claude-only deterministic spine; auto-launch; any custom context-refresh mechanism; automated (non-human-mediated) impact re-runs.

---

# Part A — Requirements spine

## A1. Cross-cutting / system requirements

| ID | Pri | Requirement | Ref |
|----|-----|-------------|-----|
| FR-XS-01 | M | The system MUST hold a **generic core** constant and isolate variation to exactly two seams: a **domain seam** (data adapter / BRD-FRD profiles / Jira template / tag vocabulary) and a **runtime-tool seam** (instruction file / agent wrappers / prompt files / launch). No other axis of variation is permitted. | §3, §12 |
| FR-XS-02 | M | The **UI MUST collect configuration only** and emit a single canonical `UI_INPUT.yaml`. It MUST NOT perform plumbing or judgment. | §3, §5 |
| FR-XS-03 | M | The **scaffolder/bootstrap MUST be deterministic plumbing** (filesystem, subprocess, git, hydration, merge). It MUST NOT make authoring judgments. | §3, §5 |
| FR-XS-04 | M | **The AI session is the orchestrator.** It reads its instruction file and delegates to native subagents. Python scripts are *called by* agents; Python MUST NOT spin up the AI session. **All generation runs in-session via the selected tool (Claude Code or Copilot) reading skill instruction files; no direct Claude API calls in MVP** — a direct-API execution path is a deferred pivot, taken only if the in-session approach proves insufficient. | §3, §11 |
| FR-XS-05 | M | **Durable state MUST live in files** (`UI_INPUT.yaml`, `context_set/`, `index.json`, `code_map.json`, `BRD.md`, `FRD.md`, `jira_plan.json`, `jira_trace.json`). Context windows are ephemeral working memory only; no single session is required to carry the whole pipeline. | §3 |
| FR-XS-06 | M | The system MUST run an identical shared core on **either Claude Code or Copilot**, selected by a UI switch, with only the thin overlay differing. Skills, profiles, templates, Python plumbing, and artifact contracts MUST NOT be duplicated per tool. | §4 |
| FR-XS-07 | M | On Generate, the system MUST assemble `core/` + `profiles[domain]` + `templates[domain]` + `overlays/<tool>` and emit a self-contained instruction file (`CLAUDE.md` *or* `copilot-instructions.md`) from **one canonical template**. No runtime `AGENTS.md` pointer. | §4, §14 |
| FR-XS-08 | M | Each agent role MUST be a **thin tool-specific wrapper** pointing at **one shared skill**; the logic MUST NOT be copied across tools. Interactive roles (`brd_author`, `frd_author`) are `user-invocable`; workers (`source_processor`, `code_impact`, validators) are subagent-only. | §4, §11 |
| FR-XS-09 | M | **Generate-scaffold and run-workflow MUST be two steps** so the scaffold and `UI_INPUT.yaml` can be inspected before execution. | §5 |
| FR-XS-10 | M | Hydration MUST pull version-pinned content from the Bitbucket registry and record the **registry commit SHA in `UI_INPUT.yaml`** for reproducibility. | §5 |
| FR-XS-11 | M | Stage transitions at interactive boundaries MUST be defined **in the instruction file**, surfaced by the agent as the closing line of the prior stage, and **performed by the operator** (Claude `/clear`/new session; Copilot `Ctrl+N`). The agent MUST NOT self-issue them. Each overlay ships per-stage prompt files (`/start-brd`, `/start-frd`, `/start-jira`). | §4 |
| FR-XS-12 | W | No custom context-refresh mechanism is built for MVP; the system relies on each tool's auto-compaction plus operator new-thread at boundaries. | §4 |

## A2. Data & context layer (Layer 1)

| ID | Pri | Requirement | Ref |
|----|-----|-------------|-----|
| FR-DC-01 | M | The layer MUST run four stages — source configuration (UI) → generic ingestion connectors (per source-type) → domain-adapter pre-processing → serve — and **fan out per source**. | §6 |
| FR-DC-02 | M | Ingestion connectors MUST be **generic per source-type** (Confluence, SharePoint, Bitbucket) and reused across every domain; the path/URL/auth parameterizes each connector. For code, "ingest" = **git clone** the repo (by SEAL ID) into `repo/`. | §6, §10 |
| FR-DC-03 | M | Pre-processing MUST be the **domain adapter** (the swappable seam): docs → extract→summarize→classify/assess into provenance-tagged `context_set/`; code → build the coarse `code_map.json`. | §6 |
| FR-DC-04 | M | The layer MUST emit `context_set/index.json` — a manifest listing each file with **provenance tags** (source system, path/URL, ingest time, adapter, change-type) and a one-line descriptor — enabling selective read from day one. | §6 |
| FR-DC-05 | M | Fan-out MUST use **one reusable `source_processor` agent definition**, instantiated once per source in parallel; each owns one source end-to-end and writes its slice + manifest entries; a deterministic **`merge_manifest.py`** assembles `index.json`. Split at the source/source-type boundary, never per file. | §6 |
| FR-DC-06 | M | The MVP MUST use **large-context direct feed with selective read** — **no RAG / vector store**. The manifest is always loaded; agents pull only section-relevant files and expand on demand. | §6, §17 |
| FR-DC-07 | W | Sync/freshness, change detection & downstream flagging, and semantic (embeddings) retrieval are deferred. | §6 |

## A3. BRD generation layer (Layer 2)

| ID | Pri | Requirement | Ref |
|----|-----|-------------|-----|
| FR-BR-01 | M | BRD authoring MUST use the **generic `brd_author` skill driven by `brd_profile.<domain>.yaml`**. The skill hardcodes no domain content and is never edited at runtime; composition is `skill(profile) → BRD.md`. | §7, §8 |
| FR-BR-02 | M | Authoring MUST begin with **short framing discovery** (load `UI_INPUT.yaml` + manifest; 2–3 clarifying questions), then proceed **section by section** in a deliberate order, with the **executive summary written last**. | §8 |
| FR-BR-03 | M | Per section, the agent MUST ground in the **information hierarchy**: (1) source documents (selective-read), (2) the `UI_INPUT` requirement frame, (3) chat gap-fill limited to unsatisfied `must_capture` items. Questions are gap-fills tied to unsatisfied requirements, not 1:1 with files. | §8 |
| FR-BR-04 | M | Loading MUST be **always selective by section** — manifest always loaded, section-routed files loaded by default, more pulled on demand for cross-references. No load-all path, no size threshold. | §8, §17 |
| FR-BR-05 | M | The agent MUST support **revisiting** (later sections may revise earlier ones) and **shared memory** (never re-ask an answered question; the session + accumulating `BRD.md` carry answers; on mid-stage reset, persist facts to the draft first). | §8 |
| FR-BR-06 | M | Every substantive claim MUST be **grounded and cited inline** to a `context_set/` file, the `UI_INPUT` frame, or an explicit operator answer; ungrounded items MUST be marked `[TBD — unsourced]`, never invented. | brd skill |
| FR-BR-07 | M | At the code-impact section, the agent MUST **delegate to the `code_impact` subagent**, draft the section **business-framed** (impacted systems / scale / risk — not file/function detail), and run the **human-mediated flag loop** (see FR-BR-08). | §10 |
| FR-BR-08 | M | On returned flags the agent MUST NOT auto-apply scope changes. For each significant flag it MUST **surface** (finding/implication/options, one at a time, with a recommendation), **wait** for the operator decision, **apply** it (updating affected sections incl. earlier ones, recording decision + rationale), and **re-run `code_impact` only if scope changed materially** (see D6). | §10 |
| FR-BR-09 | M | `brd_validator` MUST cross-check section coverage against required topics, source artifacts, and the code surface, returning a **completion score + section-level gap suggestions** for in-chat fill-in. | §2, wireframe |

## A4. FRD generation layer (Layer 3)

| ID | Pri | Requirement | Ref |
|----|-----|-------------|-----|
| FR-FR-01 | M | FRD authoring MUST use the **generic `frd_author` skill driven by `frd_profile.<domain>.yaml`** (same engine pattern as BRD). | §7 |
| FR-FR-02 | M | The FRD MUST consume the **accepted `BRD.md` as primary input** and translate it into functional decomposition: actor flows, system behaviors, data contracts, error states, NFRs. | §2, wireframe |
| FR-FR-03 | M | The FRD MUST carry the **detailed technical code impact** forward from the BRD code-impact work (the BRD section stays business-framed; the FRD holds file/function detail). | §10 |
| FR-FR-04 | M | The FRD author MUST support **inquiry mode** and **modify-via-chat with diff preview**. | wireframe |
| FR-FR-05 | M | `frd_validator` MUST check **BRD→FRD traceability** and **testability / acceptance-criteria coverage**, returning a completion score + remediation suggestions. | wireframe |

## A5. Jira epic creation layer (Layer 4)

| ID | Pri | Requirement | Ref |
|----|-----|-------------|-----|
| FR-JR-01 | M | The layer MUST be **epic-only for MVP** (`jira_author` / `jira_validator`); stories are deferred to the same layer later. | §9 |
| FR-JR-02 | M | Inputs MUST be `jira_template.<domain>.yaml` (epic schema, controls fields, labels) + accepted `FRD.md` (primary) + `BRD.md` (business context only). | §9 |
| FR-JR-03 | M | `jira_author` MUST cluster the FRD into epics by functional area, map each to template fields, link each epic to its source FRD requirements, and draft a reviewable **`jira_plan.json`** — **no write to Jira**. | §9 |
| FR-JR-04 | M | `jira_validator` MUST check **bidirectional traceability** (every FRD area covered by an epic; every epic traces to the FRD) + **required/controls field completeness**, returning a coverage score + gap list. | §9 |
| FR-JR-05 | M | A **single human gate** MUST combine validation review and push authorization into one sign-off; no epics are created without it. | §9 |
| FR-JR-06 | M | Push MUST go **via the `jpmc_adapters` seam** and write epic keys to `jira_trace.json` for **idempotent re-runs**. | §9 |

## A6. Metrics layer (Layer 5)

| ID | Pri | Requirement | Ref |
|----|-----|-------------|-----|
| FR-MX-01 | M | Metrics MUST be **auto-computed from pipeline telemetry** (`telemetry.emit()` events), not hand-entered. | §2, wireframe |
| FR-MX-02 | M | MVP MUST compute at minimum: M01 $/BRD, M02 $/FRD, M03 avg completion score at acceptance, M04 first-pass acceptance rate, M05 docs/month, M06 BRD→FRD cycle time, M07 agent latency p95, M09 FRD→epic coverage at push, M10 epics/FRD, M11 Jira push success rate. (M08 upstream-change alerts depends on deferred change-detection → **W**.) | wireframe |

---

# Part B — Resolved design questions (§18, in order)

Each resolution states the ruling, the rationale, the resulting artifact, and the requirement IDs it emits.

---

## D1 — `must_capture` / `probe_if_missing`: topic level vs section level

**Question.** Do the capture criteria and probe questions attach to a section, or to topics within a section?

**Decision.** **Topic level, canonically.** A *section* is a container; a *topic* is the unit that carries exactly one `{must_capture, probe_if_missing}` pair. The validator scores coverage per topic and the agent's probes are gap-fills tied to an unsatisfied topic. `sources` is a **section-level** routing field. The section's `topics` set is **implicit** — it is the distinct set of `requirements[].topic` values — so there is no separate `topics:` field to drift out of sync with the requirements. An atomic section (one thing to capture) is written with a single requirement whose `topic` equals the section `id`.

**Rationale.** A real section captures several distinct things (the worked example's `business_context` captures both `mandate` and `brand_rules`), each needing its own capture test and its own probe; section-level criteria would force one vague probe. Topic-level also gives the validator the per-topic coverage marks the skill already emits (`satisfied by source / frame / operator / open`). Deriving `topics` from the requirements rather than listing it twice enforces the **adapter-emits ↔ profile-topics contract** at one place.

**Resulting artifact — `brd_profile.<domain>.yaml` section schema (normative):**

```yaml
# brd_profile.<domain>.yaml
domain: payment_brand            # must equal UI_INPUT.domain
sections:
  - id: business_context         # section id; matches a baseline id to override, or new to add
    title: Business context       # optional; inherited from baseline if overriding
    position: null                # null = keep baseline order; "last" = pin last; "after:<id>" = insert
    required: true                # section-level: must be satisfied before BRD acceptance gate
    sources: [confluence, sharepoint]   # section-level routing: index.json source filter
    requirements:                 # one entry per topic (topics are implicit = these .topic values)
      - topic: mandate            # MUST be a tag in the domain's adapter vocabulary (see D5)
        must_capture: "The originating brand mandate, its ID, and the compliance deadline"
        probe_if_missing: "Which brand mandate triggers this work, and what's the deadline?"
        required: true            # topic-level: counts toward the section's required coverage
      - topic: brand_rules
        must_capture: "Brand technical/operational rules constraining the implementation"
        probe_if_missing: "Which brand rules apply — message formats, cert requirements?"
        required: false           # captured if available; not blocking
```

**Routing rule (selective read):** for a section, load `index.json` entries where `source ∈ section.sources` **and** `topic ∈ {requirements[].topic}`; expand on demand.

**Emits:** `FR-BR-10 (M)` — the profile schema above is the contract; the `brd_author` skill MUST treat `topics` as implicit from `requirements[].topic` and MUST NOT require a separate `topics:` field. *(Refinement to the example skill: drop any expectation of a standalone `topics:` field; section `sources` stays explicit.)*

---

## D2 — Baseline sections: in the skill vs `brd_baseline.yaml`

**Question.** Should the universal BRD section list live in `brd_author.skill.md`, or as a separate `brd_baseline.yaml`?

**Decision.** **Keep baseline sections inline in `brd_author.skill.md`** (and `frd_author.skill.md`) for MVP — no separate baseline YAML file. The skill already carries the nine universal sections; that stays. The **profile remains the per-domain substance carrier** — it names the section `id`s it touches and supplies each one's `topics` + `must_capture` / `probe_if_missing`, plus any net-new sections. The baseline+profile merge (skill operating-procedure step 1) is unchanged; it simply merges profile entries over the skill's inline baseline list rather than over a hydrated file.

Extracting baseline to `core/brd_baseline.yaml` (same schema as a profile's `sections:` block) is recorded as a **deferred multi-domain refinement** — see FR-BR-11(W) below.

**Rationale.** At one domain the inline list is equally effective. The only payoff of the YAML extraction — a uniform same-schema baseline+profile merge and a fully content-free skill — is multi-domain hygiene, not worth an extra file and load step now. **MVP-honest:** smallest correct thing; heavier machinery visibly parked. Baseline sections are genuinely universal structure (true for every domain), so holding them in the generic skill is not a "domain content in the engine" violation.

**Baseline (as it lives inline in the skill) + merge semantics.** The skill's baseline block carries, per section, `id` / `title` / `order` / `required` (and `position: last` for the executive summary) — but **no `topics` or `must_capture`**, since what-must-be-covered is inherently domain-specific and lives only in the profile:

```text
# inline in brd_author.skill.md — baseline block (skeleton only; no must_capture)
business_context        order 10  required          out_of_scope            order 80  required
scope_objectives        order 20  required          executive_summary       position last  required (draft LAST)
stakeholders            order 30  required
current_state           order 40
requirements            order 50  required
success_metrics         order 60
constraints_assumptions order 70
```

**Merge algorithm (deterministic, by `id`):**
1. Start from the skill's inline baseline sections (skeleton).
2. For each profile section: if `id` matches a baseline section → **deep-merge** (profile supplies that section's `sources` + `requirements`; profile may raise `required`; the engine warns if a profile tries to drop a baseline-required section). If `id` is new → **insert** at `position` (`after:<id>`) or `order`, default append before `executive_summary`.
3. `executive_summary` is pinned last and **drafted last** (FR-BR-02).
4. The merged list is the authoring plan; the skill iterates it.

> **Non-blocking note (deferred) — per-domain section exclusion.** The profile currently has *add / specialize / mark-required* but **no explicit suppress verb**, so a domain cannot drop a baseline section (e.g. Payment Brand omitting "Current state"). Resolution: add an optional `suppress: [<id>]` (or per-section `include: false`) to the profile schema so a domain can omit a baseline section cleanly. This is **deferred and not blocking MVP** — until it exists a domain simply leaves an unneeded section thinly populated. Independent of where the baseline physically lives. Tracked as FR-BR-14 (W).

**Emits:** `FR-BR-11 (W)` — extracting baseline to `core/brd_baseline.yaml` / `core/frd_baseline.yaml` (same schema as the profile `sections:` block, enabling a uniform data-on-data merge) is **deferred** to when multiple domains stress the merge. For MVP the baseline stays inline in the author skills; the profile carries per-section substance and the merge runs against the inline list. `FR-BR-14 (W)` — an optional profile `suppress: [<id>]` / `include: false` verb to let a domain drop a baseline section is **deferred**; non-blocking for MVP.

---

## D3 — FRD profile + Jira template schemas (BRD-profile treatment)

**Question.** Give the FRD profile and the Jira template the same rigor as the BRD profile.

**Decision.** The **FRD profile reuses the BRD profile schema** plus two FRD-specific fields per topic/section; the **Jira template is a structural contract** (not an authoring profile) defining the epic field schema, controls fields, label/component conventions, and FRD→epic mapping + traceability rules.

### D3a — `frd_profile.<domain>.yaml` (normative)

Same `sections → requirements{topic, must_capture, probe_if_missing}` shape as D1, with additions:
- per section: `functional_kind` ∈ `{actor_flow | system_behavior | data_contract | error_state | nfr}` — lets `frd_validator` check testability coverage by kind.
- per topic: `traces_to` — the BRD section/requirement id(s) this functional item derives from (drives the BRD→FRD traceability check, FR-FR-05).

```yaml
# frd_profile.<domain>.yaml
domain: payment_brand
sections:
  - id: routing_behavior
    functional_kind: system_behavior
    sources: [bitbucket, confluence]
    requirements:
      - topic: routing
        traces_to: [scope_objectives, requirements.routing]   # BRD anchors
        must_capture: "Per-brand routing behavior: inputs, decision logic, outputs, idempotency"
        probe_if_missing: "How is a transaction routed to a brand handler today, and what changes?"
        required: true
  - id: error_handling
    functional_kind: error_state
    sources: [bitbucket]
    requirements:
      - topic: error_handling
        traces_to: [requirements.error_handling]
        must_capture: "Failure modes, error codes, retry/fallback, observable signals"
        probe_if_missing: "What are the failure paths and the expected recovery behavior?"
        required: true
```

FRD baseline sections stay **inline in `frd_author.skill.md`** (same MVP decision as D2): `actor_flows`, `system_behaviors`, `data_contracts`, `error_states`, `nfrs`, plus `traceability` (the BRD→FRD map) and `executive_summary` (last). The profile supplies each section's substance; extraction to `core/frd_baseline.yaml` is deferred with the BRD baseline (FR-BR-11 W).

### D3b — `jira_template.<domain>.yaml` (normative)

```yaml
# jira_template.<domain>.yaml
domain: payment_brand
epic:
  required_fields:
    - { key: summary,     type: string,  source: derived }     # from functional area
    - { key: description, type: markdown, source: derived }    # grounded in FRD reqs
    - { key: project_key, type: string,  source: ui_input }    # operator-supplied
    - { key: issue_type,  type: enum,     value: Epic }
  controls_fields:                                             # JPMC controls — required at push
    - { key: seal_id,            type: string,  required: true,  source: ui_input }
    - { key: risk_classification,type: enum,    required: true,  values: [low, medium, high] }
    - { key: control_owner,      type: string,  required: true,  source: ui_input }
    - { key: change_record_ref,  type: string,  required: false }
  labels:
    fixed:   [agentic-pdlc, payment-brand]
    derived: [functional_area]                                 # one label per FRD area
  components:
    map_from: code_map.module                                  # affected modules → Jira components
  traceability:
    epic_must_link: frd_requirement_ids                        # every epic → ≥1 FRD requirement
    coverage_rule: every_frd_area_has_epic                     # every FRD area → ≥1 epic
mapping:
  cluster_by: functional_area        # author groups FRD reqs into epics by area
  one_epic_per: functional_area      # MVP: 1:1 area→epic unless area is oversized
```

**Rationale.** FRD authoring varies by domain the same way BRD does → same engine + profile. Jira does **not** have section-by-section authoring variation; it has a **field/traceability contract** the author conforms to and the validator scores against → a template, not a profile. `traces_to` (FRD) and `epic_must_link` (Jira) make traceability machine-checkable end to end: BRD req → FRD topic → epic.

**Emits:** `FR-FR-06 (M)` FRD profile schema above is the contract; `traces_to` is mandatory on every FRD topic. `FR-JR-07 (M)` the Jira template schema above is the contract; `jira_validator` scores field completeness + bidirectional traceability against it.

---

## D4 — Gate inventory

**Question.** Enumerate the gates: BRD acceptance, FRD acceptance, Jira push.

**Decision.** Six control points. Three are **human acceptance gates** (G1–G3), one is a **scaffold inspection checkpoint** (G0), and the per-flag operator decision is a **sub-gate inside BRD authoring** (GF). Validator passes are **machine soft-gates** that feed the human gate's decision but do not themselves block.

| ID | Type | Stage / boundary | Precondition | Action | Output / side-effect | Performed by | Reversible |
|----|------|------------------|--------------|--------|----------------------|--------------|-----------|
| **G0** | Checkpoint | After Generate-scaffold, before Run | Scaffold laid + `UI_INPUT.yaml` written | Operator inspects scaffold + config | Proceed to run, or regenerate | Operator | Yes (regenerate) |
| **GF** | Sub-gate (loop) | Inside BRD code-impact section | `code_impact` returned ≥1 flag | Operator decides each flag (surfaced one at a time w/ recommendation) | Sections updated; decision + rationale recorded; conditional `code_impact` re-run (D6) | Operator | Yes (revise) |
| **G1** | Human acceptance | End of BRD layer | `brd_validator` score ≥ threshold **and** all `required` topics satisfied or explicitly waived **and** all flags resolved/recorded | Operator accepts BRD | `BRD.md` locked as **BRD vN**; downstream may begin | Operator | Re-open → vN+1 |
| **G2** | Human acceptance | End of FRD layer | `frd_validator` passes: every BRD requirement traced or marked out-of-scope; testability coverage met | Operator accepts FRD | `FRD.md` locked (pinned to BRD vN) | Operator | Re-open → re-validate |
| **G3** | Human (combined) | Before Jira push | `jira_validator` bidirectional traceability + field/controls completeness; coverage ≥ threshold | Operator accepts coverage **and** authorizes push in one sign-off | Epics pushed via `jpmc_adapters`; keys → `jira_trace.json` | Reviewer | Idempotent re-push (no dup) |

Notes:
- **G1 is the backstop for any missed flag** (§10): acceptance cannot pass with unresolved flags.
- **Validator soft-gates** (`brd_validator`, `frd_validator`, `jira_validator`) run before G1/G2/G3 respectively, returning the score + gap list the human gate consults; they never auto-advance.
- Gate thresholds (the numeric score bars for G1/G2/G3) are **configurable** and default to a single project-level value; the concrete default is set in the tech spec.

**Emits:** `FR-XS-13 (M)` the six control points above are the complete gate inventory; G1/G2/G3 are operator sign-offs (the agent surfaces, never self-advances). `FR-XS-14 (M)` G1/G2 produce versioned locks (BRD vN; FRD pinned to BRD vN); re-opening increments the version.

---

## D5 — First domain + concrete tag vocabulary

**Question.** Pick the first domain and define its concrete tag vocabulary — the adapter-emits ↔ profile-topics ↔ code_map-tags contract.

**Decision.** First domain = **Payment Brand Implementations** (overview §16 recommendation). Its **canonical tag vocabulary** is the single source of truth: every `requirements[].topic` in `brd_profile.payment_brand.yaml` and `frd_profile.payment_brand.yaml`, and every `tags[]` value the domain adapter and `code_map.json` emit for code sections, **MUST** be drawn from this set. The contract is enforced as a build check (D9 parity tooling).

**Resulting artifact — Payment Brand tag vocabulary (normative for the first domain):**

| Tag | Definition | Emitted by (adapter skill) | Consumed by | Code tag? |
|-----|------------|----------------------------|-------------|-----------|
| `mandate` | The originating brand mandate, its ID and compliance deadline | `change_type_assess`, `article_summarize` | BRD business_context | no |
| `brand_rules` | Brand technical/operational rules constraining implementation | `article_summarize` | BRD business_context, FRD system_behavior | no |
| `card_brand` | Which card brand(s) the work concerns | `change_type_assess` | BRD scope, code routing | yes |
| `routing` | Transaction routing to brand handlers | `change_type_assess`, `code_map_build` | BRD/FRD routing_behavior | yes |
| `message_format` | Message/wire formats and field-level changes | `article_summarize` | FRD data_contracts | yes |
| `certification` | Brand certification / conformance requirements | `change_type_assess` | BRD requirements, FRD nfrs | no |
| `settlement` | Settlement / reconciliation behavior | `code_map_build` | BRD change-impact, FRD system_behavior | yes |
| `transaction_flow` | End-to-end transaction lifecycle steps | `article_summarize`, `code_map_build` | FRD actor_flows | yes |
| `error_handling` | Failure modes, error codes, retry/fallback | `code_map_build` | FRD error_states | yes |
| `interchange_fees` | Interchange / fee schedule impacts | `article_summarize` | BRD requirements | no |
| `reporting` | Reporting / downstream data obligations | `article_summarize` | BRD success_metrics, FRD data_contracts | no |
| `compliance_deadline` | The hard date(s) the work must meet | `change_type_assess` | BRD constraints_assumptions | no |

**Contract invariant (machine-checked):**
- `topics(brd_profile) ∪ topics(frd_profile) ⊆ vocabulary` — every profile topic is a known tag.
- `tags(code_map) ⊆ vocabulary` — code-map tags reuse the same vocabulary (so code sections route correctly).
- The domain adapter's emit set **covers** every `required: true` topic — a required topic with no producing adapter is a build error.

**Rationale.** Selective read works only if the tag a section routes on is the tag the adapter actually stamped on files (§7 "a profile's topics must match the tags the domain adapter emits"). One published vocabulary per domain, checked at build, makes the contract enforceable rather than aspirational.

**Emits:** `FR-DC-08 (M)` each domain MUST publish a canonical tag vocabulary in `core/profiles/`; the adapter, BRD/FRD profiles, and `code_map.json` MUST draw tags only from it. `FR-DC-09 (M)` the build MUST fail if a profile topic is absent from the vocabulary or a required topic has no producing adapter.

---

## D6 — `code_map.json` schema + Flags schema (+ "material" threshold)

**Question.** Pin the `code_map.json` schema and the Flags schema, including types, fields, and the threshold for a "material" scope change.

### D6a — `code_map.json` (normative)

```json
{
  "repo": "merchant-routing-svc",
  "seal_id": "SEAL-12345",
  "commit_sha": "9f3c1ab",
  "generated_at": "2026-06-15T14:02:00Z",
  "coverage": "coarse",
  "components": [
    { "module": "routing", "purpose": "Routes a transaction to the correct card-brand handler" }
  ],
  "files": [
    {
      "path": "src/routing/brand_router.java",
      "module": "routing",
      "purpose": "Routes a transaction to the correct card-brand handler",
      "interfaces": ["routeTransaction(txn)", "registerBrand(brand)"],
      "depends_on": ["settlement/reconciler", "config/brand_rules"],
      "used_by": ["api/transaction_controller"],
      "tags": ["routing", "card_brand"],
      "coverage": "coarse"
    }
  ]
}
```

Rules (from `code_map_build.skill.md`, now contractual): map don't copy (reference by `path`, never inline code bodies); capture **both** dependency directions (`depends_on` + `used_by`) for closure; `tags` MUST be from the domain vocabulary (D5); per-file `coverage ∈ {coarse, deep}` flags honesty so deep impact knows where to drill; top-level `coverage` summarizes the map; `commit_sha` makes the cache key (rebuild only on SHA change).

### D6b — Flags schema (normative)

```yaml
flags:
  - type: scope_ripple            # scope_ripple | complexity | constraint | infeasible
    area: settlement/reconciler   # module/component the finding concerns
    finding: "Brand routing is shared with settlement reconciliation"
    implication: "Adding a brand also changes settlement, not just routing"
    options: [include in scope, phase separately, adjust requirement, accept risk]
    recommended_option: "include in scope"   # code_impact recommends; never decides
    severity: material                        # material | advisory  (see threshold below)
    requirement_ref: requirements.routing     # the BRD/FRD requirement whose assumption diverged
```

The **Flags section is required on every `code_impact` run** (emit "no flags" when none) so deviations are actively checked, not noticed by chance.

### D6c — "Material" scope-change threshold (the re-run trigger)

A flag's resolution is **material** — triggering section revision **and** a conditional `code_impact` re-run — when the operator's decision does **any** of:
1. **Changes the impacted code surface** — adds or removes a module/component from the in-scope set, *or*
2. **Changes a requirement's `must_capture`** that the deep pass depended on, *or*
3. **Moves a boundary** in the Scope / Out-of-scope sections.

Otherwise the flag is **advisory**: recorded with its decision, sections updated if needed, **no re-run**.

`code_impact` proposes `severity`; the **operator's decision confirms it** (a flag proposed `advisory` becomes `material` if the operator's chosen option crosses one of the three lines above). **Re-run scope is narrowed:** re-run only over the *changed* code surface (the added/removed modules), not the whole map — consistent with "deep mode reads only the flagged slice."

**Emits:** `FR-DC-10 (M)` `code_map.json` conforms to D6a; `coverage` and `commit_sha` are mandatory; the map is cached and rebuilt only on `commit_sha` change. `FR-BR-12 (M)` `code_impact` MUST emit the Flags section every run per D6b. `FR-BR-13 (M)` the material-flag threshold (D6c) governs whether `brd_author` re-runs `code_impact`; re-runs are scoped to the changed surface only. `FR-DC-13 (M)` code impact in MVP is **single-repo** — one repo cloned by SEAL ID, one `code_map.json`, within-repo dependency closure only. Multi-system discovery and federated cross-repo impact are **deferred** (see C5). The `code_map.json` schema MAY reserve (unpopulated) boundary-integration fields (`external_calls` / `exposes`) so the later cross-repo extension is additive, not a reshape.

**Deterministic extractor + onboarding gate (code_map).** *Terms used below: an **extractor** is the per-language deterministic utility that pulls structure + dependency edges from code (e.g. ctags/cscope for C); **onboarding** is the one-time, human-gated step that authors or refines an extractor against real code; **freeze** = commit it as a fixed, version-controlled artifact; the **onboarding manifest** records which extractors are frozen (per language) and the content hash each map was built against.*

`FR-DC-14 (M)` The structural extractor is a **frozen, version-controlled artifact**. The model MAY author or refine it **only via a human-gated onboarding step** that emits a reviewable artifact for a human to freeze and commit; it MUST NOT be generated, modified, or self-refined at map-build runtime. *Why: the extractor is the reproducibility/audit anchor of the code map — a runtime-mutable or model-rewritten extractor would let the same repo yield different maps across runs, which is unacceptable for a traceable BRD input.*

`FR-DC-15 (M)` Map-build MUST be **gated by deterministic checks only** — extractor presence (per language) + repo content hash — with **no model involvement in the gate decision**. Branches: no frozen extractor → onboarding; content hash unchanged → reuse cached `code_map.json`; content changed → rebuild changed files only, extractor stays frozen. *Why: keeps the steady-state decision reproducible and model-free.*

`FR-DC-16 (M)` The extractor MUST emit **coverage/failure signals**; coverage below a defined threshold MUST **flag for human re-onboarding**, never auto-modify the tool — a frozen extractor raises its hand, it does not rewrite itself. *Why: separates "code content changed" (→ rebuild map) from "a structural pattern the tool can't handle" (→ human decides whether to re-bless), so the freeze stays stable without going blind to genuinely new idioms.*

`FR-DC-17 (M)` Code-map construction is a **blend**: deterministic tooling is the **primary source of structure + dependency edges** (resolved from the language's import/include/symbol signals via a per-language extractor, selected by deterministic language detection); the model owns **`purpose` and `tags`** only and MUST NOT be the primary source of dependency edges. A **model-only fallback** is permitted for languages with no extractor, but its output MUST be marked lower-coverage. Static-analysis blind spots (function pointers, macros, config-driven wiring) are marked `coverage: coarse` and confirmed in the deep pass. *Why: deterministic tooling is more accurate and cheaper on resolvable edges, the model is required for the semantics tooling can't infer; using each where it is strong beats model-for-everything on both accuracy and cost.*

---

## D7 — Does ingestion ever vary by domain?

**Question.** Ingestion is currently generic — does any domain need to fork it?

**Decision.** **No. Ingestion connectors are keyed by source-type, never by domain.** What varies by domain is (a) *which* sources the operator configures and (b) *pre-processing* (the domain adapter, Stage 3). Per-instance differences (a specific Confluence space, a specific repo, that instance's auth) are **configuration** (`UI_INPUT.yaml` paths/URLs + `jpmc_adapters` for auth), not domain logic.

**Edge case rule.** If a future domain needs a **source type that does not yet exist** (e.g. a database source), the response is to add **one new generic connector for that source-type to `core/`** — never to specialize an existing connector for a domain. A connector that branches on `domain` is a defect.

**Rationale.** Keeps the domain seam exactly where the architecture puts it (data adapter / profiles / template / vocabulary). Generic ingestion is explicitly shared core (§6, §12). Folding domain logic into connectors would create a second, illegitimate domain seam and break the "fixed pipeline shape" principle.

**Emits:** `FR-DC-11 (M)` ingestion connectors MUST be domain-agnostic and source-type-keyed; they MUST NOT branch on `domain`. New source types are core additions (one generic connector each), not domain forks. `FR-DC-12 (M)` per-instance auth/crawl parameters are sourced from `UI_INPUT.yaml` + `jpmc_adapters`, not embedded in connector logic.

---

## D8 — Re-run / idempotency / error handling; what `UI_INPUT` + the JSONL ledger persist

**Question.** Define re-run, idempotency, and error handling beyond Jira; and the division of persisted state.

**Decision.** **Files are the durable artifact state; an append-only JSONL ledger + small per-run state/decision files are the run/telemetry record; `UI_INPUT.yaml` is the immutable run config. No SQLite for MVP** — it's deferred (see D8a). Every stage is idempotent at a defined granularity, and failures are stage-scoped with file-checkpoint resume.

### D8a — Persistence division

- **`UI_INPUT.yaml`** (file, canonical, **immutable after Generate**): working path; configured sources + URLs/paths; the requirement/project frame; `domain`; `runtime_tool`; pinned registry `commit_sha`; `run_id`. Re-configuring is a **new run** (new `run_id`, new `UI_INPUT.yaml`) — never an in-place edit.
- **Artifact state** (files): `context_set/` + `index.json`, `code_map.json`, `BRD.md`, `FRD.md`, `jira_plan.json`, `jira_trace.json`. These are the durable handoff between stages and sessions ("state lives in files").
- **Run/telemetry record (MVP) — JSONL + per-run files, not a database.** Three append-only/replaceable files, scoped per run unless noted:
  - **`telemetry.jsonl`** (append-only; the source for every Layer-5 metric) — one JSON object per line, schema in D8a-1. May be per-run or a single global file; metrics are computed by scanning.
  - **`run_state.json`** (per run; replaceable) — current stage, per-stage timestamps and status (for resume + cycle-time). Resume can also be inferred from which artifacts exist; `run_state.json` makes it explicit.
  - **`decisions.jsonl`** (per run; append-only audit) — gate decisions (G1–G3: who, when, outcome, version) and flag decisions (GF: flag, option chosen, rationale). Errors are recorded as `error` events in `telemetry.jsonl`.
  None of these store artifact content (that lives in the artifact files above).
- **SQLite — deferred, not MVP.** Adopt a queryable store only when an Insights/metrics dashboard needs interactive aggregate queries over large history, or multi-operator/high-volume concurrency arrives. The JSONL events become the rows — a clean later swap-in. For MVP, scanning JSONL is sufficient and avoids a database dependency on the VDI.

#### D8a-1 — `telemetry.jsonl` event schema (normative)

One JSON object per line. Common envelope on every event:

```json
{ "ts": "2026-06-16T14:02:00Z", "run_id": "r-2026-06-16-001", "domain": "payment_brand", "tool": "copilot", "event": "<event_type>" }
```

Event types and their payload fields (in addition to the envelope):

| `event` | Payload fields | Feeds metric(s) |
|---------|----------------|-----------------|
| `run_started` | `path`, `registry_sha` | M05 docs/month |
| `stage_started` | `stage` | M06 cycle time, M07 latency |
| `stage_completed` | `stage`, `duration_ms` | M06, M07 (p95) |
| `model_call` | `stage`, `model`, `tokens_in`, `tokens_out`, `cost_usd` | M01 $/BRD, M02 $/FRD |
| `validation` | `artifact` (brd/frd/jira), `score` | M03 completion score, M09 coverage |
| `gate_decision` | `gate` (G1/G2/G3), `outcome` (accept/reopen), `actor`, `version` | M04 first-pass acceptance |
| `flag_decision` | `flag_type`, `option`, `severity` | (audit) |
| `jira_push` | `epics`, `success` (bool), `partial` (bool) | M10 epics/FRD, M11 push success |
| `error` | `stage`, `kind`, `message` | (error log) |

Metrics (Part A6) are derived by filtering/aggregating these events; no metric is hand-entered (FR-MX-01).

### D8b — Idempotency & re-run, per stage

| Stage | Idempotency key | Re-run behavior | Failure handling |
|-------|-----------------|-----------------|------------------|
| Clone / ingest | repo `commit_sha`; source URL+ingest-time | Re-clone/pull to pinned SHA; skip if present & matching | Retry; a failed source is marked failed in the manifest, batch continues |
| Pre-process (per source) | source id | Regenerates that source's slice + manifest entries; `merge_manifest.py` reassembles `index.json` | Source-scoped; one source failing does **not** fail the fan-out; partials + gap list surfaced |
| Code map | repo `commit_sha` | Cached; rebuilt only on SHA change | Rebuild on demand; coarse coverage marked honestly |
| BRD authoring | `run_id` + section id | Resumable: re-entered session loads `UI_INPUT` + manifest + existing `BRD.md` and continues (shared-memory rule); accepted → BRD vN | Mid-stage reset persists gathered facts to the draft first (FR-BR-05); ungrounded items `[TBD — unsourced]` |
| FRD authoring | `run_id`; pinned BRD vN | Resumable like BRD; re-opening BRD → FRD re-validates against new vN | Traceability gaps surfaced by `frd_validator`, not silently dropped |
| Jira push | `jira_trace.json` epic keys | Re-push **updates** existing epics by key — never duplicates | Partial push recorded in `jira_trace.json`; idempotent retry of the remainder |

### D8c — Error-handling principles

1. **Stage-scoped failure + file checkpoint resume** — a failure aborts its stage, not the run; resume from the last good file state.
2. **Fan-out isolation** — a single source's failure is contained; the batch proceeds with partials and a recorded gap list; the operator chooses retry-or-proceed.
3. **No silent gaps** — agent-judgment shortfalls surface as `[TBD — unsourced]` or validator gap items, never invented content.
4. **Idempotent external writes** — Jira push is the only external mutation and is guarded by `jira_trace.json`.

**Emits:** `FR-XS-15 (M)` the run/telemetry/decision record is **append-only `telemetry.jsonl` + per-run `run_state.json` / `decisions.jsonl`** (schema in D8a-1); artifact content lives only in files; **SQLite is deferred** (adopt when a metrics dashboard or multi-operator concurrency requires it). `FR-XS-16 (M)` `UI_INPUT.yaml` is immutable post-Generate; re-config = new `run_id`. `FR-XS-17 (M)` every stage is idempotent at the granularity in D8b. `FR-XS-18 (M)` failures are stage-scoped with file-checkpoint resume; fan-out is failure-isolated; external writes are idempotent.

---

## D9 — Overlay authoring: hand-maintain vs generate from one spec

**Question.** Maintain the two tool overlays by hand, or generate both from one workflow spec?

**Decision.** **Hand-maintain the two overlays for MVP, with parity enforced by a shared checklist spec — not a generator.** Concretely:
- **Generated (one piece only):** the **instruction file** (`CLAUDE.md` / `copilot-instructions.md`) is emitted at Generate from **one canonical template** (already required, FR-XS-07).
- **Hand-authored, native, per tool:** the **agent/subagent wrapper files** and **per-stage prompt files** — kept idiomatic (frontmatter + location genuinely differ; §4 says don't abstract).
- **Parity tooling (not generation):** a `core/overlay_manifest.yaml` lists every required role (with its shared skill), every prompt file, and the launch method **per tool**. A build check asserts that each overlay implements every manifest role with a wrapper pointing at the correct shared skill, and ships every required prompt file. Author by hand; **verify by spec**.

**Resulting artifact — `core/overlay_manifest.yaml` (normative):**

```yaml
roles:
  - { name: brd_author,       skill: brd_author,       user_invocable: true }
  - { name: frd_author,       skill: frd_author,       user_invocable: true }
  - { name: brd_validator,    skill: brd_validator,    user_invocable: false }
  - { name: frd_validator,    skill: frd_validator,    user_invocable: false }
  - { name: jira_author,      skill: jira_author,      user_invocable: false }
  - { name: jira_validator,   skill: jira_validator,   user_invocable: false }
  - { name: source_processor, skill: source_processor, user_invocable: false }
  - { name: code_impact,      skill: code_impact,      user_invocable: false }
prompt_files: [start-brd, start-frd, start-jira]
overlays:
  claude:  { instruction_file: CLAUDE.md,                 agents_dir: .claude/agents/, launch: terminal_interactive }
  copilot: { instruction_file: copilot-instructions.md,   agents_glob: "*.agent.md",   launch: agent_mode }
parity_check: every_role_and_prompt_present_in_both_overlays
```

**Rationale.** Only two overlays, both thin; a generator would be machinery for little gain and risks a leaky abstraction over genuinely-divergent native syntax — violating **MVP-honest** and §4's "keep each native, don't abstract." The manifest gives the safety of a single source of truth (no role silently missing from one tool) without the cost of generation. Generating the wrappers once the role set stabilizes is a **deferred** option.

**Emits:** `FR-XS-19 (M)` overlay wrappers + prompt files are hand-authored per tool; the instruction file is generated from one template. `FR-XS-20 (M)` `core/overlay_manifest.yaml` is the parity source of truth; the build MUST fail if either overlay omits a listed role or prompt file. `FR-XS-21 (W)` generating wrappers from the manifest is deferred.

---

## D10 — Auto-launch vs manual start; the Copilot/VDI validation task

**Question.** Per tool/environment, auto-launch or manual start? And the Copilot agent-mode + command-execution policy check in the VDI.

**Decision.** **Manual start for both tools in MVP** (auto-launch deferred, §16). Generate lays the scaffold and opens VSCode where allowed; the operator starts the session — interactive Claude Code in the terminal, or Copilot agent mode — manually, using the per-stage prompt files. The UI **MUST surface the exact start gesture per tool** at hand-off.

**Claude Code and Copilot are co-equal MVP paths.** Both run the same instruction-file-driven orchestration (`CLAUDE.md` / `copilot-instructions.md`) delegating to **internal subagents**; neither uses headless mode on the shared path (headless `claude -p` is only the optional, deferred, Claude-only spine — §4, §16). The single genuine tool asymmetry is **Python-drivability** (Claude Code can be launched/driven locally; Copilot cannot), and that asymmetry maps entirely onto features already deferred from MVP — **auto-launch** and the **Claude-only spine**. For the MVP's manual-start, interactive, internal-subagent path the two tools do the same job, so neither is second-class.

**The Copilot/VDI check is an early validation task, not a feasibility gate.** Executing a script from a Copilot agent is a supported capability; the only environment-dependent residue is whether the VDI's **command-approval policy** lets the agent invoke the plumbing scripts (clone/ingest/hydrate/merge) without per-command approval stalling the loop, plus a couple of agent-mode behaviors. Concretely, VS Code Copilot agent mode controls this via a terminal **allow/deny list** (`github.copilot.chat.agent.terminal.allowList` / `denyList`) or a blanket auto-approve (`chat.tools.terminal.autoApprove`) — set in **user** `settings.json` (validation found workspace `.vscode/settings.json` scope unreliable for these keys; see result). The task confirms these are settable (not locked by managed VDI policy) and that an allow-list lets a multi-step loop run cleanly. A hiccup means **tune the allow-list**, not "drop Copilot from MVP." The task is run **early** to de-risk approval friction before the overlay work depends on it.

**Validation-task scope (see companion `COPILOT_VDI_VALIDATION.md`):**
1. Copilot **agent mode** available/enabled in the target VDI; note selectable models.
2. **Custom agents/subagents** (`*.agent.md`) load and are invocable (user-invocable role + subagent-only worker).
3. **Command-approval policy** — agent can run the plumbing scripts; allow-list (`…agent.terminal.allowList`) is settable and lets a multi-step loop proceed without per-command stalls; deny-list reserved for destructive commands.
4. **Parallel fan-out** via coordinator-instruction phrasing actually parallelizes (or runs as isolated collapsible tool calls), not silent serialization.
5. **Stage transition** via `Ctrl+N` + a prompt file (`/start-frd`) yields a clean fresh context that re-orients from `UI_INPUT.yaml` + the prior artifact.

**Validation result (2026-06-16) — PASSED.** Run in the target VDI. Command execution confirmed (a multi-command sequence ran to completion); **parallel fan-out ran with genuine concurrency** (two workers concurrently), exceeding the "isolated tool calls" bar; custom subagents loaded. Critically, **user-scope** auto-approval settings took effect — so the org's Copilot policy does **not** force manual approval, the one scenario that could have hard-blocked the Copilot path. One scoping detail learned: **workspace** `.vscode/settings.json` did **not** take effect for these keys, while **user-scope** settings did — which fixes the allow-list's home as user scope, not the scaffold (FR-XS-26). Remaining check 5 (fresh-context re-orientation) is low priority; persistence is moot under user-scope settings.

**Rationale.** Once orchestration is instruction-driven (not scripted), the MVP path uses internal subagents on both tools (no headless), and Copilot can execute scripts, the basis for ranking Claude above Copilot in MVP largely disappears. What remains is a concrete, fixable environment question — the VDI command-approval policy — which is a validation/config item, not an existential risk. **MVP-honest:** validate the one uncertain thing early; don't pre-emptively demote a co-equal path on an assumption.

**Emits:** `FR-XS-22 (M)` MVP supports **manual start** for both tools; the UI MUST surface the exact per-tool start gesture. `FR-XS-23 (M)` Claude Code and Copilot are **co-equal MVP paths** (instruction-driven orchestration + internal subagents; no headless on the shared path). `FR-XS-24 (M)` the Copilot/VDI command-approval policy was validated early via `COPILOT_VDI_VALIDATION.md` — **PASSED 2026-06-16** (command execution + concurrent fan-out confirmed; org policy not locking approval); a failure would have been resolved by allow-list tuning, and only a confirmed hard block demotes Copilot. `FR-XS-25 (W)` auto-launch (Claude-only first) and the Claude-only deterministic spine are deferred. `FR-XS-26 (M)` the Copilot terminal allow-list lives in **user-scope** settings, not the workspace/scaffold (workspace scope proved unreliable for these keys); in production it MUST be **provisioned centrally** (MDM / managed VS Code profile / VDI bootstrap) and **surfaced by Generate/onboarding as a VDI prerequisite** — the scaffolder does NOT emit it. The `max-autonomy` skill provides local/dev toggling of the same user-scope keys (`maximum` / `balanced` / `safe default` / add-one-command).

---

# Part C — Non-functional requirements, acceptance & traceability

## C1. Non-functional requirements

| ID | Pri | Requirement | Ref |
|----|-----|-------------|-----|
| NFR-01 | M | **Reproducibility** — a run MUST be reconstructable from `UI_INPUT.yaml` alone (pinned registry SHA + repo SHA + frame + config). | §5, D8 |
| NFR-02 | M | **Portability** — the codebase MUST remain runnable on both tools by changing only the overlay; no tool-specific logic leaks into the shared core. | §4, D9 |
| NFR-03 | M | **Auditability** — every substantive BRD/FRD claim is provenance-cited; every gate and flag decision is recorded (who/when/outcome/rationale) in the per-run decision log (`decisions.jsonl`). | §6, D4, D8 |
| NFR-04 | M | **JPMC environment fit** — runs on local VDI; models via JPMC Bedrock (`CLAUDE_CODE_USE_BEDROCK`); all external integration (auth, Jira write) is isolated to the `jpmc_adapters` seam. | §15 |
| NFR-05 | M | **Selective-read scalability** — authoring MUST stay within context budget at any corpus size via manifest + on-demand expansion (no load-all path, no size threshold). | §8, §17 |
| NFR-06 | S | **Observability** — `telemetry.emit()` events MUST be sufficient to compute all MVP metrics (Part A6) without manual instrumentation. | §2 |
| NFR-07 | M | **Determinism of plumbing** — scaffolding, hydration, fan-in merge, and idempotency keys MUST be deterministic; only authoring/assessment is model-driven. | §3 |
| NFR-08 | S | **Resumability** — an interrupted run MUST resume from last good file state without redoing completed stages (D8b). | D8 |
| NFR-09 | M | **Security of external writes** — the only external mutation is the Jira epic push, gated by G3 and guarded for idempotency by `jira_trace.json`. | §9, D4 |

## C2. Per-layer acceptance criteria

- **Data & context:** every configured source produces a `context_set/` slice + manifest entries; `index.json` merges deterministically; failed sources are marked, not silent; for code-bearing domains `code_map.json` exists with `commit_sha` + honest `coverage`. (FR-DC-01…11, FR-DC-08/09)
- **BRD:** all `required` topics satisfied or explicitly waived; every claim grounded/cited or `[TBD]`; all flags resolved/recorded; `brd_validator` score ≥ threshold; **G1** sign-off → BRD vN locked. (FR-BR-*, D4)
- **FRD:** every BRD requirement traced or marked out-of-scope; testability/acceptance-criteria coverage met by `functional_kind`; **G2** sign-off → FRD pinned to BRD vN. (FR-FR-*, D3a, D4)
- **Jira:** `jira_plan.json` drafted (no write); bidirectional traceability + required/controls field completeness pass; **G3** single sign-off → push via `jpmc_adapters`; keys in `jira_trace.json`. (FR-JR-*, D3b, D4)
- **Metrics:** MVP metric set computes from telemetry with no manual entry. (FR-MX-*)

## C3. Contract traceability (the spine that must hold end to end)

```
domain tag vocabulary (D5)
      │  every topic ⊆ vocabulary; every required topic has a producing adapter
      ▼
brd_profile.topic ──► BRD section (must_capture)
      │  traces_to
      ▼
frd_profile.topic ──► FRD section (functional_kind, testable)
      │  epic_must_link
      ▼
jira_plan epic ──► FRD requirement ids ──► (push) jira_trace.json
```
Each arrow is **machine-checkable**: the build verifies vocabulary containment (D5); `frd_validator` verifies BRD→FRD `traces_to`; `jira_validator` verifies FRD↔epic bidirectional links. A break anywhere fails the corresponding gate.

## C4. §18 resolution → requirement map

| §18 Q | Decision | Key emitted requirements |
|-------|----------|--------------------------|
| 1 | Topic-level capture; `topics` implicit; `sources` section-level | FR-BR-10 |
| 2 | Baseline stays **inline** in author skills for MVP; profile carries per-section substance; YAML extraction deferred | FR-BR-11 (W) |
| 3 | FRD profile = BRD schema + `traces_to`/`functional_kind`; Jira = structural template | FR-FR-06, FR-JR-07 |
| 4 | Six control points (G0, GF, G1–G3); validators are soft-gates | FR-XS-13, FR-XS-14 |
| 5 | First domain Payment Brand; published tag vocabulary as contract | FR-DC-08, FR-DC-09 |
| 6 | `code_map.json` + Flags schemas; material = surface/requirement/boundary change | FR-DC-10, FR-BR-12, FR-BR-13 |
| 7 | Ingestion never varies by domain; new source types = core connectors | FR-DC-11, FR-DC-12 |
| 8 | Files = artifacts; append-only JSONL ledger + per-run state/decision files (**SQLite deferred**); `UI_INPUT` immutable; per-stage idempotency | FR-XS-15…18 |
| 9 | Hand-author overlays; parity via `overlay_manifest.yaml`; instruction file generated | FR-XS-19…21 |
| 10 | Manual start MVP; Claude Code + Copilot **co-equal**; Copilot/VDI command-approval **validated — PASSED**; allow-list home = user-scope, centrally provisioned | FR-XS-22…26 |

## C5. Handed forward to the tech spec (explicitly not decided here)

- Concrete **gate score thresholds** (G1/G2/G3 numeric bars) and the validator scoring formulas.
- The **`jpmc_adapters` interface** signature for the Jira write (and Bedrock wrapper specifics).
- **Registry hydration** mechanics (clone vs sparse fetch; SHA-pinning implementation).
- The **`telemetry.jsonl` event schema is defined here** (D8a-1), not handed forward. A SQLite schema/DDL is **deferred** — not a tech-spec item for MVP; revisit only if a queryable metrics store is later adopted.
- A **direct Claude API execution path** is **deferred** — MVP generation runs entirely in-session (Claude Code / Copilot); pivot to API only if the in-session approach proves insufficient (FR-XS-04).
- **Telemetry event schema** backing the Part A6 metrics.
- The **Copilot/VDI validation task** is **PASSED** (D10, runbook `COPILOT_VDI_VALIDATION.md`) — not an open question. Production allow-list provisioning (central/MDM) is an onboarding/ops task, not a design decision.
- **Multi-system / cross-repo code impact — deferred (FR-DC-13).** MVP is single-repo. The deferred design reuses the existing patterns one tier up ("fractal"): a **system tier** that discovers impacted repos by matching the requirement against a cached corpus of **coarse code_maps** (coarse-map-as-discovery), backed by a *thin* repo inventory (enumeration + ownership + LOB filter) and an architecture-metadata cross-check for config-driven edges; then the existing **code tier** within each impacted repo. Cross-repo analysis happens **only at integration seams** — match a producer's outbound call site to the consumer's inbound handler, check whether the contract changes, raise contract-break flags, and descend into the consumer only if the contract breaks (never an N×N all-function trace). Staged adoption: (1) single-repo [MVP] → (2) explicit multi-repo (operator names the repos; stitch at contracts) → (3) registry-filtered coarse-map discovery. Forward-compat hook: reserve `external_calls`/`exposes` in `code_map.json` now (FR-DC-13).
- **Code-map extractor + onboarding gate — mechanics handed to tech spec (FR-DC-14…17).** *Decided:* adapt-at-onboarding-then-**freeze** (the model proposes/refines an extractor against real code, a human freezes & commits it, it runs deterministically thereafter) — **not** runtime self-refinement, because a self-modifying extractor breaks map reproducibility. *Decided:* a content change **rebuilds the map** while the extractor **stays frozen**; only a structural pattern the extractor cannot handle **flags for human re-onboarding** — keeping these two cases separate avoids re-onboarding on every commit yet doesn't go blind to genuinely new idioms. *Decided:* a **blend** (deterministic tooling for edges, model for `purpose`/`tags`) over model-for-everything, because tooling is more accurate/cheaper on resolvable edges and the model is needed for semantics. **Tech spec to define:** the **onboarding-manifest schema** (frozen extractors per language + per-repo content hashes); the **3-branch gate algorithm** (FR-DC-15); the **coverage threshold** that triggers re-onboarding (FR-DC-16); the **dispatcher + per-language extractor normalization contract** (detect language → route to extractor → normalize output to the `code_map` schema → model-only fallback when no extractor exists); and the **external-build → VDI-port** handling (the frozen extractor is plumbing that ports unchanged; verify `ctags`/`cscope`/language tools exist or are provisioned on the VDI; the model-only fallback covers their absence).

---

*End of requirements. Next: tech spec → per-tool task lists → UI design.*
