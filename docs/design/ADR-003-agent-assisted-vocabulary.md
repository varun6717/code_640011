# ADR-003 — Agent-assisted domain vocabulary: onboarding proposal + every-run adequacy check (propose, never bless)

**Status:** **Accepted** — ruled by operator **V**, 2026-06-20 (option **A**: forward-compat hook now + L1 deterministic detector in-slice + L2 deferred to port + L3 Phase 5).
**Amends:** `REQUIREMENTS.md` (new `FR-DC-20` W / `FR-DC-21` S; a forward-compat **note** on D5); `TECH_SPEC.md` §3.6 (`vocab_gap_flag` record), §5.2 (`onboarding_manifest` gains `built_with_vocab_sha` + `adequacy_threshold`), §5.3 (`vocab_sha` added to the cache key), §5.4 (the L1 adequacy detector, normative), §5.5 (purpose-before-tags split; `tags:[]` feeds adequacy), §10 (adequacy is a **runtime flag**, not a build gate); `TASK_LIST.md` (TASK-012/013 absorb the hook + L1; Phase 5 gains L2/L3); `code_map_build.skill.md`.
**Does not reopen:** D1–D10. D5's **12 tags stay frozen**; a vocabulary *amendment* is a human-gated **addition**, never a silent redefinition. Architectural invariants intact: deterministic/frozen extractor, model-free 3-branch gate, model owns `purpose`+`tags` only, deterministic `merge_edges`, and the §10.1/§10.5 **containment** check is unchanged. This ADR adds a complementary *adequacy* check; it does not weaken containment.
**Sibling of:** `FR-DC-19` (`extractor_onboard`). Same governance shape — an agent **proposes** a frozen artifact, a human **freezes/commits**; the skill must never self-bless. This ADR is that pattern applied to the **vocabulary** instead of the extractor.

---

## Context

The domain tag vocabulary (D5) is the contract three things route on: adapter `emits`, `code_map` `tags`, and BRD/FRD profile `topics`. It is **per-domain and frozen**, authored once and SHA-pinned.

Today exactly **one direction** of vocabulary checking exists:

- **Containment (§10.1/§10.5, TASK-046)** — *usage ⊆ dictionary.* Every topic/emit/tag must already be in the vocabulary. This catches **invention/drift** (a tag escaping the dictionary) and is a **build-time hard gate**.

The **other direction does not exist**:

- **Adequacy** — *does the dictionary cover the concepts actually present in the artifacts?* This catches the vocabulary being **too small** for the real corpus.

Two forces make the dictionary outgrow itself, and **neither shows up in this external build** because the synthetic fixtures were authored to fit the 12 tags:

1. **A much larger real codebase** (the VDI Stratus repo) contains modules whose concepts the 12 tags do not name.
2. **A new PDF/article** introduces a concept no existing tag covers.

In both cases the model **cannot invent a tag** (`assert tags ⊆ vocabulary` forbids it), so the affected file/doc comes out `tags: []`. That is *honest* but **silent**: an untagged file is found by no section's selective read, and nothing fails. The gap is invisible until someone notices a requirement that should have had code behind it didn't. We want that silent gap turned into a **visible, trending, human-actionable signal** — and we want it designed **before the port**, since the port is where the gap first becomes real.

A second, related need: a **new (second) domain** has no D5 decision at all — its vocabulary must be authored from scratch. An agent that has read the domain's sample artifacts can **propose** that first vocabulary far faster than a blank-file start.

## Decision

Add **two human-gated, agent-assisted capabilities**, sharing one principle — **propose, never bless.**

### 1. `domain_onboard` — propose a vocabulary for a *new* domain (FR-DC-20, W)

At new-domain onboarding, before any run, a deferred skill proposes `vocabulary.<domain>.yaml` from:

- the **untagged code_map** of a sample repo — structure (`path/module/interfaces/depends_on`) **plus `purpose`**, but **not** `tags` (circular);
- **sample documents** for the domain;
- the operator's **domain framing**.

Output is a **reviewable proposal** — for each candidate tag `{name, definition, emitted_by, code_tag?, evidence:[files/docs]}` — that a **human edits, approves, and freezes**. It never commits the file.

This requires one mechanical refinement to enrichment: **split `model_enrich` into a purpose-first pass and a tags-last pass.** `purpose` is vocabulary-independent and may be computed before the vocabulary exists (it feeds the proposal); `tags` stays last, consuming the frozen result. In a normal run the two run back-to-back exactly as today — the split only matters during onboarding.

