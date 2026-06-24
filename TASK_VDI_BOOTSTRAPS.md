# TASK_VDI_BOOTSTRAPS.md — paste-ready Copilot prompts for the 5B tasks

One bootstrap per task (TASK-060–078). **How to use:** find the task, copy the fenced block,
fill any `<<PLACEHOLDER>>` (reference files, API shapes, choices), paste into Copilot on the VDI.
Every prompt carries the same spine: implement the generic piece → keep real APIs/secrets behind
a seam + `[TBD — VDI]` placeholder in their own function → verify (proof + `build_checks.py`) →
re-publish the registry so the UI run uses it.

> **Standing rules for all tasks** (state once; the prompts assume them): never branch on
> `domain`; keep `build_checks.py` (§10 ×5) green; secrets only via the auth seam (`handle.reveal()`,
> never on disk); connectors keep the exact `ingest_file.py` descriptor shape; onboarding skills
> **propose, never bless** (human freezes; amendments are build-time, not runtime). After any
> `core/` change: `python core/scripts/publish_registry.py <registry-url> --branch feature/pdlc_app`
> then re-Generate. Run Python with `httpx` + `PyYAML` importable (extractor tasks also need
> `tree-sitter`).

---

## TASK-060 — Thread `runtime_tool` through G1/G2 telemetry

```
TASK: In core/scripts/brd_validator.py and frd_validator.py, the telemetry Emitter in
record_g1 / record_g2 hardcodes tool="claude". Replace it with the run's actual tool from
UI_INPUT.runtime_tool, so the acceptance ledger envelopes carry copilot vs claude correctly.
Read docs/TECH_SPEC.md §8.1 for the envelope contract first.
Change ONLY the tool field source — no other behavior.
VERIFY: run a copilot-config run (or the existing proof) and confirm the G1/G2 ledger
envelopes show tool: copilot; then python core/scripts/build_checks.py -> all 5 green.
(No registry re-publish needed unless this code is hydrated into the run.)
```

## TASK-061 — Reconcile D5 `card_brand` / `message_format` emitted_by

```
TASK: In docs/REQUIREMENTS.md, the D5 table is missing code_map_build in the emitted_by
column for card_brand and message_format. core/profiles/payment_brand/vocabulary.payment_brand.yaml
already has the r2 fix. Add code_map_build to those two rows in the D5 table so D5 and the
vocabulary agree. Read CLAUDE.md's resolved-flag port note for context.
Edit only the D5 table. VERIFY: python core/scripts/build_checks.py -> §10.5 green; diff the
D5 emitted_by against vocabulary.payment_brand.yaml -> identical for all 12 tags.
(Docs-only; no registry re-publish needed for the run.)
```

## TASK-062 — Align `UI_INPUT.example.yaml` frame with the bundled PDF

```
TASK: fixtures/UI_INPUT.example.yaml's frame says "Discover" but the bundled PDF fixture is the
Mastercard mandate. Update frame.title and frame.intent to match the actual Mastercard-mandate
subject so the fixture is self-consistent. Edit only the frame block.
VERIFY: python fixtures/frontend/verify_frontend.py and fixtures/generate/verify_backend.py
-> green; python core/scripts/build_checks.py -> 5 green.
```

## TASK-063 — Confluence connector (`ingest_confluence.py`)

```
TASK: Create core/scripts/ingest_confluence.py — the type:confluence source connector. Model it
EXACTLY on core/scripts/ingest_sharepoint.py (same structure, seam, descriptor). Read
ingest_sharepoint.py + ingest_file.py and docs/TECH_SPEC.md §6.6.2, §3.2 first.

REFERENCE (working Confluence API example, dev-time only, do not import/vendor):
  <<PASTE_CONFLUENCE_REFERENCE_PATH_OR_ATTACH>>

1) Generic connector: stage content into <dest>/<source>/ and emit the SAME descriptor shape as
   ingest_file.py (type, source, url, staged_path, auth_ref, ingest_ts). auth_ref defaults to
   jpmc_adapters:confluence. Never read or branch on `domain`. Keep the offline local-path
   convenience (a local path / file:// url stages directly) like ingest_sharepoint.py.
2) Real fetch behind a seam: put the live Confluence call in ONE isolated function (e.g.
   _fetch_confluence) with a set_fetcher-style injection point + a [TBD - VDI] placeholder that
   raises NotImplementedError. The real call (modeled on REFERENCE) is a /vdi plugin, NOT inlined.
   token via handle.reveal(), only in the request header, never on disk; raise on non-2xx/empty.
3) Confluence resides as: <<A SPACE/PAGE-TREE URL the connector LISTS (pull every child page),
   OR specific page URLs>> — implement accordingly (mirror SharePoint's folder-listing if "lists").
VERIFY: fixtures/confluence/verify_confluence.py (create it on the ingest_sharepoint proof's
pattern, local-path stand-in) -> green; python core/scripts/build_checks.py -> §10.4 maps
type:confluence -> ingest_confluence.py, 5 green; AST-confirm no `domain` branch.
PUBLISH after green: publish_registry.py ... --branch feature/pdlc_app; re-Generate.
DO NOT: change ingest_file.py / the descriptor shape, import REFERENCE, branch on domain.
```

