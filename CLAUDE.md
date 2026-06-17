# CLAUDE.md — PDLC_App_v2 (external Claude Code build)

**Read this file first, at the start of every session.** It tells you what this repo is, where the authoritative design lives, how to execute a task, and the rules you must not break. It is short on purpose; the substance is in `docs/`.

---

## What this repo is

You are building **PDLC_App_v2** — an agentic **BRD → FRD → Jira** generation pipeline for JPMC Merchant Services. Five layers: **Data & context → BRD → FRD → Jira epics → Metrics**. This repo is the **external Claude Code build**; it is validated here, then ported to the JPMC VDI later via thin overlays (the port artifact is produced separately — not your concern in this repo).

**First slice (what you are building now):** single domain `payment_brand`; single repo; **BRD → FRD only** (no Jira push); one PDF input + one Stratus C repo. Breadth (Jira, multi-input, multi-repo, more languages, multi-domain) is explicitly deferred — see `TASK_LIST.md` Phase 5.

---

## Authoritative documents (precedence order — do not reopen)

All design docs live in **`./docs/`**. They are authoritative and frozen; you implement against them, you do not redesign them.

1. **`docs/REQUIREMENTS.md`** — WHAT / WHY. FR/NFR IDs, MoSCoW, the ten resolved decisions **D1–D10**. Every requirement *rationale* ("Why: …") is a binding constraint. **Do not reopen D1–D10.**
2. **`docs/TECH_SPEC.md`** — HOW. On-disk schemas, the code-impact subsystem (extractor / dispatcher / onboarding gate), the seams, `jpmc_adapters`, telemetry→metrics, gate thresholds, build checks. **Every YAML/JSON block here is a contract; field names are part of it.** Build directly off these.
3. Supporting context (read when a task cites them): `docs/SKILLS_INDEX.md`, `docs/BUILD_OVERVIEW.md`, `docs/brd_frd_overview.html`, `docs/COPILOT_VDI_VALIDATION.md`, and the seed skills `docs/brd_author.skill.md`, `docs/code_impact_assess.skill.md`, `docs/code_map_build.skill.md`, `docs/max-autonomy.skill.md`.

> The older **v1 8-layer platform (L0–L8)** is **dead**. Ignore any v1 reference.

---

## How to execute a task

Work through **`TASK_LIST.md`** in order. Each task is sized for a single session and carries:

- **Depends on** — prior tasks + the on-disk artifacts that must already exist. **Verify these exist before starting** (list the files; if a dependency is missing, stop and say so).
- **Reads** — the *exact* doc + section to open (e.g. ``docs/TECH_SPEC.md`` §5.3). **Open and read the cited sections before writing anything.** Do not work from memory of the design; the cited section is the contract.
- **Creates / edits** — the exact output paths (from `docs/TECH_SPEC.md` §2).
- **Acceptance** — concrete, checkable conditions. The task is done only when all are true.
- **Fixture / proof** — what demonstrates correctness.

After finishing a task, **tick its checkbox in `TASK_LIST.md`** and commit. The checkbox state is how a later session knows what is done.

---

## Context-restart protocol (important — context will get large)

It is safe to **start a fresh chat / new context window at any phase boundary** (marked in `TASK_LIST.md`). To re-orient a fresh session:

1. Read this `CLAUDE.md`.
2. Open `TASK_LIST.md`; the **first unchecked task** is where to resume.
3. Inspect the repo on disk (`core/`, `overlays/`, `runs/`, `fixtures/`) to confirm what the checkboxes claim — disk state is ground truth.
4. Execute the next task per "How to execute a task" above.

Durable state lives in **files and git**, never in the conversation. Never rely on something said in an earlier session; if it matters, it is on disk.

---

## Hard rules (carry these into every task)

- **Ladder discipline.** Requirements define WHAT/WHY; the tech spec defines HOW; the task list defines the build sequence. If a task would change a pinned contract or reopen D1–D10, **stop and flag it** — that is out of scope.
- **Two seams only (FR-XS-01):** the **domain seam** (adapter / profiles / template / vocabulary) and the **runtime-tool seam** (instruction file / wrappers / prompt files / launch). The per-language **extractor** is the one non-domain variation point, governed by the onboarding gate. Nothing else varies.
- **Binding rationales (never violate):** the structural extractor is **deterministic and frozen** — never model-rewritten at runtime; the map-build gate is **model-free**; the model owns only `purpose` + `tags` in the code map; ingestion **never branches on domain**; the only external mutation is the (deferred) Jira push; scope changes are **operator-decided** (human-mediated flag loop).
- **MVP scope:** single domain `payment_brand`; single repo; **in-session execution** (no direct Claude API); files-as-artifacts + **JSONL ledger** (no SQLite); **BRD → FRD only** this slice.
- **Cite-or-flag:** every substantive artifact claim is grounded to a source/frame/operator answer or marked `[TBD — unsourced]`. Never invent.

---

## Known open flag (do not silently resolve)

**F1 — `mandate` emitter mismatch.** `docs/REQUIREMENTS.md` D5 lists `mandate` as emitted by **both** `change_type_assess` and `article_summarize`, but the `docs/TECH_SPEC.md` §6.6.3 `adapter.yaml` example emits it only from `change_type_assess`. Build check §10.5 (no-drift) will fire on this. When you reach TASK-017/021, **surface it to V and reconcile — do not pick one yourself.**

---

## Repo layout (after TASK-000)

```
./CLAUDE.md            ← you are here
./TASK_LIST.md         ← the build sequence
./docs/                ← authoritative design (REQUIREMENTS, TECH_SPEC, supporting)
./core/                ← the generic core you build (skills, scripts, extractors, adapters, profiles, templates)
./overlays/            ← the two runtime-tool overlays (claude, copilot)
./fixtures/            ← input fixtures (PDF, C repo, signed-off code_map)
./runs/                ← run workspaces created when the spine is exercised (Phase 3+)
```
