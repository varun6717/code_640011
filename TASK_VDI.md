# TASK_VDI.md — Milestone 5B build list (execute on the VDI with Copilot)

**What this is.** The Phase 5B enhancement tasks, packaged to be executed **on the JPMC VDI**
with Copilot (Opus 4.8). The MVP (BRD→FRD, single domain, SharePoint + Bitbucket) is running;
this file adds breadth one task at a time. The canonical specs also live in `TASK_LIST.md`
(TASK-060–078) — this file is the **VDI operating manual** around them: the rules, the
execute→verify→publish loop, and the environment specifics.

**How to use it.** Pick the first unchecked task, top-down. For each task, follow the
**Execution protocol** below. Tick the box only when every Acceptance condition is true and the
proof + build checks are green. Disk + git are ground truth.

---

## Execution protocol (run this loop for EVERY task)

1. **Read the cited design first.** Each task names the exact `docs/…` §sections and files under
   **Reads** — open them. Do not work from memory; the cited section is the contract.
2. **Verify dependencies exist** (the **Depends on** files). If one is missing, stop and say so.
3. **Implement the GENERIC piece.** Build what is testable here. For anything that must hit a
   **real external API or secret store**, do NOT inline it — leave a `set_*`-style **injection
   seam + a `[TBD — VDI]` placeholder** in its own isolated function, and put the real call in a
   gitignored `/vdi` plugin that snaps into the seam (see **Hard rules** §S). Keep each
   env-specific call in its own function so it never shares a merge region with generic code.
4. **Verify.** Run the task's **Proof** and then **`python core/scripts/build_checks.py`** — all
   5 §10 checks must be green. A connector also runs its `fixtures/<type>/verify_*.py`.
5. **Publish so the UI run sees it** (only after green):
   `python core/scripts/publish_registry.py <registry-repo-url> --branch feature/pdlc_app`
   then delete the stale run workspace and **re-Generate** from the UI to test end-to-end.
   (Local edits are invisible to the UI until the registry is re-published.)
6. **Tick the box** and (if the VDI can push to GitHub) push so the external copy stays current.

---

## Hard rules (never violate — condensed from `CLAUDE.md` / `docs/`)

- **S. Build-and-port / seam discipline.** Generic code is shared and built+tested first; any
  real API/secret is reached through a seam (`set_downloader`/`set_fetcher`/`set_backend`) with a
  `[TBD — VDI]` placeholder. The real implementation is a gitignored `/vdi` plugin that registers
  itself into the seam; a committed auto-load hook imports `/vdi` if present (no-op if absent).
  Env-specific code lives in its **own function** so VDI edits and generic edits never collide.
- **Two seams only.** The **domain seam** (adapter / profiles / template / vocabulary) and the
  **runtime-tool seam** (instruction file / wrappers / prompts / launch). The per-language
  **extractor** is the one non-domain variation point, governed by the **onboarding gate**.
- **Binding rationales.** The structural extractor is **deterministic + frozen** — never
  model-rewritten at runtime. The map-build gate is **model-free**. The model owns only
  `purpose` + `tags` in the code map. **Ingestion never branches on `domain`.** The **only**
  external mutation of a run is the Jira push. Scope changes are operator-decided.
- **Descriptor parity.** Every source connector emits the **same descriptor shape** as
  `ingest_file.py` (`type, source, url/…, staged_path, auth_ref, ingest_ts`). Downstream
  (`pdf_extract → article_summarize → change_type_assess`) must not change.
- **Onboarding skills: propose-never-bless.** The onboarding aids (extractor/domain/profile/
  adapter) **propose reviewable artifacts**; a human **freezes**. Amendments are **build-time**
  (committed + re-pinned), never runtime mutations. §10 build checks gate every freeze.
- **Cite-or-flag.** Every substantive artifact claim is grounded to a source/frame/operator
  answer or marked `[TBD — unsourced]`. Never invent.
- **§10 must stay green.** No task lands with a red build check. Connectors keep §10.4; the
  domain seam keeps §10.1/10.3/10.5; overlays keep §10.2.

---

## VDI environment notes

- **Python deps.** Scripts need `httpx` + `PyYAML`; extractor tasks also need
  `tree-sitter==0.25.2` + `tree-sitter-c==0.24.2` (ADR-001). No venv is assumed — use whatever
  Python you run the repo with. Check: `python -c "import httpx, yaml"`.
- **Auth (the seam, env backend).** Set as **user** env vars so the run inherits them:
  `PDLC_AUTH_BITBUCKET` (+ `_USER`), `PDLC_AUTH_SHAREPOINT` (+ `_USER`), and for new connectors
  `PDLC_AUTH_CONFLUENCE` / Jira likewise. The token never lands on disk — `auth_ref` is a pointer.
- **Registry / code repos.** Registry = `feature/pdlc_app`; Stratus code = `feature/c_repo`
  (one Bitbucket repo, two branches). Re-publish to `feature/pdlc_app` after any `core/` change.
