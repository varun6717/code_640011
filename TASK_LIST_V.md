# TASK_LIST_V.md — VDI bring-up (get the self-serve run working on the JPMC VDI)

**What this is.** The external build (`TASK_LIST.md`) is validated; every 5A connector + seam is
proven **offline**. This list is the **port**: the steps that turn "proven offline" into "running
on the VDI." The *mechanism* does not change here — only the things that are environment-specific:
where secrets come from, which Bitbucket/SharePoint hosts, and the runtime tool. Models come from
the runtime tool itself (Copilot + Claude Code) — there is **no separate model backend** to wire.

**How to read it.** Same shape as `TASK_LIST.md`: each task has **Depends / Reads / Do /
Acceptance / Proof**. Tick the box when all acceptance conditions are true. Disk + git are ground
truth. Nothing here reopens a pinned contract (D1–D10) or a 5A design — it only binds endpoints.

**The split that matters (read first).** Two different git-auth paths exist by design:
- **Registry** (`publish_registry.py` push + `hydrate.py`/`generate.py` pull) uses **ambient git
  transport** — configure a git credential helper with the HTTP access token (V-03a).
- **Code source** (`clone.py`) uses the **auth seam** — `PDLC_AUTH_BITBUCKET` (or the JPMC
  secret-store backend) via `jpmc_adapters.auth` (V-03b).
- **SharePoint** (`ingest_sharepoint.py`) uses the **auth seam** for the Bearer token (V-07).

---

## Phase V0 — Environment bring-up (the control plane)

- [ ] **V-00 — Place the PDLC repo + Python env on the VDI**
  - **Depends on:** the PDLC repo (app/ + core/ — the control plane).
  - **Reads:** `docs/ENV_PRECHECK.md` (tree-sitter via venv, ADR-001); `app/backend/requirements.txt`.
  - **Do:** Clone/copy the PDLC repo onto the VDI. Create `.venv`; `pip install -r app/backend/requirements.txt` + `tree-sitter==0.25.2 tree-sitter-c==0.24.2`. Install Node for `app/frontend` (`npm install`).
  - **Acceptance:** `.venv/bin/python core/scripts/build_checks.py` → all 5 §10 checks green; `import tree_sitter, tree_sitter_c` succeed in the venv; frontend builds.
  - **Proof:** build-checks output green; `verify_*` offline proofs still pass on the VDI.

- [ ] **V-01 — Runtime tool in VS Code (the executor + the model)**
  - **Depends on:** V-00.
  - **Reads:** `overlays/<tool>/launch.md`; `overlays/copilot/VDI_PREREQUISITES.md`; `docs/COPILOT_VDI_VALIDATION.md`.
  - **Do:** Install/enable the runtime tool — **GitHub Copilot agent mode** and/or **Claude Code**. The tool supplies the model directly (no Bedrock/env wiring). For Copilot, set the terminal command **allow-list at USER scope** (`github.copilot.chat.agent.terminal.allowList`) — provisioned centrally, never in the scaffold.
  - **Acceptance:** the tool loads custom agents/skills and can run a terminal command without per-command approval stalls (COPILOT_VDI_VALIDATION Checks 1–3 PASS); a model response returns from the tool.
  - **Proof:** the validation runbook outcome recorded (PASS / PARTIAL-tuned).

---

## Phase V1 — Bitbucket repos + auth binding

- [ ] **V-02 — Create the two Bitbucket repos + an HTTP access token**
  - **Depends on:** access to the VDI (JPMC Data Center) Bitbucket.
  - **Reads:** `docs/TECH_SPEC.md` §2.1 (registry), §6.6.2 (code source).
  - **Do:** Create **repo #1 (registry)** and **repo #2 (code)**. Mint an **HTTP access token** with repository **read+write** (write needed to publish the registry + push the code).
  - **Acceptance:** both repo URLs resolve; the token authenticates a manual `git ls-remote`.
  - **Proof:** `git ls-remote <each repo>` succeeds with the token.

