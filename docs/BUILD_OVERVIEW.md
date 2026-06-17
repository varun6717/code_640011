# Build Overview — Agentic BRD / FRD / Jira Generation Pipeline

**Project:** Agent_OrchX_PDLC · JPMC Merchant Services · AI Automation
**Status:** Architecture aligned end-to-end (UI → agents → orchestration → code impact → tool-agnostic build). Ready for detailed design → requirements document.
**Purpose:** Hand-off seed for a new chat. Captures *everything* decided in the originating design
conversation so the next chat can produce the requirements document without re-deriving anything.

**Companion artifacts (in this package):**
- `brd_frd_overview.html` — the visual architecture wireframe (5 layers). Authoritative picture.
- `brd_author.skill.md` — example skill: the generic engine + domain-profile pattern, with the
  loading strategy and the impact-flag handling rule.
- `code_map_build.skill.md` — example skill: Phase A, builds the coarse code map.
- `code_impact_assess.skill.md` — example skill: Phase B deep impact, with the required Flags contract.

---

## 1. What we are building

An agentic pipeline that turns enterprise product context into a validated **BRD**, a validated
**FRD**, and controls-tracked **Jira epics** — driven from a small config UI, executed by an AI
coding agent (**Claude Code or GitHub Copilot**) running locally in VSCode. Two seams keep it clean:
- **Generic core + thin domain seam** — generic machinery is constant; per-domain variation is isolated.
- **Generic core + thin runtime-tool seam** — the same build runs on Claude Code or Copilot; only a thin overlay differs.