- **Copilot layout (already fixed).** Generate emits `.github/copilot-instructions.md` +
  `.github/prompts/*.prompt.md`; agents are `*.agent.md` at the run root.

---

# The tasks (TASK-060 – 078, dependency order)

> Full canonical spec for each is in `TASK_LIST.md`. Open the **Reads** there if you need more
> than what's below.

## Carried fixes (independent, small — good warm-ups)

- [ ] **TASK-060 — Thread `runtime_tool` through G1/G2 telemetry**
  - **Reads:** `core/scripts/brd_validator.py` / `frd_validator.py` (`record_g1`/`record_g2`); `docs/TECH_SPEC.md` §8.1.
  - **Do:** replace hardcoded `tool="claude"` in the validators' telemetry `Emitter` with `UI_INPUT.runtime_tool`.
  - **Acceptance:** a copilot run's G1/G2 envelopes record `tool: copilot`; build_checks green.

- [ ] **TASK-061 — Reconcile D5 `card_brand`/`message_format` `emitted_by`**
  - **Reads:** `CLAUDE.md` port note; `docs/REQUIREMENTS.md` D5 table; `vocabulary.payment_brand.yaml` (already r2).
  - **Do:** add `code_map_build` to `emitted_by` for `card_brand` + `message_format` in the D5 table.
  - **Acceptance:** D5 table == `vocabulary.yaml`; §10.5 green.

- [ ] **TASK-062 — Align `UI_INPUT.example.yaml` frame with the bundled PDF**
  - **Reads:** `fixtures/UI_INPUT.example.yaml`; the bundled PDF (Mastercard mandate).
  - **Do:** the frame says "Discover" but the PDF is the Mastercard mandate — align title/intent.
  - **Acceptance:** frame matches the fixture; verify_frontend/backend green.

## Connectors

- [ ] **TASK-063 — Confluence connector (`ingest_confluence.py`)**
  - **Depends:** TASK-055 (`ingest_sharepoint.py` pattern), TASK-052 (auth seam).
  - **Reads:** `ingest_sharepoint.py` + `ingest_file.py`; `docs/TECH_SPEC.md` §6.6.2, §3.2; FR-DC-01/11/12.
  - **Do:** generic source-type-keyed connector, same descriptor as `ingest_file.py`, `auth_ref: jpmc_adapters:confluence`, no domain branch. **Real Confluence fetch behind a seam + `[TBD — VDI]` placeholder, in its own function** (real call = `/vdi` plugin). Offline local-path convenience.
  - **Acceptance:** a `type:confluence` source stages content + contract-valid descriptor (offline local path); §10.4 maps `type:confluence → ingest_confluence.py` green; no domain branch.
  - **Proof:** `fixtures/confluence/verify_confluence.py`.

## Jira (the only external mutation + G3)

- [ ] **TASK-064 — Jira authoring + validation skills + `jira_template`**
  - **Reads:** `docs/TECH_SPEC.md` §9.4, §10.3; FR-JR-*, FR-XS-17.
  - **Do:** `core/skills/jira_author.skill.md` + `jira_validator.skill.md`; add `jira_template` to the `payment_brand` seam (then §10.3 requires it).
  - **Acceptance:** a fixture FRD → jira plan authored + gated; §10.3 checks `jira_template` (green); no push yet.

- [ ] **TASK-065 — Jira push seam + `jira_plan/` + `trace.json` + G3**
  - **Depends:** TASK-064, TASK-052.
  - **Reads:** `docs/TECH_SPEC.md` §3.8, §7, §9; FR-JR-*.
  - **Do:** generic Jira-push connector behind a seam + placeholder (real JPMC Jira REST = `/vdi` leaf); emit `jira_plan/` + `trace.json`; gate **G3** before push. Push is the **only** external mutation — operator-confirmed.
  - **Acceptance:** G3 gates; stub push records `trace.json`; no secret on disk; build_checks green.

## Code-impact enhancements (real-corpus value)

