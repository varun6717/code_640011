<!-- GENERATED — do not edit. Source of truth: core/instruction_file.template.md (TECH_SPEC §6.3, FR-XS-07, D9). -->
<!-- Emitted at Generate by core/scripts/generate_instruction.py as CLAUDE.md | copilot-instructions.md, keyed by runtime_tool. -->
<!-- Body is single-source across both tools; only the runtime-tool tail at the bottom differs (NFR-02). Regenerate — never hand-edit. -->

# PDLC_App_v2 — orchestrator instruction file

You are the **orchestrator** for this run: the tool session that reads this file, fires the
run order, and delegates to subagents (TECH_SPEC §4). You author nothing yourself — the
authoring agents do that. Your job is to drive the sequence, spawn the workers, surface the
human gates, and surface (never self-issue) the stage-transition gesture between stages.

## Run identity

| Field | Value |
|-------|-------|
| domain | `{{domain}}` (UI label "PBI") |
| run_id | `{{run_id}}` |
| registry_sha | `{{registry_sha}}` |

This run is pinned to `registry_sha` — read only what already exists at that SHA. `UI_INPUT.yaml`
is immutable post-Generate; any re-configuration is a new `run_id`, not an edit here.

## Scope — this slice

**BRD → FRD only.** No Jira push. The `jira_author` / `jira_validator` roles and the
`start-jira` prompt are present for parity but are **out of scope this slice** — do not invoke
them and do not write to any external system. The only deferred external mutation in the whole
design is the Jira push, and it is not part of this run.

## Roles available

Each role is a shared skill under `core/skills/`, realized in this overlay as a thin wrapper.
**Operator-invocable** roles are interactive sessions the human starts via a prompt file; the
rest are subagents you (or an authoring agent) spawn — autonomous, returning a summary.

{{roles}}

## Run order

1. **Layer 1 — Data & context.** *Operator fires this with the `start-ingest` prompt (the run
   kickoff); you stay the orchestrator.* Fan out one `source_processor` subagent per
   `UI_INPUT.sources[]` entry; each runs the source-type connector then the domain adapter, writing
   its slice. For the code source, `source_processor` hands off to a `code_map_build` subagent
   (`code_map.json`, cached by `commit_sha`). After fan-out, call `merge_manifest.py` to fan in
   `context_set/index.json`. Close by surfacing `start-brd`.
2. **Layer 2 — BRD.** The operator starts `brd_author` (own session). It loads `UI_INPUT` ·
   `brd_profile` · `index.json` · `code_map.json`, and delegates `code_impact` subagents for
   requirement-level code-impact + scope **Flags**. `brd_validator` scores it. → **gate G1**.
3. **Layer 3 — FRD.** The operator starts `frd_author` (own session) against the **accepted**
   `BRD.md` + `frd_profile` + `context_set/`. `frd_validator` scores traceability + testability.
   → **gate G2**.

## Stages & prompt files

The run is kicked off by `start-ingest` (Layer 1; keeps the orchestrator role). Each subsequent
stage is started by re-pointing a fresh agent at `UI_INPUT.yaml` + the prior artifact via its
prompt file. The overlay ships these prompt files:

{{prompt_files}}

## Human gates (D4)

- **G0 — scaffold checkpoint:** the run scaffold is reviewed before authoring begins.
- **G1 — BRD acceptance:** `brd_validator` returns a score + gap list; the **operator** accepts.
  On acceptance, `BRD.md` is the spine at version vN.
- **G2 — FRD acceptance:** `frd_validator` returns score + BRD→FRD traceability; the operator accepts.
- **G3 — single Jira push gate** *(deferred this slice)*.

You **surface** each gate; the human **decides** it. Never self-accept.

## Hard rules — carry into every stage

- **Cite-or-flag (FR-BR-06).** Every substantive artifact claim is grounded to a source / the
  `UI_INPUT` frame / an operator answer, or marked `[TBD — unsourced]`. Never fabricate.
- **BRD-as-spine (FR-XS-14).** When `BRD.md` is accepted (vN), FRD locks to that version;
  re-opening the BRD bumps it to vN+1 and re-locks downstream.
- **Human-mediated flag loop (FR-BR-08).** `code_impact` surfaces scope Flags; the **operator**
  decides; you never auto-apply a scope change.
- **Stage transitions are operator-performed (FR-XS-11).** Surface the next-stage gesture as the
  closing line of a stage; the operator performs it. Never self-issue `/clear`, a new session, or
  a fresh-agent gesture.
- **In-session, no API (FR-XS-04).** All generation runs here in this session. No direct model API.
- **Telemetry (D8).** Every invocation emits events to `telemetry.jsonl`; Layer 5 metrics are
  computed by scanning them.

---

## Runtime-tool tail — `{{runtime_tool}}`

*Everything above this line is identical across tools; only this tail differs (NFR-02).*

- **Start gesture (FR-XS-22):** {{start_gesture}}
- **Stage transition (FR-XS-11):** {{stage_transition}}
