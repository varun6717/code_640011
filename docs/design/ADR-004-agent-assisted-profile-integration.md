# ADR-004 — Agent-assisted profile integration: routing a new tag into a profile section (gate 3, propose-never-bless)

**Status:** **Accepted** — ruled by operator **V**, 2026-06-20. Deferred (W); named now, built at the port / second domain. No in-slice build, no pinned-contract change.
**Amends:** `REQUIREMENTS.md` (new `FR-DC-22` W, in the FR-DC cluster beside FR-DC-19/20/21); `TECH_SPEC.md` §6.6.1 (forward-compat note — the agent-assisted profile aid respects build-time registration); `TASK_LIST.md` (Phase 5 named follow-on). No change to any normative schema (D1/D3a already admit a new `requirements[]` entry additively), no reserved hook, no Python.

---

## Context

The adaptive-dictionary story (ADR-003) has three steps, but only two have an authoring aid:

| gate | act | aid | status |
|------|-----|-----|--------|
| 1. **detect** | name a recurring uncovered concept (`VOCAB_GAP_FLAG`) | L1 detector | **built** (TASK-013) |
| 2. **name a tag** | concept → candidate tag (name, definition, `emitted_by`, `code_tag`) | `vocab_gap_assess` / `domain_onboard` | named, deferred (FR-DC-20/21) |
| 3. **route into a profile** | add `requirements[].topic` to a section so a BRD/FRD consumes it | **— none —** | **manual** |

The gap: a tag that reaches the vocabulary but **no profile section** is *taggable but unconsumed*. It is stamped onto artifacts (`code_map` tags / `index` topics), it stops tripping the adequacy detector — but because no `requirements[].topic` references it, **no BRD/FRD section ever surfaces it**. The detect→name chain is then wasted: the concept was recognized and even tagged, yet it never reaches an output artifact. So gate 3 is **necessary** for a grown vocabulary to matter — and it is the one seam with no propose-not-bless helper. Today, and in the deferred design as written, routing a new tag into a profile is a manual human edit.

This is a real asymmetry, not a deliberate omission: the extractor has `extractor_onboard` (FR-DC-19), the vocabulary has `domain_onboard` (FR-DC-20), the profile has nothing.

## Decision

Name a deferred, human-gated skill — working name **`profile_onboard`** — that closes gate 3 by **proposing**, never deciding. Given an approved tag with no consuming section, it:

1. **Surfaces** the unconsumed tag to the operator — the existing `FR-BR-08` *surface → wait → apply* human-mediated flag loop, applied to the dictionary→profile seam ("`tokenization` is approved but no section consumes it — integrate into the profile?").
2. **Proposes** a target section `id` + drafted `must_capture` / `probe_if_missing` (+ `required`). The `sources` follow deterministically from the tag's `emitted_by` (doc-emitted → `[confluence, sharepoint]`; code-emitted → `[bitbucket]`); for the FRD profile it also proposes `functional_kind` + `traces_to` (D3a). The section choice is a **reasoned suggestion** from the tag's nature, not a unilateral decision.
3. On approval, emits a **reviewable profile diff** for a human to edit, approve, and commit.

The mechanical half (section routing from `emitted_by`/`consumed_by`-style reasoning, `sources` derivation) is nearly deterministic; the discretionary half (`must_capture`/`probe_if_missing` wording — the Opus-grade authoring of TASK-015) is the model **proposal**.

## The invariant — why the human gate is structural, not ceremony

The profile is a **build-time, SHA-pinned, human-frozen seam artifact** (§6.6.1: *registration is build-time, human-authored, build-checked, SHA-pinned — never invented by the agent at runtime*). So `profile_onboard` MUST NOT:

- **decide** the section (it proposes; a human confirms/edits),
- **author** the final `must_capture` (it drafts; a human owns the wording),
- **mutate** the live profile (it emits a diff; the change lands as a **committed, re-pinned, build-time amendment**, never a runtime write).

This is the same propose-never-bless governance that FR-DC-19 applies to the extractor and FR-DC-20 to the vocabulary — now applied to the third frozen artifact. The agent raises a hand and drafts; a human owns the contract.

## Rationale

- **Completes the chain.** Detect (FR-DC-21) and name-a-tag (FR-DC-20/21) are wasted without gate 3; this makes a grown vocabulary actually reach output.
- **Pattern-consistent.** The surface→wait→apply loop already exists (FR-BR-08); `profile_onboard` reuses it rather than inventing a new interaction.
- **Decoupling is intentional.** "Is this a real concept worth a tag?" (gate 2) and "should every future BRD be *forced* to address it?" (gate 3) are different editorial judgments — keeping them separate gates lets the dictionary grow without bloating the BRD structure, and only a deliberate human decision adds a required topic.
- **Additive, cheap to defer.** The D1/D3a profile schema already admits a new `requirements[]` entry; no reserved hook or schema reshape is needed now, so naming it costs nothing and building it later is purely additive.

## Consequences

- **No in-slice change.** Nothing is built; no committed code, no schema edit, no reserved field. The single domain's profiles stay hand-authored (TASK-015/016), and there is no tag to integrate while `payment_brand`'s vocabulary is frozen by D5.
- **First exercise** is alongside `domain_onboard` / the FR-DC-21 amendment loop — a new domain, or the real-corpus vocabulary growth at the port.
- **Scope discipline.** This ADR records a design decision (a `W`-level FR) and reserves a name; it does not reopen D1–D10, change a pinned schema, or pull work into the slice. It is the profile-side sibling of ADR-003's vocabulary story.
