---
name: change_type_assess
type: Pre-processing skill (domain adapter pack; docs_pipeline step 3)
layer: Data & context
pack: core/profiles/payment_brand/adapter/   (domain seam, §6.6.3)
consumes: context_set/<source>/<doc>.md  (structural extraction + article_summarize's summary) and its manifest entry
produces: the manifest entry's change_type classification + its own topics (§3.2)
emits: [mandate, card_brand, routing, certification, compliance_deadline]   # §6.6.3 / D5 emitted_by (unchanged by F1)
runs: once per document source · ordered third (last) in docs_pipeline (after pdf_extract, article_summarize)
---

# Change Type Assess

## Role

You are the **last** step of the domain `docs_pipeline`. You read the document `pdf_extract` structured
(step 1) and `article_summarize` summarized and tagged (step 2), then you make the two judgments only you
own: **classify the *kind* of change** the document represents (`change_type`) and **assign your five
vocabulary topics** — the brand/compliance-facing tags that drive BRD scope and constraints.

`article_summarize` attached the document's *subject-matter* topics. You attach the *change/decision*
topics and the `change_type` call. After you, the docs_pipeline is done and the entry is complete.

## Principle — your inventory is fixed; assessment only narrows it

This skill is authorized for exactly five vocabulary tags (§6.6.3 / D5 `emitted_by`):

```
emits: [mandate, card_brand, routing, certification, compliance_deadline]
```

That set is your **inventory** — the closed shelf you may assign from. At runtime you **assess** which of
these five actually apply to *this* document and assign that subset to its `topics` (all five, a few, or
none). You may **narrow, never invent**:

- **Never assign a tag outside your five.** `brand_rules`, `message_format`, `interchange_fees`,
  `reporting`, `transaction_flow` belong to `article_summarize`'s inventory; `settlement` /
  `error_handling` are code-side (`code_map_build`). A tag outside your `emits` has no home in the §10.5
  emit-map — it is a contract violation, not a judgment call.
- **Assign only what the document earns.** A topic (and the `change_type`) is assigned only when the text
  actually supports it. Do not pad `topics` or guess a `change_type` to look decisive.
- **Cite-or-flag fidelity.** Every tag and the `change_type` are grounded in the extracted text — a
  mandate ID, a named brand, a routing change, a certification clause, a stated date. If the document is
  silent or ambiguous, leave the tag off and say so; never infer a classification the document does not
  state.
- **Domain-agnostic plumbing.** You live in the `payment_brand` pack for ordering and for your tag
  inventory, but you do not branch on `domain` (D7) — classify-and-tag is the same shape for any domain;
  only the inventory differs, and that comes from the pack, not from code.

## The `change_type` call (yours alone)

You set the manifest entry's **`change_type`** — a short classification of what *kind* of change the
source describes (the §3.2 example is `"new"`). Base it strictly on the document: is it introducing
something new, modifying existing behavior, or retiring/deprecating it? Assign the value the text
supports; if the document does not make the kind of change clear, flag it rather than guessing. This is
the one field `article_summarize` deliberately left for you.

## Your tag inventory (what each of the five means)

Assign each only when the extracted text supports it (definitions are D5, verbatim from the vocabulary):

- **`mandate`** — the originating brand mandate, its ID and compliance deadline. *(Shared with
  `article_summarize`; both skills may emit it — F1-reconciled, TASK-017.)*
- **`card_brand`** — which card brand(s) the work concerns. *(Shared with code-side `code_map_build`.)*
- **`routing`** — transaction routing to brand handlers. *(Shared with code-side `code_map_build`.)*
- **`certification`** — brand certification / conformance requirements.
- **`compliance_deadline`** — the hard date(s) the work must meet.

## Input

The `context_set/<source>/<doc>.md` file (structural extraction + `article_summarize`'s summary) and its
manifest-entry — already carrying `pdf_extract`'s structural fields and `article_summarize`'s `topics`,
`descriptor`, and `adapter: article_summarize`. You read this; you do not re-fetch or re-extract.

## Output

**Manifest-entry enrichment** (§3.2) on the *same* entry the prior steps built — you do not create a new
file or a new entry:

1. set **`change_type`** to your classification of the document;
2. **add** the subset of your five tags the document earns to the entry's **`topics`** (union with the
   topics `article_summarize` already set — you extend, you do not overwrite);
3. set **`adapter: change_type_assess`** to record the last skill that touched the entry.

The final `index.json` is assembled deterministically by `merge_manifest.py` (§3.2).

```
context_set/
  confluence/
    discover_mandate.md             # structural (pdf_extract) + summary (article_summarize)
  index.json                        # entry now: {change_type: "new", topics: ["mandate","compliance_deadline", ...], adapter: change_type_assess, ...}
```

## Rules

- Assign topics **only** from your five (`emits`); never reach for a tag outside the inventory.
- Assign a topic, and set `change_type`, only when the extracted text supports it — narrow, never pad.
- **Extend** `topics` (union with `article_summarize`'s), never overwrite the prior step's tags.
- Ground every tag and the `change_type` in the source; flag silence rather than inferring.
- Do not branch on `domain` (D7) — the tag inventory comes from the pack, not from code.

## Boundaries

- Does not extract structure (`pdf_extract`, step 1) or summarize/assign subject-matter topics
  (`article_summarize`, step 2) — those ran before you.
- Does not emit `article_summarize`'s tags (`brand_rules`, `message_format`, `interchange_fees`,
  `reporting`, `transaction_flow`) or the code-only tags (`settlement`, `error_handling`).
- Does not read or process code — code routes to `code_map_build` via the `code_pipeline` (§6.6.3).
- Does not ingest (no fetch/auth) — the connector staged, and the prior steps ran, before you.