## TASK-064 — Jira authoring + validation skills + `jira_template`

```
TASK: Add Jira authoring to the seam. Read docs/TECH_SPEC.md §9.4 (jira) and §10.3 (seam requires
jira_template), plus FR-JR-* and FR-XS-17. Mirror the brd_author/brd_validator skill pattern.
1) Create core/skills/jira_author.skill.md (FRD -> Jira epics/stories) and
   core/skills/jira_validator.skill.md (the G3-style gate on the plan).
2) Add jira_template to the payment_brand domain seam (core/profiles/payment_brand/). Once it
   exists, §10.3 requires it for the domain — that's expected.
3) NO external push in this task (that's TASK-065). cite-or-flag throughout.
VERIFY: run a fixture FRD through jira_author -> a jira plan; jira_validator gates it;
python core/scripts/build_checks.py -> §10.3 now checks jira_template, all 5 green.
PUBLISH after green; re-Generate.
DO NOT: push to any external Jira yet; never branch on domain in shared code.
```

## TASK-065 — Jira push seam + `jira_plan/` + `trace.json` + G3

```
TASK: Implement the Jira push — the ONLY external mutation of a run. Read docs/TECH_SPEC.md §3.8
(jira_plan/, trace.json), §7 (push seam), §9 (G3). Depends on TASK-064 + the auth seam (TASK-052).

REFERENCE (working JPMC Jira REST example, dev-time only):
  <<PASTE_JIRA_REFERENCE_PATH_OR_ATTACH>>

1) Create core/adapters/jpmc_adapters/jira.py: the generic push interface behind a set_*-style
   seam + a [TBD - VDI] placeholder (the real JPMC Jira REST call is a /vdi plugin modeled on
   REFERENCE; token via handle.reveal(), header-only, never on disk).
2) Emit jira_plan/ + trace.json (issue keys) per §3.8. Gate G3 on the plan BEFORE any push.
3) The push is operator-confirmed and is the SOLE external mutation of the run.
VERIFY: stub the push (set the seam to a local stub); G3 gates; trace.json records keys;
grep the workspace -> no secret on disk; python core/scripts/build_checks.py -> 5 green.
PUBLISH after green; re-Generate.
DO NOT: make any other part of the run mutate externally; inline the real Jira call; log the token.
```

## TASK-066 — `purpose`-as-discovery in the coarse pass

```
TASK: Enhance the code_impact COARSE pass (TASK-040) so it also uses each code_map component's
model-owned `purpose` for SEMANTIC CANDIDATE DISCOVERY — surface a component whose purpose
describes the requirement's concept even when the matching tag was not applied. Read the coarse
pass + docs ADR-005 first.
Rules: this is the already-model-driven CONSUMER of the map, so it's allowed (the model-free rule
governs BUILDING the map, not reading it). Stay advisory + cite-or-flag: never silently widen
scope — surface discovered candidates via Flags for operator decision.
VERIFY: a fixture with an under-applied tag -> the coarse pass surfaces the component via purpose
(flagged); the deep-pass structural closure is unchanged; build_checks 5 green.
PUBLISH after green; re-Generate.
DO NOT: change how the map is BUILT; auto-expand scope without a Flag.
```

## TASK-067 — Doc-side semantic-gap signal

```
TASK: The code arm emits `uncovered_concepts` (meaning the vocabulary lacks); the doc arm has no
equivalent. Add a doc-side analog so vocabulary-adequacy detection (§5.4.1) is symmetric across
both arms. Read docs ADR-005 open-Q #2 and the code-side uncovered_concepts emission.
VERIFY: a doc carrying vocabulary-uncovered meaning -> a doc-side gap signal; §5.4.1 now considers
both arms; build_checks 5 green. PUBLISH after green; re-Generate.
```

## TASK-068 — Multi-repo cross-repo closure

