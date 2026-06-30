---
name: confluence_tag
type: Pre-processing skill (domain adapter pack; docs_pipeline `confluence` lane, sole step)
layer: Data & context
pack: core/profiles/payment_brand/adapter/   (domain seam, §6.6.3)
consumes: context_set/<source>/<page>.html  (the staged Confluence page from ingest_confluence.py)
produces: a manifest entry with topics/descriptor (§3.2) for the staged KB page
emits: [brand_rules, card_brand, message_format, routing, transaction_flow, error_handling]   # §6.6.3 / D5 emitted_by (r3, TASK-063B)
runs: once per Confluence source · the SOLE step of the `confluence` docs_pipeline lane (no pdf_extract / article_summarize / change_type_assess)
---

# Confluence Tag

## Role

You read the **staged Confluence page** (`ingest_confluence.py` already fetched it — it is already
text/HTML, so there is **no structural extraction step**) and **assign the vocabulary topics** that
genuinely apply to it. You are the **only** step in the `confluence` docs_pipeline lane: a Confluence
page is a **product knowledge-base / reference** page, not a mandate PDF, so it does **not** route
through `pdf_extract` (already text), `article_summarize` (a KB is not an article to summarize), or
`change_type_assess` (a KB describes steady state, not a *change*). You tag; you do not summarize or
classify a change.

## Principle — your inventory is fixed; assessment only narrows it

This skill is authorized for exactly six vocabulary tags (§6.6.3 / D5 `emitted_by`, r3):

```
emits: [brand_rules, card_brand, message_format, routing, transaction_flow, error_handling]
```

That set is your **inventory** — the closed shelf of tags you may assign, the "how it works"
reference concepts a payment-brand KB page actually carries. At runtime you **assess** which of these
six apply to *this* page and assign that subset to its `topics` (all six, a few, or none). You may
**narrow, never invent**:

- **Never assign a tag outside your six.** The change/compliance-driven tags (`mandate`,
  `compliance_deadline`, `certification`) and the others (`settlement`, `interchange_fees`,
  `reporting`) belong to other skills' inventories. A KB page that merely *mentions* certification in
  passing does **not** earn `certification` — that tag is `change_type_assess`'s, and a passing
  mention is not substantive coverage. A tag outside your `emits` has no home in the §10.5 emit-map
  and is a contract violation, not a judgment call.
- **Assign only what the page earns.** A topic is assigned only when the page actually supports it.
  Do not pad `topics`; an unsupported tag misleads every downstream consumer.
- **Cite-or-flag fidelity — cite the page, do not paraphrase it.** A KB is **reference** material:
  ground every assigned topic in the page text, and let the BRD/FRD author cite the **actual page**
  rather than a lossy summary. If the page is silent or ambiguous on something, leave the tag off and
  say so — never infer a topic the page does not state.
- **Do not summarize or classify a change.** You produce a short grounded `descriptor` line so the
  manifest entry is legible, but you do **not** write an `article_summarize`-style summary section and
  you do **not** make a `change_type` call. A KB page has no `change_type`.
- **Domain-agnostic plumbing.** You live in the `payment_brand` pack for your tag inventory, but you
  do **not** branch on `domain` (D7) — the tag-a-page behavior is the same shape for any domain; only
  the inventory differs, and that comes from the pack, not from code.

## Your tag inventory (what each of the six means)

Assign each only when the page text supports it (definitions are D5, verbatim from the vocabulary):

- **`brand_rules`** — brand technical/operational rules that constrain implementation.
- **`card_brand`** — which card brand(s) the page concerns. *(Shared with `change_type_assess` /
  `code_map_build`.)*
- **`message_format`** — message/wire formats and field-level details the page documents. *(Shared
  with `article_summarize` / `code_map_build`.)*
- **`routing`** — transaction routing to brand handlers. *(Shared with `change_type_assess` /
  `code_map_build`.)*
- **`transaction_flow`** — end-to-end transaction lifecycle steps. *(Shared with `article_summarize` /
  `code_map_build`.)*
- **`error_handling`** — failure modes, error codes, retry/fallback. *(Shared with `code_map_build`.)*

## Input

The staged Confluence page for one source — `context_set/<source>/<page>.html` — plus that page's
manifest-entry stub (`path`, `source`, `url`, `ingest_ts`, `topics: []`). You read this file; you do
not re-fetch the page (the connector already staged it; auth happened at ingest).

## Output

**Manifest-entry enrichment** (§3.2) on the staged page's entry: set **`topics`** to the subset of
your six the page earns, set `adapter: confluence_tag`, and fill the `descriptor` (a short, grounded
one-line summary of what the page covers). The final `index.json` is assembled deterministically by
`merge_manifest.py` (§3.2). The descriptor shape is **identical** to every other doc source's (parity)
— only the *processing* differed, never the manifest contract.

```
context_set/
  confluence/
    card_brand_routing.html          # ← the staged KB page (ingest_confluence.py)
  index.json                         # entry: {adapter: confluence_tag, topics: [card_brand, routing, ...], descriptor: "...", ...}
```

## Rules

- Assign topics **only** from your six (`emits`); never reach for a tag outside the inventory.
- Assign a topic only when the page text supports it — narrow, never pad; a passing mention is not coverage.
- Ground every assigned tag in the page; flag silence rather than inferring. Cite the page, don't paraphrase.
- Do not make a `change_type` call or emit another skill's tags; do not write a summary section.
- Do not branch on `domain` (D7) — the tag inventory comes from the pack, not from code.

## Boundaries

- Does not fetch/auth — `ingest_confluence.py` staged the page (auth at the seam) before you run.
- Does not extract structure — a Confluence page is already text; there is no `pdf_extract` step here.
- Does not summarize (no `article_summarize`) or classify a change (no `change_type_assess`).
- Does not read or process code — code routes to `code_map_build` via the `code_pipeline` (§6.6.3).
