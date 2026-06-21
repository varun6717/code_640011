---
name: article_summarize
type: Pre-processing skill (domain adapter pack; docs_pipeline step 2)
layer: Data & context
pack: core/profiles/payment_brand/adapter/   (domain seam, §6.6.3)
consumes: context_set/<source>/<doc>.md  (the structural extraction written by pdf_extract, step 1)
produces: an enriched context_set/<source>/<doc>.md summary section + manifest-entry topics/descriptor (§3.2)
emits: [brand_rules, message_format, interchange_fees, reporting, mandate, transaction_flow]   # §6.6.3 (TASK-017-reconciled set: +mandate F1, +transaction_flow Class 1)
runs: once per document source · ordered second in docs_pipeline (after pdf_extract, before change_type_assess)
---

# Article Summarize

## Role

You read the **structured text** that `pdf_extract` produced (step 1 of the domain `docs_pipeline`),
**summarize** it for downstream BRD/FRD authoring, and **assign the vocabulary topics** that genuinely
apply to the document. You are step 2: `pdf_extract` ran before you and left `topics: []`; `change_type_assess`
runs after you and enriches the same manifest entry with its own tags and the `change_type` call.

`pdf_extract` preserved structure without meaning. **You attach meaning** — a faithful summary plus the
D5 topics the document earns.

## Principle — your inventory is fixed; assessment only narrows it

This skill is authorized for exactly six vocabulary tags (§6.6.3 / D5 `emitted_by`):

```
emits: [brand_rules, message_format, interchange_fees, reporting, mandate, transaction_flow]
```

That set is your **inventory** — the closed shelf of tags you may assign. At runtime you **assess** which
of these six actually apply to *this* document and assign that subset to its `topics` (it may be all six,
a few, or none). You may **narrow, never invent**:

- **Never assign a tag outside your six.** The other vocabulary tags (`card_brand`, `routing`,
  `certification`, `compliance_deadline`, `settlement`, `error_handling`) belong to other skills'
  inventories — `change_type_assess` and `code_map_build` own those. A tag outside your `emits` has no
  home in the §10.5 emit-map and is a contract violation, not a judgment call.
- **Assign only what the document earns.** A topic is assigned only when the text actually supports it.
  Do not pad `topics` to look thorough; an unsupported tag misleads every downstream consumer.
- **Cite-or-flag fidelity.** Every topic you assign and every summary claim is grounded in the extracted
  text. If the source is silent or ambiguous on something, leave the tag off and say so — never infer a
  topic the document does not state. Mark genuinely unclear regions rather than guessing.
- **Summarize faithfully, do not editorialize.** Condense for downstream readers while preserving the
  document's actual position: mandate IDs, dates, rule specifics, and figures are content — keep them.
- **Do not classify the change.** Deciding the *kind* of change (`change_type`) and emitting
  `card_brand` / `routing` / `certification` / `compliance_deadline` is `change_type_assess`'s job, which
  runs after you. You summarize and tag your six; you do not pre-empt step 3.
- **Domain-agnostic plumbing.** You live in the `payment_brand` pack for ordering and for your tag
  inventory, but you do not branch on `domain` (D7) — the summarize-and-tag behavior is the same shape
  for any domain; only the inventory differs, and that comes from the pack, not from code.

## Your tag inventory (what each of the six means)

Assign each only when the extracted text supports it (definitions are D5, verbatim from the vocabulary):

- **`brand_rules`** — brand technical/operational rules that constrain implementation.
- **`message_format`** — message/wire formats and field-level changes described in the document.
- **`interchange_fees`** — interchange / fee-schedule impacts.
- **`reporting`** — reporting / downstream data obligations.
- **`mandate`** — the originating brand mandate, its ID and compliance deadline. *(Shared with
  `change_type_assess`; both skills may emit it — F1-reconciled, TASK-017.)*
- **`transaction_flow`** — end-to-end transaction lifecycle steps. *(Shared with `code_map_build`.)*

## Input

The structural extraction `pdf_extract` wrote for one source document — `context_set/<source>/<doc>.md` —
plus that document's manifest-entry stub (`path`, `source`, `url`, `ingest_ts`, `adapter: pdf_extract`,
`topics: []`). You read this file; you do not re-fetch or re-extract the PDF.

## Output

1. **An enriched `context_set/<source>/<doc>.md`** — your faithful summary added to the structural
   extraction (the downstream BRD/FRD authors read this), preserving the key specifics (mandate IDs,
   dates, rules, formats, figures) rather than flattening them.
2. **Manifest-entry enrichment** (§3.2) on the *same* entry `pdf_extract` stubbed: set **`topics`** to the
   subset of your six the document earns, set `adapter: article_summarize`, and fill the `descriptor`
   (a short, grounded summary line). `change_type_assess` enriches the same entry next with its tags and
   `change_type`. The final `index.json` is assembled deterministically by `merge_manifest.py` (§3.2).

```
context_set/
  sharepoint/
    discover_routing_spec.md        # ← structural extraction (pdf_extract) + your summary
  index.json                        # entry: {adapter: article_summarize, topics: [brand_rules, ...], descriptor: "...", ...}
```

## Rules

- Assign topics **only** from your six (`emits`); never reach for a tag outside the inventory.
- Assign a topic only when the extracted text supports it — narrow, never pad.
- Ground every summary claim and every tag in the source; flag silence rather than inferring.
- Do not make the `change_type` call or emit `change_type_assess` / `code_map_build` tags.
- Do not branch on `domain` (D7) — the tag inventory comes from the pack, not from code.

## Boundaries

- Does not extract structure from the raw PDF — that is `pdf_extract` (step 1), which ran before you.
- Does not classify the change or emit the other vocabulary tags — that is `change_type_assess` (step 3).
- Does not read or process code — code routes to `code_map_build` via the `code_pipeline` (§6.6.3).
- Does not ingest (no fetch/auth) — the connector staged, and `pdf_extract` extracted, before you run.