```
TASK: Implement cross-repo support. Read docs/TECH_SPEC.md §3.3 (the reserved external_calls /
exposes fields) and FR-DC-18.
1) Populate external_calls/exposes in code_map.json during the map build.
2) Implement cross-repo closure (a requirement whose impact spans >1 repo) and multi-repo clone
   (N repos per run via clone.py, each pinned by commit_sha).
VERIFY: two linked fixture repos -> a cross-repo edge appears in code_map + closure surfaces the
cross-repo impact; a single-repo run is unaffected; build_checks 5 green.
PUBLISH after green; re-Generate.
DO NOT: break the single-repo path; branch on domain.
```

## TASK-069 — `extractor_onboard` skill + a 2nd language extractor

```
TASK: Build the extractor onboarding aid + onboard a second language. Read docs/TECH_SPEC.md §5.7
(port_check / onboarding gate), ADR-001 (tree-sitter), FR-DC-19, docs/ENV_PRECHECK.md.
1) Create core/skills/extractor_onboard.skill.md: given a code sample, it PROPOSES/refines a
   structural extractor and emits a reviewable enhancement artifact for HUMAN FREEZE (propose,
   never bless). The extractor build is deterministic + MODEL-FREE.
2) Onboard a 2nd language (e.g. <<Java|Python|COBOL>>) via the same gate, frozen with its own
   onboarding_manifest. The TASK-010 model-only fallback covers any unonboarded language meanwhile.
VERIFY: extract a sample repo in the new language -> matches a hand-checked oracle; build_checks
5 green; confirm the map BUILD stays model-free.
PUBLISH after green.
NOTE: depends on the C-extractor pattern (TASK-009/012) — read those for the frozen shape.
```

## TASK-070 — `domain_onboard` skill (propose a new domain's vocabulary)

```
TASK: Build core/skills/domain_onboard.skill.md. Read ADR-003, FR-DC-20, and
vocabulary.payment_brand.yaml (the target shape). Given a NEW domain's sample docs + the untagged
(purpose-only) code-map of a sample repo, PROPOSE the domain's first vocabulary.<domain>.yaml as a
reviewable artifact for human freeze. Propose, never bless.
VERIFY: feed 2nd-domain samples -> a proposed vocabulary.<domain>.yaml a human could freeze; once
frozen, §10.1 containment holds; build_checks 5 green.
NOTE: first real exercise is domain #2 (payment_brand is frozen by D5) — use a synthetic 2nd domain
to exercise it. Tighten this prompt once TASK-069's untagged map output is in hand.
```

## TASK-071 — `profile_onboard` skill

```
TASK: Build core/skills/profile_onboard.skill.md. Read ADR-004, FR-DC-22, FR-BR-08, and the
payment_brand profiles. It routes an APPROVED-but-unconsumed vocabulary tag into a profile section:
surface the unconsumed tag, PROPOSE a target section id + drafted must_capture / probe_if_missing
(sources from the tag's emitted_by; functional_kind/traces_to for the FRD), and emit a reviewable
PROFILE DIFF. Two modes: bulk (first whole profile at onboarding) + incremental (one tag at drift).
Vocabulary-first (§10.1). Build-time amendment only — never a runtime mutation (§6.6.1).
VERIFY: an unconsumed tag -> a proposed profile diff a human can freeze; build_checks 5 green.
NOTE: depends on a frozen vocabulary (TASK-070). Tighten once that's in hand.
```

## TASK-072 — `adapter_onboard` skill (+ promote `pdf_extract` to core/skills/)

```
TASK: Build core/skills/adapter_onboard.skill.md. Read ADR-005, FR-DC-23, §6.6.3, and the
TASK-017 F1+3 drift note in CLAUDE.md. Given a domain's FROZEN vocabulary + profiles + sample
sources, PROPOSE the adapter pack by guided conversation: show the fixed frame (engine +
code_pipeline -> code_map_build), design the variable docs_pipeline, and DERIVE each skill's
`emits` from the vocabulary's emitted_by so adapter.yaml cannot drift from the vocab by
construction (this kills the F1+3 drift class). Bulk + incremental modes. Propose, never bless;
authors only the domain pack skills, never core/skills/ content.
First: promote the domain-agnostic pdf_extract into core/skills/ (it must exist before the pack).
VERIFY: given a frozen 2nd-domain vocab+profiles -> a proposed adapter.yaml whose emits == the
vocab's emitted_by (zero drift); §10.5 no-drift green; pdf_extract now in core/skills/; 5 green.
NOTE: depends on TASK-070+071. Tighten once those are in hand.
```