- [ ] **V-03a — Ambient git auth for the registry path**
  - **Depends on:** V-02.
  - **Reads:** `core/scripts/publish_registry.py`, `core/scripts/hydrate.py` (both use ambient git).
  - **Do:** Configure a git **credential helper** (or token-in-store) so plain `git clone`/`push` to the registry repo authenticates non-interactively with the HTTP access token.
  - **Acceptance:** `git clone <registry-url>` works without prompting; no token on disk in plaintext beyond the OS credential store.
  - **Proof:** a non-interactive clone of the (empty) registry repo.

- [ ] **V-03b — Bind the auth seam to the VDI secret (code + SharePoint)**
  - **Depends on:** V-02; `jpmc_adapters/auth.py` (TASK-052).
  - **Reads:** `docs/TECH_SPEC.md` §7; `core/adapters/jpmc_adapters/auth.py`.
  - **Do:** Make `resolve_auth("jpmc_adapters:bitbucket"|":sharepoint")` return the real token — either set `PDLC_AUTH_BITBUCKET`/`PDLC_AUTH_SHAREPOINT` (+ `_USER`) from the HTTP access token, **or** implement a JPMC secret-store `SecretBackend` and install it via `set_backend()`. Same `auth_ref`; only the backend differs.
  - **Acceptance:** `resolve_auth` returns a usable handle per service; a missing secret fails loud (named); no secret reaches workspace/ledger/artifacts.
  - **Proof:** `fixtures/auth/verify_auth.py` passes on the VDI with the real backend swapped in.

---

## Phase V2 — Registry live (publish → verified pull)

