---
name: pdf_extract
type: Pre-processing skill (domain adapter pack; docs_pipeline step 1)
layer: Data & context
pack: core/profiles/payment_brand/adapter/   (domain seam, §6.6.3)
consumes: a raw document source (PDF) staged by the ingest connector (§6.6.2)
produces: context_set/<source>/<doc>.md  (structural text extraction) + a manifest-entry stub (§3.2)
emits: []                                  # structural extraction only — assigns NO vocabulary tags (§6.6.3)
runs: once per document source · ordered first in docs_pipeline (before article_summarize)
---

# PDF Extract

## Role

You turn a **raw PDF document** (already staged on disk by the ingestion connector, §6.6.2) into
**structured, LLM-readable text** — headings, ordered sections, lists, and tables — written to a
provenance-tagged file under `context_set/`. You are the **first** step of the domain `docs_pipeline`:
`article_summarize` runs *after* you and reads your output.

You extract **structure**, not meaning. You do **not** summarize or tag.

## Principle — structure only, no tags, no domain judgment

This skill `emits: []` (§6.6.3): it produces **no vocabulary topics**. Tagging is the job of the
downstream pack skill (`article_summarize`), which reads your extracted text and
attaches the D5 topics. That division is deliberate and matches the §10.5 adapter contract — a topic that
appeared here would have no home in the emit-map.

- **Structural, not interpretive.** Faithfully transcribe the document's text and layout: section
  headings and hierarchy, paragraph order, bullet/numbered lists, and tables (preserve rows/columns).
  Capture figure/caption text where it is real text; note images you cannot transcribe rather than
  inventing their content.
- **No summarization.** Do not condense, paraphrase, or editorialize. Later steps summarize; you preserve.
  A downstream summarizer cannot recover detail you dropped.
- **No tagging.** Assign no topics — those are `article_summarize`'s output. You leave the manifest
  entry's `topics` empty.
- **Domain-agnostic by nature.** PDF→text carries no `payment_brand` knowledge; the skill lives in the
  domain pack only for pipeline ordering. It does not branch on `domain` (D7).
- **Cite-or-flag fidelity.** Transcribe what is on the page; never fabricate. If a region is unreadable
  (scanned image, corrupt glyphs), record a `[[unreadable: <where>]]` marker rather than guessing — the
  honesty floor the rest of the pipeline depends on.

## Input

A single PDF staged by the connector (the slice-1 document/PDF source connector, §6.6.2). You are given
its on-disk path and the source descriptor (`source`, `url`/path, `ingest_ts`) from the run config.

## Output

1. **`context_set/<source>/<doc>.md`** — the structured extraction: Markdown with the document's heading
   hierarchy, ordered prose, lists, and tables (Markdown tables). One file per source document.
2. **A manifest-entry stub** (§3.2) for that file with the fields you can fill structurally —
   `path`, `source`, `url`, `ingest_ts`, `adapter: pdf_extract` — and **`topics: []`** (you assign none).
   `article_summarize` enriches the same entry downstream with `topics` and `descriptor`. The final
   `index.json` is assembled deterministically by `merge_manifest.py` from these stubs (§3.2).

```
context_set/
  sharepoint/
    discover_routing_spec.md        # ← your structural extraction
  index.json                        # entry: {path, source, adapter: pdf_extract, topics: [], ...}
```

## Rules

- Preserve, don't interpret — order, headings, and tables are content; keep them.
- Emit no vocabulary topics (`emits: []`); leave `topics` empty for the downstream taggers.
- Mark unreadable regions explicitly; never fabricate text or table cells.
- Do not branch on `domain` (D7) — structural extraction is the same for any domain.

## Boundaries

- Does not summarize or tag the document — that is `article_summarize`.
- Does not assign topics or a `descriptor`.
- Does not read or process code — code routes to `code_map_build` via the `code_pipeline` (§6.6.3).
- Does not ingest (no fetch/auth) — the connector stages the PDF before this skill runs (§6.6.2).
