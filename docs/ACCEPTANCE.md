# ACCEPTANCE.md — spine end-to-end acceptance (TASK-049)

**Run:** `r-2026-06-17-001` · **domain:** `payment_brand` · **runtime_tool:** `copilot`
**Slice:** BRD → FRD only (no Jira). **Result: PASS.**

This is the end-to-end acceptance run for the external build: from the P0-locked
`UI_INPUT.yaml`, the full spine **Generate → G0 → ingestion → code_map → BRD/G1 → FRD/G2**
was exercised over the TASK-003 PDF mandate + the TASK-004 Stratus C repo, including the
human-mediated **flag loop (GF)** and one **G1 reopen → v2**. It closes the external build
(the VDI port is produced separately off this validated repo).

Reproduce: `python3 runs/r-2026-06-17-001/run_acceptance.py` (deterministic; rebuilds the
ledger and re-checks every gate + all five §10 build checks + metrics).

---

## Inputs (the locked run identity)

- **`UI_INPUT.yaml`** — `domain: payment_brand`, `runtime_tool: copilot`, `registry_sha: 7d2e9a1`,
  `gates.score_threshold: 85`; sources = one PDF (`type: file`, sharepoint provenance) + one
  code repo (`type: bitbucket`, `SEAL-12345`). [`runs/r-2026-06-17-001/UI_INPUT.yaml`]
- **PDF mandate (TASK-003):** Mastercard brand mandate **MCS-2026-R3** (Parts 1–2), ingested to
  `context_set/sharepoint/*.md` (manifest in `context_set/index.json`).
- **Repo (TASK-004):** `merchant-routing-svc` (SEAL-PBI-0001 @ `e94c70d`), mapped to
  `context_set/code_map.json` (coarse, 34 files).

## Stages

| Layer | Stage | Output | Telemetry |
|-------|-------|--------|-----------|
| L0 | **Generate → G0** | run workspace scaffolded; **stopped at G0** before run (FR-XS-09) | `run_started` |
| L1 | ingestion | `context_set/` doc slices + `index.json` (both mandate parts, code arm) | `ingest` stage |
| L1 | code_map | `context_set/code_map.json` (coarse, `tags ⊆ vocabulary`) | `code_map` stage |
| L2 | BRD authoring + `code_impact` | `BRD.md`; deep pass returns the scope-ripple flag | `brd_authoring`, `code_impact`, `model_call` |
| L2 | **GF flag loop** | operator brings settlement in scope (material) → scoped re-run | `flag_decision` + `decisions.jsonl` |
| L2 | **G1** | **v1 reopen → v2 accept** → `BRD.md` locked **v2** | `validation`, `gate_decision` ×2 |
| L3 | FRD authoring | `FRD.md` (`<!-- pinned_brd: v2 -->`), detailed code impact carried forward | `frd_authoring`, `model_call` |
| L3 | **G2** | accept → `FRD.md` pinned to BRD v2 | `validation`, `gate_decision` |

### G0 — scaffold checkpoint (D4, FR-XS-09)

`generate.py` laid the §2.2 workspace (instruction file `copilot-instructions.md`, 8 overlay
wrappers + 4 prompt files, domain-pruned `core/`, initialized ledger, empty `context_set/` +
`repo/`) and **stopped before any stage** — Generate and Run are deliberately two steps so the
scaffold + immutable `UI_INPUT.yaml` are inspectable at G0. `ran_workflow: false`, `checkpoint: G0`.

### GF — human-mediated flag loop (FR-BR-08/13, D6c, §9.5)

`code_impact`'s deep pass traced a real closure from source: `src/routing/brand_router.c` calls
`reconcile_txn()` on the settle path → `routing/brand_router → settlement/reconciler`. It returned
one `scope_ripple` flag (recommended `material`). The flag was **surfaced, not auto-applied**
(FR-BR-08); the operator decided **"include settlement in scope"**. Being material (D6c), it
triggered a BRD section revision **and** a `code_impact` re-run **scoped to the changed surface
only** (routing + settlement). Recorded as a `flag` in `decisions.jsonl` + a `flag_decision`
telemetry event.