- [ ] **V-04 — Publish the registry to Bitbucket (repo #1)**
  - **Depends on:** V-00, V-03a.
  - **Reads:** `core/scripts/publish_registry.py`; `core/registry_manifest.yaml`.
  - **Do:** `python core/scripts/publish_registry.py <vdi-registry-url>` — the §10 gate runs, the 88-file subset is pushed, and a `registry_sha` is printed. (Or `--stage registry_repo` then push manually.)
  - **Acceptance:** push succeeds only with green build checks; the printed `registry_sha` is the repo's HEAD; the published tree has `core/` + `overlays/` at the root.
  - **Proof:** the live push log + `git -C <clone> rev-parse HEAD == registry_sha`.

- [ ] **V-05 — Verified hydrate from the live registry**
  - **Depends on:** V-04.
  - **Reads:** `docs/TECH_SPEC.md` Appendix B; `core/scripts/hydrate.py`, `generate.py`.
  - **Do:** Hydrate a scaffold from the Bitbucket registry at the pinned SHA (`generate.py --registry <vdi-registry-url>` with `registry_sha` in `UI_INPUT.yaml`).
  - **Acceptance:** hydration takes the **verified** clone+checkout path (not the non-git convenience); `registry_sha_verified == registry_sha`.
  - **Proof:** the generate descriptor showing `registry_sha_verified` == the V-04 SHA.

---

## Phase V3 — Code source live

- [ ] **V-06 — Push the Stratus C code + live-clone it through the seam**
  - **Depends on:** V-03b; `core/scripts/clone.py` (TASK-054).
  - **Reads:** `docs/TECH_SPEC.md` §6.6.2, §7; `fixtures/code_clone/verify_clone.py`.
  - **Do:** `git push` the Stratus C repo into **repo #2**. Then clone it via `clone.py` with `auth_ref: jpmc_adapters:bitbucket` (HTTP-token transport via the `GIT_ASKPASS` seam) into `repo/`.
  - **Acceptance:** a real clone completes through the seam; `commit_sha` pinned + recorded; **no secret on disk** (descriptor/ledger carry the `auth_ref` pointer only); §10.4 stays green.
  - **Proof:** the clone descriptor with `commit_sha`; a grep of `repo/` + ledger shows no token.

---

## Phase V4 — SharePoint live (implement the one placeholder)

- [ ] **V-07 — Implement `_download_pdf` for the JPMC SharePoint tenant**
  - **Depends on:** V-03b; `core/scripts/ingest_sharepoint.py` (TASK-055).
  - **Reads:** `core/scripts/ingest_sharepoint.py` (the `[TBD — VDI]` block + the Graph example); `docs/TECH_SPEC.md` §6.6.2, §3.2.
  - **Do:** Implement the marked `_download_pdf(url, handle, target)` (or inject via `set_downloader`) with the tenant's Graph/REST fetch — `Authorization: Bearer handle.reveal()`, stream bytes to `target`. Grant the SharePoint scope to the token resolved at `jpmc_adapters:sharepoint`.
  - **Acceptance:** a real SharePoint URL stages the PDF and emits the **same descriptor shape** as `ingest_file.py`; downstream `pdf_extract → article_summarize → change_type_assess` unchanged; no domain branch; no secret on disk.
  - **Proof:** `fixtures/sharepoint/verify_sharepoint.py` passes with the real downloader; a live pull stages the actual PDF.

---

## Phase V5 — End-to-end self-serve acceptance (TASK-056, run on the VDI)

- [ ] **V-08 — Configure a run in the UI → Generate (G0)**
  - **Depends on:** V-05, V-06, V-07.
  - **Reads:** `docs/ACCEPTANCE.md` (the offline spine run); `TASK_LIST.md` TASK-056.
  - **Do:** In the React UI, configure: domain `payment_brand`; sources = the **SharePoint PDF** + the **Bitbucket code repo**; registry = the **Bitbucket registry URL** + the V-04 `registry_sha`; runtime tool. Click **Generate** → scaffold laid, stops at **G0**.
  - **Acceptance:** `UI_INPUT.yaml` carries the real URLs + pinned SHAs; the scaffold hydrates from the live registry; sources are reachable through the connectors + seam.
  - **Proof:** the G0 descriptor + the laid run workspace.

- [ ] **V-09 — Run the spine → accepted BRD + FRD**
  - **Depends on:** V-08.
  - **Reads:** the generated instruction file + `overlays/<tool>/launch.md`.
  - **Do:** Open the scaffold in VS Code; run the spine via the runtime tool (`/start-brd` → `/start-frd`). Sources pulled live; code mapped; BRD then FRD authored + gated.
  - **Acceptance:** BRD/FRD pass **G1/G2**; `build_checks.py` green; `metrics_scan.py` derives the run's metrics; the ledger records the run with the **actual** runtime tool.
  - **Proof:** `docs/ACCEPTANCE_5A.md` — the self-serve run log + artifact links (the milestone 5A done-marker).

---

## Phase V6 — Port-time reconciliations (do alongside; documented port notes)

- [ ] **V-10 — Reconcile the D5 `card_brand` / `message_format` `emitted_by` gap**
  - **Reads:** `CLAUDE.md` (resolved-flag port note); `docs/REQUIREMENTS.md` D5 table; `core/profiles/payment_brand/vocabulary.payment_brand.yaml` (already r2-fixed).
  - **Do:** Apply the r2 fix to the **D5 table in `REQUIREMENTS.md`** itself (the `vocabulary.yaml` fix is already in; D5 still carries the gap).
  - **Acceptance:** D5 table and `vocabulary.yaml` agree; §10.5 stays green.

- [ ] **V-11 — (Optional, 5B-carried) thread the real runtime tool through G1/G2 telemetry**
  - **Reads:** `TASK_LIST.md` Milestone 5B carried-fixes (a); `brd_validator.record_g1` / `frd_validator.record_g2`.
  - **Do:** Replace the hardcoded `tool="claude"` in the validators' telemetry `Emitter` with `UI_INPUT.runtime_tool`. (Not required to *run*; fixes ledger fidelity when the tool is Copilot.)
  - **Acceptance:** the acceptance ledger's envelopes carry the run's actual tool.

---

> ✅ **VDI bring-up done = V-09 green** (a fresh operator completes a live UI → Generate → tool →
> BRD/FRD run, logged in `docs/ACCEPTANCE_5A.md`). Only then is the port validated end-to-end.