### 2. Every-run vocabulary **adequacy** check + amendment loop (FR-DC-21, W)

This is the vocabulary twin of the coverage floor: a deterministic trigger that raises a **human-gated** flag. Direction reminder: `untagged_ratio = untagged ÷ total`, so a **high** ratio is the bad one.

```
on each run (reusing the gate's existing new/changed signal — §5.3 commit_sha/git_diff; doc source-idempotency):

  # ---- always, cheap, model-free ----
  untagged_ratio(code) = files with tags:[]      / total files        # CODE arm
  untagged_ratio(docs) = manifest entries no-topic / total entries    # DOC  arm
  emit both to telemetry every run                                    # continuous trend, never blind

  new_untagged = { NEWLY-INTRODUCED untagged files/docs }             # the delta only, from the gate

  # ---- TRIGGER 1 (delta): a single new concept is never missed ----
  if new_untagged non-empty:
      vocab_gap_assess(new_untagged)        # BOUNDED model pass over the delta ONLY (never re-chews
                                            #   unchanged files); proposes a tag ONLY if it finds a real,
                                            #   recurring, nameable concept — an isolated legitimately-
                                            #   untaggable file (utility/vendor) yields no proposal.

  # ---- TRIGGER 2 (corpus): systematic inadequacy ("thousand cuts") ----
  if untagged_ratio(code) > T or untagged_ratio(docs) > T:
      raise VOCAB_GAP_FLAG into decisions.jsonl   # louder; the dictionary is systematically too small

  # ---- human-gated amendment (either trigger) ----
  human reviews the proposal → if accepted:
      add tag(s) to vocabulary.<domain>.yaml      # an ADDITION; D5 set never silently redefined
      bump vocab_sha (versioned)
      re-tag pass: only the TAG pass re-runs (structure/purpose untouched); a vocab_sha change
                   invalidates affected code_maps via the gate cache key, exactly as a re-blessed
                   extractor_sha does (§5.3 Branch B guard).
```

**Two triggers, OR'd, because each catches what the other misses.** The corpus ratio alone would miss a *single* new file carrying a genuine new concept (one file barely moves an aggregate); firing on *every* new untagged file alone would spam proposals for legitimately-untaggable utility files. Delta-scoping the model pass + a corpus threshold gives "never miss a real single concept" without "re-diagnose the whole repo every run."

## The invariant — why the human gate is structural, not ceremony

The same model that **assigns** tags at runtime (and routes sections on them) is the one that would **propose** new tags. If it could also silently **add** the tags it wished it had, the vocabulary stops being an external contract and `assert tags ⊆ vocabulary` becomes the model grading its own homework — it could never be "wrong." The human-freeze gate is the **only** thing that keeps the dictionary an independent contract. Hence: agent **proposes**, human **disposes**, build checks **enforce** — identical to FR-DC-19's freeze discipline.

And the two checks stay distinct in *kind*:

| Check | Direction | Enforcement | Failure mode it catches |
|---|---|---|---|
| **Containment** (exists, §10.1/§10.5) | usage ⊆ dictionary | **build-time hard gate** | a tag *escaping* the dictionary (drift/invention) |
| **Adequacy** (this ADR) | corpus → dictionary | **runtime flag** (never hard-fails a run) | the dictionary being *too small* (silent `tags:[]`) |

Adequacy must **not** become a hard gate — a run with some untagged files is valid and proceeds; the flag is advisory input to a human, recorded in `decisions.jsonl`.

## Rationale

1. **The gap is otherwise silent.** Without adequacy, an undersized vocabulary degrades to `tags:[]` that no section finds and no check fails. This converts that into a trending, actionable signal.
2. **Reuses existing machinery — no new change detection.** Code uses the gate's `commit_sha`/`git_diff_names`; docs use per-source idempotency (D8b). The only additions are a **count** (`untagged_ratio`) and a **gated, delta-scoped model pass**.
3. **It parallels `REONBOARD_FLAG` exactly.** Deterministic trigger (coverage floor / untagged ratio) → human-gated frozen-artifact change (onboard an extractor / amend the vocabulary). The system already accepts this shape for the extractor; this applies it to the dictionary.
4. **Determinism + freeze intact.** The ratio is model-free; the model only *proposes*; the human *freezes*; the extractor and the gate are untouched.
5. **Forward-compat hook reserved now, like FR-DC-13 reserved `external_calls`/`exposes`.** Adding `vocab_sha` to the onboarding manifest + gate cache key **now** (cheap) means a future amendment invalidates affected maps without a key reshape later. Naming the loop now keeps it additive.
6. **Sibling governance to FR-DC-19.** One coherent "propose-not-bless onboarding" story for both frozen artifacts (extractor, vocabulary).