## TASK-073 — Domain-onboarding orchestrator (`onboard.py` + `ONBOARD_INPUT.yaml`)

```
TASK: Build core/scripts/onboard.py + ONBOARD_INPUT.yaml. Read the onboard.py design block in
TASK_LIST.md (Milestone 5B), plus §6.6.1, §10, and Appendix B (consume-pull vs author-pull).
ONBOARD_INPUT.yaml = a UI_INPUT-shaped envelope with a `mode` discriminator.
mode: onboard authors the registry, in this exact sequence:
  1. authoring pull: clone the registry into onboard_dir/ (scratch).
  2. run the four helpers IN ORDER with a HUMAN FREEZE GATE at each:
     extractor_onboard -> domain_onboard -> profile_onboard -> adapter_onboard.
  3. run python core/scripts/build_checks.py (§10) as a HARD GATE — RED => STOP, NO PUSH.
  4. git commit + push to Bitbucket; emit the new registry_sha (to thread into a mode: run).
mode: run consumes the registry (unchanged — that's the existing path).
The push here is a BUILD-TIME developer git action, NOT a runtime agent mutation (distinct from
the Jira push). Registry stays human-frozen + SHA-pinned. Distinct from hydrate.py (consume pull).
VERIFY: onboard a synthetic 2nd domain against a local bare-git registry -> §10 green -> push ->
registry_sha emitted; force a §10 RED and confirm NO push happens.
NOTE: depends on all four helpers (069–072) existing. Tighten once they're in hand.
```

## TASK-074 — Multi-domain enablement (`domains_index.yaml` + UI)

```
TASK: Make the system multi-domain. Read FR-BR-11/14, FR-XS-21, D2, and the UI DOMAINS list in
app/frontend/src/PDLCConfigurator.jsx.
1) Add domains_index.yaml listing the registered domains.
2) Drive the UI domain dropdown from domains_index.yaml instead of the hardcoded payment_brand.
   Generate hydrates the chosen domain (domain-pruned, as today).
VERIFY: a 2-domain index -> the UI offers both -> Generate prunes correctly to the chosen domain;
payment_brand runs are unaffected; build_checks 5 green. PUBLISH after green.
NOTE: needs a real 2nd domain authored (TASK-073).
```

## TASK-075 — `vocab_gap_assess` + amendment loop

```
TASK: Build the model half of vocabulary adequacy. Read ADR-003, FR-DC-21, and the in-slice L1
detector (TASK-013: untagged_ratio -> VOCAB_GAP_FLAG). Create core/skills/vocab_gap_assess.skill.md:
a BOUNDED model pass over the NEWLY-INTRODUCED untagged delta that proposes a candidate tag +
evidence; then a human-gated AMENDMENT -> vocab_sha bump -> re-tag pass. Propose, never auto-mutate.
VERIFY: a synthetic untagged delta -> a proposed tag + evidence artifact; the human-gated amendment
bumps vocab_sha and re-tags; build_checks 5 green.
NOTE: real value is on the VDI corpus (synthetic fixtures fit the 12 tags).
```

## TASK-076 — Metrics store + dashboard (SQLite)

```
TASK: Promote the JSONL ledger to a queryable SQLite store + a metrics dashboard, ADDITIVELY —
the JSONL ledger stays the source of truth (D8). Read FR-MX-* and the ledger/metrics_scan code.
VERIFY: ingest a run's ledger -> events queryable in SQLite + the dashboard renders the run's
metrics; the JSONL ledger is unchanged; build_checks 5 green.
```

## TASK-077 — Auto-launch

```
TASK: Automate the manual start gesture (open the tool + run start-brd) where the environment
permits — Claude-only convenience first. Read FR-XS-25 and the overlays' launch.md. The manual
two-step path must still work. VERIFY: Generate -> the run starts without the manual step where
allowed; the manual path is unaffected.
```

## TASK-078 — UI enhancements (role gating + telemetry surface)

```
TASK: Add role gating to the configurator + a richer live telemetry/metrics surface (live run
status + G-gate results) driven from GET /runs/{id}/status. Read the role-gating FRs and the
status endpoint. VERIFY: roles gate the relevant actions; the UI surfaces live ledger status for a
run; build_checks 5 green.
```

---

> When a task fights you, bring the failing **proof** or **build-check** output (or a screenshot)
> back to the external Claude Code session and we'll debug. For the interdependent onboarding tasks
> (070–073), ping me to tighten the prompt once the prior task's output exists.