### G1 — BRD soft-gate + reopen (§9.2, FR-XS-13/14, D4)

- **v1:** `brd_score = 100` but **not eligible** — the scope-ripple flag was still undispositioned,
  failing the absolute "all flags resolved" precondition (§9.2). Operator **reopened** → v2.
- **v2:** flag resolved in `decisions.jsonl`; every `required:true` topic satisfied & grounded;
  `topic_coverage = 1.0`, `citation_integrity = 1.0` → `brd_score = 100`, **eligible** → operator
  **accept** → `BRD.md` locked as **v2**.

The validator is a soft gate — it never auto-advanced; the operator supplied each outcome, and an
`accept` on the ineligible v1 would have been refused (D4 backstop).

### G2 — FRD soft-gate (§9.3, FR-FR-05)

`frd_score = 100` (`traceability = 1.0`, `testability = 1.0`); every FRD topic `traces_to` a real
BRD anchor; every BRD requirement is traced **or** marked out-of-scope
(`requirements.interchange_fees`, `constraints_assumptions.compliance_deadline` — pure
business/compliance facts with no system behavior). Behavioral kinds carry acceptance criteria;
the `nfr` (certification) carries a measurable MAC-L2 target. Accept → `FRD.md` pinned to **BRD v2**.

## Build checks (all five §10 — green)

`python3 core/scripts/build_checks.py` → **5/5 PASS**: §10.1 vocabulary containment, §10.2 overlay
parity, §10.3 domain artifacts, §10.4 connector coverage, §10.5 adapter coverage/no-drift (the F1
reconciliation holds — all 12 per-tag mappings match).

## Metrics (derived from the ledger alone — NFR-06, FR-MX-01)

`python3 core/scripts/metrics_scan.py runs/r-2026-06-17-001/ledger/telemetry.jsonl`

| Metric | Value |
|--------|-------|
| M01 $/BRD | 1.55 |
| M02 $/FRD | 0.58 |
| M03 avg completion score | 100.0 |
| M04 first-pass acceptance | 0.0 *(this run was reopened — correctly not first-pass)* |
| M05 docs/month | `{2026-06: 1}` |
| M06 BRD→FRD cycle (s) | 1920.0 |
| M07 latency p95 (ms) | 120000 |
| M09 / M10 / M11 (Jira) | `null` *(no Jira this slice)* |
| M08 upstream-change alerts | deferred (W) |

No metric is hand-entered; all derive from `telemetry.jsonl` (25 events).

## Acceptance conditions (all met)

- [x] Clean **`BRD.md` v2** passes **G1** (score ≥ 85 + every required topic satisfied + all flags resolved).
- [x] **`FRD.md`** pinned to BRD v2 passes **G2** (score ≥ 85 + full BRD→FRD traceability).
- [x] **Flag loop exercised** (one material `scope_ripple`, operator-decided, scoped re-run).
- [x] **One G1 reopen → vN+1** exercised (v1 reopen → v2 accept).
- [x] `build_checks.py` **green** (5/5).
- [x] Ledger lets `metrics_scan.py` **derive every run metric** (no hand entry); all three ledger files validate.
- [x] **No Jira artifacts produced** (out of slice).

## Artifacts

- `runs/r-2026-06-17-001/UI_INPUT.yaml` — locked run identity
- `runs/r-2026-06-17-001/context_set/index.json` · `code_map.json` — ingestion + code map
- `runs/r-2026-06-17-001/BRD.md` — accepted BRD **v2**
- `runs/r-2026-06-17-001/FRD.md` — FRD pinned to BRD **v2**
- `runs/r-2026-06-17-001/ledger/telemetry.jsonl` · `decisions.jsonl` · `run_state.json` — the run ledger
- `runs/r-2026-06-17-001/run_acceptance.py` — the deterministic driver (reproduces this run)

> **External build complete at TASK-049.** The VDI-port artifact (thin overlay + `port_check` +
> allow-list runbook) is produced separately, off this validated repo.