## Consequences

### Already-built work (TASK-008/009/010/011): **no code change required.**
- `model_enrich` already emits `tags:[]` for files with no in-vocabulary concept — that *is* the adequacy signal; nothing to add to it.
- `load_domain_vocabulary` already **abstracts the source** of the set; the producer (proposal) and consumer (`apply_enrichment`/`assert_tags_in_vocabulary`) are cleanly separated, so a proposal capability is purely additive.
- The `merge_edges` closure and the C extractor are untouched.
- **Only future, optional touch:** `load_domain_vocabulary` may later also return a `vocab_sha` (a one-line addition) once versioning lands. Not needed until the amendment loop is built.

### The timing split ruled by V (option A)

**Hook — now (TASK-012/013, forward-compat plumbing, behavior-free).** Reserve `built_with_vocab_sha` in `onboarding_manifest.yaml` (TASK-012) and add it to the gate's Branch-B cache key (TASK-013), constant for the single frozen domain — exactly the `external_calls`/`exposes` reservation pattern (FR-DC-13). A future vocabulary amendment then invalidates affected maps (→ re-tag) without a later key reshape.

**L1 deterministic detector — in this slice (folded into TASK-013).** The adequacy detector is the model-free twin of the coverage floor (`REONBOARD_FLAG`), which is already MVP — so it belongs in the same task. It needs **no model and no vocabulary** to run: it counts `code_map` entries with `tags == []` (and, when the doc manifest exists, entries with no topics), computes `untagged_ratio`, and raises `VOCAB_GAP_FLAG` when the ratio exceeds `adequacy_threshold`. Testable now against `fixtures/c_repo` (≈0.06 → no flag) plus a crafted high-untagged variant (flag fires) — the same proof shape as `assert_tags_in_vocabulary`. New code: a small deterministic helper (e.g. `core/scripts/checks/vocab_adequacy.py`) invoked from the gate's post-build path beside `check_coverage`.

**L2 model diagnosis + amendment loop — deferred to the port (Phase 5 / port-time).** `vocab_gap_assess` (the gated model pass over the new-untagged delta), the human-gated `vocab_sha` amendment, and the re-tag pass. The model-judgment half cannot be meaningfully validated against synthetic fixtures that were authored to fit the 12 tags; its first real exercise is the VDI corpus. Named now, built at the port.

**L3 `domain_onboard` — Phase 5 (named not built).** `core/skills/domain_onboard.skill.md` — propose a *new* domain's vocabulary from the untagged map + sample docs. Cannot be exercised until domain #2 exists (`payment_brand`'s vocabulary is frozen by D5). Mirrors how FR-DC-19's `extractor_onboard` is named-not-built.

### Spec/ledger touch-points (on Accept)
- **§3.4 / §8.1:** an adequacy telemetry event (`untagged_ratio` for code + docs), so the trend is observable; no metric hand-entered.
- **§3.6:** a `vocab_gap_flag` decision record (who/when/ratio/threshold/decision), alongside `reonboard_flag`.
- **§5.4:** an `adequacy_threshold` named beside the coverage floor.
- **§5.5:** note the purpose-first/tags-last split and that `tags:[]` feeds the adequacy ratio.
- **§10:** state that adequacy is a **runtime flag**, not a build gate; containment stays the build gate.
- **`vocabulary.<domain>.yaml`:** gains an additive `vocab_sha`/version header.
- **REQUIREMENTS.md:** `FR-DC-20`/`FR-DC-21` (Watcher) in the deferred area near FR-DC-19; a forward-compat **note** on D5 that the frozen set may be **extended** via this human-gated loop (the existing 12 are not changed).

### Scope discipline
- `payment_brand` is unaffected operationally: its vocabulary was frozen by D5, so a real run exercises only the *application* path; on `fixtures/c_repo` the adequacy detector reads low (≈0.06) and raises nothing. The **L1 detector ships in-slice** (it is the coverage-floor twin and is testable here); the **L2 diagnosis/amendment loop** earns its cost at the **first real (VDI) corpus**; **L3 `domain_onboard`** earns its cost at the **second domain**. Pulling L1 in is a small, deliberate, operator-ruled expansion of the MVP "single domain" note — justified because the detector is the exact model-free analog of a signal the MVP already builds (the coverage floor), and because the gap it catches first appears at the port.