- [ ] **TASK-066 — `purpose`-as-discovery in the coarse pass**
  - **Reads:** the TASK-040 coarse pass; ADR-005.
  - **Do:** let the coarse pass use `purpose` for semantic candidate **discovery** (surface a component whose `purpose` fits the requirement even when the tag wasn't applied). Advisory + cite-or-flag; never silently widen scope.
  - **Acceptance:** a mis-tagged-but-`purpose`-relevant component surfaces as a flagged candidate; deep-pass closure unchanged.

- [ ] **TASK-067 — Doc-side semantic-gap signal**
  - **Reads:** ADR-005 open-Q #2; the code-side `uncovered_concepts`.
  - **Do:** add a doc-arm analog of `uncovered_concepts` so §5.4.1 vocab-adequacy is symmetric across both arms.
  - **Acceptance:** the doc arm emits a leftover-meaning signal; §5.4.1 considers both.

## Multi-repo

- [ ] **TASK-068 — Multi-repo cross-repo closure**
  - **Reads:** `docs/TECH_SPEC.md` §3.3 (`external_calls`/`exposes`); FR-DC-18.
  - **Do:** populate the reserved cross-repo fields in `code_map.json` + cross-repo closure; multi-repo clone (N repos/run).
  - **Acceptance:** a 2-repo run maps cross-repo calls; closure surfaces cross-repo impact; single-repo unaffected.

## Domain onboarding (proposer skills → orchestrator)

- [ ] **TASK-069 — `extractor_onboard` skill + a 2nd language extractor**
  - **Reads:** `docs/TECH_SPEC.md` §5.7, ADR-001, FR-DC-19; `docs/ENV_PRECHECK.md`.
  - **Do:** skill proposes/refines an extractor against a sample → reviewable artifact for human **freeze**; onboard a 2nd language (Java/Python). Structural-only, **model-free build**.
  - **Acceptance:** a 2nd-language extractor onboarded + frozen vs an oracle; §10 green; build stays model-free.

- [ ] **TASK-070 — `domain_onboard` skill (propose a new domain's vocabulary)**
  - **Depends:** TASK-069. **Reads:** ADR-003, FR-DC-20; `vocabulary.payment_brand.yaml`.
  - **Do:** propose a new domain's first `vocabulary.<domain>.yaml` from sample docs + the untagged (`purpose`-only) code-map → reviewable artifact (propose-never-bless).
  - **Acceptance:** 2nd-domain samples → a freezable `vocabulary.<domain>.yaml`; §10.1 holds once frozen.

- [ ] **TASK-071 — `profile_onboard` skill**
  - **Depends:** TASK-070. **Reads:** ADR-004, FR-DC-22, FR-BR-08.
  - **Do:** route approved tags into profile sections — surface unconsumed tag, propose section `id` + `must_capture`/`probe_if_missing` → reviewable **profile diff**. Bulk + incremental. Build-time only (§6.6.1).
  - **Acceptance:** an unconsumed tag → a freezable profile diff; no runtime mutation.

- [ ] **TASK-072 — `adapter_onboard` skill (+ promote `pdf_extract` to `core/skills/`)**
  - **Depends:** TASK-070, TASK-071. **Reads:** ADR-005, FR-DC-23, §6.6.3; the F1+3 drift class.
  - **Do:** propose the adapter pack by guided conversation; **derive each skill's `emits` from the vocabulary's `emitted_by`** (kills the drift class). Bulk + incremental. Promote `pdf_extract` to `core/skills/` first. Propose-never-bless.
  - **Acceptance:** proposes a pack whose `emits` == `emitted_by` by construction; §10.5 no-drift green.

- [ ] **TASK-073 — Domain-onboarding orchestrator (`onboard.py` + `ONBOARD_INPUT.yaml`)**
  - **Depends:** TASK-069..072, TASK-048. **Reads:** the `onboard.py` design in `TASK_LIST.md`; §6.6.1, §10, Appendix B.
  - **Do:** `mode: onboard` — authoring pull → run the four helpers **in order** with a human **freeze gate** each → `build_checks.py` as a **HARD GATE** (red ⇒ no push) → commit + push to Bitbucket → emit new `registry_sha`. `mode: run` consumes (unchanged). Push = build-time git action, not a runtime mutation.
  - **Acceptance:** a new domain authored end-to-end → §10 green → pushed → `registry_sha` emitted; red §10 blocks push.

- [ ] **TASK-074 — Multi-domain enablement (`domains_index.yaml` + UI)**
  - **Depends:** TASK-073. **Reads:** FR-BR-11/14, FR-XS-21, D2; the UI `DOMAINS` list.
  - **Do:** add `domains_index.yaml` + drive the UI domain dropdown from it (instead of hardcoded `payment_brand`).
  - **Acceptance:** a 2nd domain appears in the UI + Generates a correctly-pruned scaffold; `payment_brand` unaffected.

## Vocabulary adequacy (L2)

- [ ] **TASK-075 — `vocab_gap_assess` + amendment loop**
  - **Depends:** TASK-013 (L1 detector). **Reads:** ADR-003, FR-DC-21.
  - **Do:** model pass over the newly-introduced untagged delta → propose a candidate tag + evidence; human-gated amendment → `vocab_sha` bump → re-tag pass.
  - **Acceptance:** an untagged delta → proposed tag + evidence; amendment bumps `vocab_sha` + re-tags; no auto-mutation.

## Infra / UX (lower priority)

- [ ] **TASK-076 — Metrics store + dashboard (SQLite)** — promote the JSONL ledger to a queryable store + dashboard, additive (JSONL stays source of truth). FR-MX-*, D8.
- [ ] **TASK-077 — Auto-launch** — automate the manual start gesture where the environment permits (Claude-only first). FR-XS-25.
- [ ] **TASK-078 — UI enhancements** — role gating on the configurator + a richer live telemetry/metrics surface. FR-XS-*.

---

> ✅ **A task is done when:** Acceptance true · its proof green · `build_checks.py` (§10 ×5) green ·
> the registry re-published (so the UI run uses it) · box ticked. Come back to the external
> Claude Code session for help when a task fights you — paste the failing proof / build-check.