### Operator journey (end to end)
1. **UI** — operator enters the working PATH, input pipelines + URLs/paths, the **requirement/project frame**, the **domain**, and the **runtime tool** (Claude Code or Copilot).
2. **Generate** — backend creates the dir, writes `UI_INPUT.yaml`, lays the shared core, and lays the chosen tool's overlay.
3. **VSCode** — operator starts the agent session (interactive Claude Code in the terminal, or Copilot agent mode).
4. **Bootstrap** — hydrates the scaffold from the Bitbucket registry (shared skills + the domain's adapter/profile/template), version-pinned.
5. **Run** — Data Processing (parallel per-source) → BRD → FRD → Jira epics, with human gates and stage transitions.
6. **Outputs** — `context_set/` + `index.json`, `code_map.json`, `BRD.md`, `FRD.md`, a reviewed `jira_plan.json`, and (on approval) epics pushed to Jira.

---

## 2. Architecture — the five layers

(See `brd_frd_overview.html`.)

1. **Data & context layer** — configure → ingest → pre-process (domain adapter) → `context_set/` + `index.json`. Processing fans out per source.
2. **BRD generation layer** — chat-driven authoring + validation → `BRD.md` (gated).
3. **FRD generation layer** — functional translation + validation → `FRD.md` (gated).
4. **Jira epic creation layer** — decompose the accepted FRD into epics, validate traceability, single human gate, push via the JPMC adapter seam.
5. **Metrics layer** — auto-computed from pipeline telemetry.

---

## 3. Core principles

- **Generic core + thin seams** — fixed pipeline shape; variation isolated to a **domain seam** and a **runtime-tool seam**.
- **Three responsibilities, kept separate:** UI = config collection only (→ `UI_INPUT.yaml`); scaffolder/bootstrap = deterministic plumbing; agents = judgment only.
- **The AI session is the orchestrator; Python is called-plumbing.** The running agent session reads its instruction file and delegates to subagents; Python scripts (ingest, clone, hydrate, merge) are *called by* the agents. Python never spins up the AI (Copilot can't be Python-driven in the target env).
- **Plumbing out of the model** — one correct deterministic outcome → code; judgment → model.
- **State lives in files** — context windows are ephemeral working memory; `BRD.md`, `context_set/`, `code_map.json`, etc. are the durable handoff. So no single session must carry the whole pipeline.
- **MVP-honest** — smallest correct thing; heavier machinery visibly parked.

---

## 4. Runtime-tool agnosticism (Claude Code vs Copilot)

Both tools have converged: root instruction file + agent files (YAML frontmatter) + orchestrator delegating to subagents in isolated contexts. So agnosticism is well-supported.

### The seam: one shared core + two thin overlays
- **Shared core (authored once, no tool-specific syntax):** the **skills** (`SKILL.md` cross-tool format), **domain profiles/templates** (YAML), **Python plumbing**, **contracts/artifacts** (`context_set/`, `index.json`, `BRD.md`, `code_map.json`). Never duplicate these per tool.
- **Two idiomatic overlays (native per tool):** the instruction file (`CLAUDE.md` vs `copilot-instructions.md`), the agent/subagent definition files, the per-stage **prompt files**, and the launch method. These genuinely differ in syntax/location — keep each native, don't abstract.

### Agent files vs skills (the thin-wrapper rule)
The **skill** carries the substance (procedure, rules, sections) and is shared. The **agent definition file** is a thin tool-specific wrapper that points at the skill — differing only in frontmatter and location:
- Claude: `.claude/agents/brd_author.md` (frontmatter: name, description, tools, model)
- Copilot: `brd_author.agent.md` (frontmatter: name, tools, `user-invocable`, `model`, `agents:`)

Both bodies are near-identical ("You are the BRD author; follow the `brd_author` skill…"). Maintain *two small wrappers* per role over *one shared skill* — never two copies of the logic. Mark interactive roles (BRD/FRD author) `user-invocable: true`; mark workers (`source_processor`, `code_impact`) subagent-only.

### The UI switch
On Generate, the switch assembles **shared core + `profiles[domain]` + `overlays/<chosen tool>`**, emitting a self-contained `CLAUDE.md` *or* `copilot-instructions.md` from one canonical template. **No runtime `AGENTS.md` pointer** — generation keeps things consistent.

### Orchestration model (works on both)
- **The tool's own session is the orchestrator** — interactive Claude Code in the terminal, or Copilot agent mode. It reads the instruction file and delegates to native subagents.
- **Subagents are internal, not headless** — delegating spins up an isolated context window inside the session; no separate process, no "headless steps" to mark.
- **No headless on the authoring path.** Headless (`claude -p`) is one-shot, only for an optional **Claude-only** deterministic spine (not the shared path).
- **Parallel fan-out:** Claude parallel subagents; Copilot via coordinator-instruction phrasing ("run these as parallel subagents") — not the CLI's `/fleet`, which the target Copilot env lacks. Subagents appear as collapsible tool calls in the Copilot chat UI.

### Stage transitions
A fresh context at each interactive stage boundary is **needed on both tools** (context hygiene), via tool-native gestures, defined **in the instruction file** (not forked agent files):
- Claude: `/clear` (or new session) → kickoff.
- Copilot: `Ctrl+N` (new thread) → `/start-frd`.

The gesture is an **operator action** the agent *surfaces* as the closing line of the prior stage; the agent can't self-issue it. Ship a per-stage **prompt file** (`/start-brd`, `/start-frd`, `/start-jira`) in each overlay; keep it short — it just points the fresh agent at `UI_INPUT.yaml` + the prior artifact.

### Context refresh — don't build a mechanism
Both tools **auto-compact** when the window fills (Copilot: `github.copilot.chat.summarizeAgentConversationHistory.enabled`; Claude: equivalent). A hard reset is one keystroke (new thread/session) at a stage boundary where a human is already present. So **for MVP build no refresh automation** — no Copilot JS extension (its chat-session API is proposed/unstable), no scripted `/clear`. The optional Claude-only spine gets fresh context for free (each `claude -p` is a new context); that's a separate path, not the shared one.

### Models differ
Claude via Claude Code; Copilot uses its own model selection (GPT-family or Claude — Copilot can run Claude models, narrowing divergence). Keep skills model-neutral; validate on both. Keep skills shared until one demonstrably needs per-tool phrasing.

---

## 5. Bootstrap / initializer

- **UI** collects: working PATH, input pipelines + URLs/paths, the **requirement/project frame**, the **domain**, the **runtime tool**.
- **Generate** → FastAPI backend (local) creates the dir, writes `UI_INPUT.yaml` (canonical run record), lays the shared core, lays the chosen overlay.
- **Hydration (scripted):** pulls from the Bitbucket registry — shared skills, the domain's pre-processing skills + order, `brd_profile.<domain>.yaml`, `jira_template.<domain>.yaml`.
- **Version-pin the registry** — commit SHA in `UI_INPUT.yaml`, for reproducibility.
- **Generate-scaffold and run-workflow are two steps**, so the scaffold + `UI_INPUT.yaml` can be inspected first.

---

## 6. Data & context layer

Four stages; the third is the only domain-specific one. Processing **fans out per source**.

1. **Source configuration** (UI) — toggles + URLs/paths, saved as config; the path parameterizes each connector.
2. **Ingestion connectors** (generic, per source-type) — fetch/auth/crawl/download; scripts the agents call → raw artifacts. (For code, "ingest" = **git clone** the repo into the workspace — see §10.)
3. **Pre-processing — domain adapter** (swappable) — extract → summarize → classify/assess (docs); **build the coarse code map** (code). The seam each domain fills.
4. **Serve** — `context_set/` (summarized, provenance-tagged) + `index.json` manifest; `code_map.json` for code.

### Per-source fan-out
Sources are independent → **fan-out / fan-in**: one `source_processor` agent definition, instantiated **once per source in parallel**, each owning one source end-to-end and writing its slice + manifest entries; then a deterministic **`merge_manifest.py`** assembles `index.json`. Split at the **source/source-type** boundary, not per file. The ingest connector + pre-processing skills differ by source type; the agent definition is one reusable worker.

### Context handling (MVP)
- **No RAG / vector store.** Large-context direct feed.
- **Selective read, day one.** `index.json` lists each file with provenance + a one-line descriptor; agents load the manifest then pull only the section-relevant files.
- **Provenance-tagged** — source system, path/URL, ingest time, adapter, change-type → inline citations + audit.

### Deferred
Sync/freshness, change detection & downstream flagging, **semantic (embeddings) retrieval**.

---

## 7. Generation layers — the skill + profile engine

- **`<x>_author.skill.md`** = generic engine (process, boundaries, grounding, interaction, baseline sections). Hardcodes no domain content; reads the profile and iterates.
- **`<x>_profile.<domain>.yaml`** = the arguments (per-section `sources`, `topics`, per-topic `requirements`: `must_capture`, `probe_if_missing`). The "routing map" is the `sections:` block.
- **Composition is `skill(profile) → BRD.md`** — the skill file is never edited; the profile parameterizes at runtime, section by section.
- **Baseline + override merge** — baseline sections in the skill (or later `brd_baseline.yaml`); profile adds/specializes/marks-required.
- **Contract** — a profile's `topics` must match the **tags the domain adapter emits**.

`BRD.md`/`FRD.md` are Markdown deliverables; profiles are YAML config.

---

## 8. BRD authoring process

### Discovery
Runs in the **VSCode BRD agent session**, with a rhythm — not one big upfront interrogation:
1. **Framing (short discovery)** — the agent loads `UI_INPUT.yaml` + the manifest, confirms intent and scope with 2–3 clarifying questions. Just enough to seed the coarse code pass and orient the agent.
2. **Coarse code pass** (if code is a source) → flagged areas (see §10), enriching discovery.
3. **Section-by-section authoring** — the main work.

### Information hierarchy (per section's `must_capture`)
1. **Source documents** (`context_set/`, selective-read) — grounding.
2. **UI requirement frame** (`UI_INPUT.yaml`) — operator's authoritative intent; *necessary*, since sources give domain context but not "the specific requirement we're authoring now."
3. **Chat** — gap-fill: only the `must_capture` items neither sources nor frame answered. Questions are **gap-fills tied to unsatisfied requirements**, not 1:1 with files.

### Section-by-section model (decided)
For each section: ground (sources + frame + for code, impact) → draft what's possible → chat the gaps → next. With:
- **Revisiting** — later sections can surface changes to earlier ones; not a one-way pass.
- **Shared memory across sections** — an answer given once isn't re-asked (carried by the session + the incrementally-written `BRD.md`; if mid-stage reset is used, persist gathered facts in the draft).
- **Deliberate order** — context/scope before requirements; **executive summary written last**.
- **Loading strategy** — **always selective-read by section**; never bulk-load the corpus. The manifest
  is always loaded (full index in view), the `BRD.md` draft accumulates, and the agent expands on demand
  for cross-references — so cross-section awareness holds without a load-all path or any size threshold.
- Optional later enhancement: a light **holistic first pass** (skeleton across all sections) for cross-section coherence.

---

## 9. Jira epic creation layer

- **Epic-only for MVP** (stories later, same layer; skills `jira_author` / `jira_validator`).
- **Inputs** — `jira_template.<domain>.yaml` (epic schema, controls fields, labels) + accepted `FRD.md` (primary) + `BRD.md` (context).
- **Author** drafts `jira_plan.json` (no write to Jira); **validator** checks bidirectional traceability + field completeness → coverage score.
- **Single human gate** — reviewer checks validation *and* approves push in one sign-off.
- **Push** via the `jpmc_adapters` seam; writes epic keys to `jira_trace.json` for idempotent re-runs.

---

## 10. Code impact (Bitbucket)

Code is handled **differently from documents**. Documents are summarized *into* `context_set/`. Code is **cloned into the workspace** (`repo/` on disk), read natively by the agent on demand; only a lightweight `code_map.json` (index) is produced. Two phases:

### Phase A — code map (requirement-independent, built once, cached)
- **Ingest = git clone** the repo (by SEAL ID) into the workspace (plumbing).
- **The AI (Claude/Copilot) builds `code_map.json`** by exploring the repo: per module/file → purpose summary, key interfaces, **dependency edges** (deps are what make it an *impact* map, not a flat summary).
- **Coarse-first, deep-on-demand** — module-level summaries; don't read every file up front. Optional cheap deterministic scaffolding (file tree, grep imports) for very large repos.
- Output: `context_set/code_map.json` (the index over `repo/`).

### Phase B — impact (requirement-dependent)
- **Coarse impact (early):** requirement × `code_map.json` → likely-affected areas. *Reads the map only*, so it's cheap and fast. It threads **high-level code context into the early sections** and enriches discovery.
- **Deep impact (at the code-impact section):** for the flagged areas only, the **`code_impact` subagent** selective-reads the actual code from `repo/`, traces the real dependency closure, and produces the detailed assessment **plus flags**. Isolated context → returns a concise result to the BRD session.

### Where it lands in the BRD
- The code-impact BRD section is **business-framed** ("impacted systems / change impact") — affected systems, scale, risk — *not* file/function detail. The detailed technical impact carries forward to the **FRD**.
- It's **profile-defined** (present only when the domain has code) and typically **finalized late** (after scope/requirements stabilize, like the exec summary).

### The feedback loop (human-mediated)
Encoded as a structured output contract + a handling rule, so it's reliable:
- **`code_impact.skill.md`** must emit a required **Flags** section — deviations from the requirement's assumptions, typed `scope_ripple | complexity | constraint | infeasible`, each with finding/implication/options. (Detection is forced by making Flags a required output, not optional.)
- **`brd_author.skill.md`** must handle flags: do not auto-apply; **surface each to the operator** with a recommendation, **wait for the decision**, **apply** it (update affected sections, including earlier ones like scope), and **re-run only if scope changed materially**.
- "**Human-mediated**" = the operator decides scope/requirement changes; the agent surfaces and executes, never changes scope autonomously. The **BRD acceptance gate** is the backstop for any missed flag.

The code map persists and is reused downstream: the FRD decomposes functional changes per module; Jira epics map to affected areas.

---

## 11. Agent topology & orchestration

- **Orchestrator** = the tool's session reading the instruction file. Drives the workflow; delegates to subagents. Hub-and-spoke (subagents return summaries to the orchestrator; they don't chain to each other; kept flat).
- **Interactive stages run as their own sessions** — the BRD/FRD author is the *active agent* of a dedicated session (its own window), the human chats with it directly. Not a subagent (subagents are autonomous workers, not chat surfaces).
- **Autonomous sub-work = subagents** (isolated context, returns a summary): `source_processor` (×N parallel), `code_impact`, the validators.
- **Context per agent:** the orchestrator/session window holds the instruction + the running coordination thread (compact summaries); each subagent's heavy work stays in its own window and is discarded. State flows between stages via **files**, not shared context.
- **Don't over-create agents** — a few real agents (orchestrator + authoring/validation roles + `source_processor` + `code_impact`); everything else is skills.

### Agent vs Skill vs Profile
- **Agent** = actor with a job, loop, tools. **Skill** = reusable instruction module the agent loads. **Profile (YAML)** = per-domain data that parameterizes a generic skill.

### Optional later hardening (Claude-only)
A deterministic **Python spine** can own cross-step ordering (`claude -p` per node). Claude-only; not the agnostic path.

---

## 12. Seams summary

- **Constant (shared core):** orchestration *logic*; generic ingestion connectors; agents + generic skills (`brd_author`, `brd_validator`, `frd_author`, `frd_validator`, `jira_author`, `jira_validator`, `source_processor`, `code_impact`, `code_map_build`); universal BRD/FRD structure; manifest/selective-read; Python plumbing.
- **Domain-specific (by domain key):** pre-processing skills + order; unique pre-processors; `brd_profile.<domain>.yaml`; `jira_template.<domain>.yaml`; the adapter's tag vocabulary.
- **Tool-specific (the overlay, ×2):** instruction file; agent/subagent definition files; per-stage prompt files; launch.

---

## 13. File & format conventions

Heuristic: **code-parsed → YAML; model-read-as-instructions → Markdown; both → YAML front-matter + Markdown body.**
- **YAML/JSON:** `UI_INPUT.yaml`, `brd_profile.<domain>.yaml`, `jira_template.<domain>.yaml`, pre-processing skill list, `index.json`, `code_map.json`, `jira_plan.json`, `jira_trace.json`.
- **Markdown:** skills, agent/subagent wrappers, prompt files, `BRD.md`, `FRD.md`, narrative domain context, instruction files.

---

## 14. Registry layout

```
registry/
  core/                      # shared, authored once (tool-agnostic)
    skills/                  # SKILL.md (both tools read these)
    scripts/                 # python plumbing (clone, ingest, hydrate, merge_manifest)
    profiles/                # brd_profile.<domain>.yaml
    templates/               # jira_template.<domain>.yaml
  overlays/
    claude/                  # CLAUDE.md + .claude/agents/*.md + prompt files + launch
    copilot/                 # copilot-instructions.md + *.agent.md + prompt files + launch
```
On Generate: scaffold = `core/` + `profiles[domain]` + `templates[domain]` + `overlays/<tool>`.

---

## 15. Tech stack & environment

- **Frontend:** React + Vite (config UI).
- **Backend:** FastAPI (local) — filesystem + subprocess + git; creates scaffold, writes `UI_INPUT.yaml`, runs hydration, opens VSCode / starts the agent where allowed.
- **State:** SQLite (MVP) → Snowflake (prod).
- **Deploy:** local VDI (MVP); AWS deferred.
- **Models:** Claude (Opus) via JPMC Bedrock (`CLAUDE_CODE_USE_BEDROCK`); Copilot uses its own model selection.
- **Execution surfaces:**
  - **Claude Code** — interactive session in the VSCode terminal (authoring); CLI + headless available (optional Claude-only spine); Python can drive it locally.
  - **Copilot** — **VSCode agent mode** (no CLI in target env; not Python-launchable). Orchestrates via `copilot-instructions.md` + custom agents/subagents; parallelism via coordinator instructions.
  - **No custom chat UI for MVP** — operator authors in the tool's native session after the UI hands off.

---

## 16. MVP scope vs deferred

**In MVP:** five layers; one domain (recommend Payment Brand Implementations first); generic ingestion; domain-adapter pre-processing; per-source parallel fan-out; manifest + selective read; **code clone + coarse map + coarse/deep impact + human-mediated flag loop**; BRD + FRD authoring/validation; Jira **epic** creation with one human gate + adapter push; basic metrics; local VDI; **agnostic build (Claude + Copilot via the UI switch)**; AI-session-driven orchestration; stage transitions via prompt files.

**Deferred:** Jira stories; sync/freshness; change detection & downstream flagging; semantic retrieval; multi-domain breadth; AWS + Snowflake; the Claude-only deterministic spine; auto-launch of the session; any custom context-refresh mechanism; automated (non-human-mediated) impact re-runs.

---

## 17. Decisions locked

- Five layers; Jira epic creation between FRD and Metrics.
- No RAG for MVP; large-context + manifest-driven selective read; semantic retrieval deferred.
- Selective read (`index.json`) is a day-one artifact; per-section, not per-question; **always selective — manifest always loaded, expand on demand (no load-all path, no size threshold).**
- Domain seam = adapter (data) / profile (BRD/FRD) / template (Jira). Generic skill engine + per-domain YAML; skill never edited at runtime.
- Jira epic-only MVP; single combined human gate; push via `jpmc_adapters`; `jira_trace.json` idempotency.
- UI = config only → `UI_INPUT.yaml` (now includes the **requirement/project frame**); scaffolder = plumbing; agents = judgment.
- **AI session is the orchestrator; Python is called-plumbing.** Subagents internal, not headless. No headless on the authoring path.
- **Data Processing = one `source_processor` fanned out per source in parallel + deterministic merge.**
- **Agnostic build: one shared core + two idiomatic overlays (Claude/Copilot), chosen by a UI switch**; tool file generated from one template; no runtime `AGENTS.md`; **thin agent-file wrappers over shared skills**.
- **Stage transitions live in the instruction file** (`/clear` vs `Ctrl+N` + a prompt file); operator-performed, agent-surfaced. **No custom context-refresh mechanism** (auto-compaction + new-thread at boundaries).
- **BRD authoring**: framing discovery up front + section-by-section with revisiting, shared memory, deliberate order (exec summary last); info hierarchy sources → UI frame → chat gap-fill.
- **Code**: clone repo to workspace; AI builds coarse `code_map.json`; coarse impact threads high-level code context into early sections; **deep impact at the code-impact section** (a `code_impact` subagent reading actual code); business-framed BRD section (detail → FRD); **human-mediated flag loop** encoded via a required Flags output + a flag-handling rule.

---

## 18. Next chat — produce the requirements document

Open questions to resolve there:

1. `must_capture` / `probe_if_missing` at **topic** vs **section** level.
2. Baseline sections in the **skill** vs a **`brd_baseline.yaml`**.
3. **FRD profile + Jira template** schemas — give them the BRD-profile treatment.
4. **Gate inventory** — BRD acceptance gate, FRD acceptance gate (plus the Jira push gate).
5. **First domain** + its concrete **tag vocabulary** (adapter-emits ↔ profile-topics contract).
6. **`code_map.json` schema** + the **Flags** schema (types, fields, thresholds for "material" scope change).
7. Whether **ingestion** ever varies by domain (currently generic).
8. **Re-run / idempotency / error handling** beyond Jira; what `UI_INPUT` + SQLite persist.
9. **Overlay authoring** — hand-maintain the two overlays vs generate both from one workflow spec.
10. **Auto-launch vs manual** start per tool/environment; the validation spike for Copilot agent-mode + `runCommands` policy in the VDI.

Subsequent chats: tech spec → per-tool task lists → UI design.
