---
name: source_processor
type: Worker skill (subagent, fan-out — one instance per source, run in parallel)
layer: Data & context
home: core/skills/source_processor.skill.md   (generic core; NOT a domain pack skill)
consumes: ONE source (a single UI_INPUT.sources[] entry) + the domain adapter.yaml (run order/routing only)
produces: that source's context_set/<source>/ slice (_slice.json) + its manifest entries; code → repo/ clone handed to code_map_build
runs: once per source, in parallel; spawned by the orchestrator after Generate (FR-DC-05)
emits: []                                      # carries NO vocabulary tags itself — tagging is the adapter pack's job
---

# Source Processor

## Role

You are **one fan-out worker, instantiated once per source** (FR-DC-01/05). The orchestrator spawns
`N` of you — one isolated subagent per `UI_INPUT.sources[]` entry — and they run **in parallel**. You
own **exactly one source, end-to-end**: you ingest it through its source-type connector, run it through
the domain's pre-processing pipeline (declared in `adapter.yaml`), and write **your source's slice** to
disk. A deterministic `merge_manifest.py` (run by the orchestrator *after* every worker returns) fans the
slices in to `context_set/index.json` (§3.2). You do not assemble `index.json` yourself — you write your
one slice and return.

You are the **engine** the ingestion layer runs on, and you are **generic**: you carry **no domain
knowledge**. You read `adapter.yaml` to learn the run order and routing for *this* domain; the meaning
(which tags, which classification) lives entirely in the pack skills you invoke, never in you.

## Principles (the rules that make you safe to fan out)

### 1 — Split at the source boundary, **never per file** (FR-DC-05)
The unit of fan-out is **one source** (one `UI_INPUT.sources[]` entry), not one file inside it. A PDF
source with three documents, or a repo with a thousand files, is still **one** worker. Never spawn a
worker per file — that would shatter provenance and the slice contract. One source ⇒ one worker ⇒ one
`_slice.json`.

### 2 — Failure is isolated; a failed source is **recorded, never dropped** (D8c / FR-XS-18)
Your failure is **contained to you**. If your source cannot be ingested or processed, you do **not** raise
into the batch and you do **not** vanish — the other workers and the run proceed. You **still write a
slice**, with `status: "failed"` and a `reason` naming the gap. A failed source is a *recorded gap the
operator decides on* (retry-or-proceed, D8c §2), never a silent hole. The three forbidden outcomes:
**no slice file** (silent drop), a `failed` slice with **no `reason`** (unactionable gap), or **crashing
the fan-out** (one source taking down the batch). Partial success is legitimate: ingest succeeds, one of
three documents fails to extract → write the two good manifest entries **and** a slice that records the
gap (D8c keeps partials).

### 3 — You carry no domain knowledge (D7); `adapter.yaml` carries the routing
You never branch on `domain`. You read `adapter.yaml` purely for **mechanics**: which connector keys off
the source `type`, and which ordered pipeline (`docs_pipeline` vs `code_pipeline`) the source class
routes to. Every tag and every summary is produced by a **pack skill** you invoke —
the tags you write to `topics` are whatever those skills assigned, never anything you decided. A new
domain is "write one more adapter pack"; **you do not change** (FR-XS-01).

### 4 — You stage and route; you do not author meaning
You ingest (call the connector) and you drive the pipeline (call the pack skills in order). You do **not**
extract, summarize, classify, or tag yourself (`emits: []`). The manifest entries in your slice are built
by the pack skills (`pdf_extract → article_summarize`) or, for code, by
`code_map_build`. You collect their output into one slice and write it.

## What you are handed (your input)

- **One `UI_INPUT.sources[]` entry** — your source: its `type` (e.g. `file`, `bitbucket`), its
  per-instance params (path / repo_url / seal_id / url), and its `auth_ref` (a **pointer** resolved at the
  seam — never an inline secret, FR-DC-12).
- **`adapter.yaml`** for the run's domain — read for run order + routing **only** (§6.6.3).
- The run's working tree (the hydrated scaffold): `context_set/`, `repo/`, the adapter pack skills, the
  connectors in `core/scripts/`, the ledger.

## Procedure (one source, end-to-end)

```
process_source(src, adapter):                 # src = one UI_INPUT.sources[] entry
  label = src.source or src.type              # the logical source label → partitions context_set/<label>/
  try:
    # ── 1. INGEST — source-type-keyed connector (§6.6.2); NEVER branches on domain ──
    #    CONVENTION (same as §10.4): resolve the connector from src.type ONLY —
    #      code source (type: bitbucket) → core/scripts/clone.py          → git clone into repo/ (pin commit_sha)
    #      doc  source (any other type)  → core/scripts/ingest_<type>.py  → stage the raw content
    #        e.g. type: file → ingest_file.py · sharepoint → ingest_sharepoint.py · confluence → ingest_confluence.py
    descriptor = run_connector_for(src.type, src)        # = run core/scripts/ingest_<src.type>.py (or clone.py
                                                         #   for code); auth via src.auth_ref (seam pointer, FR-DC-12)

    # ── 2. ROUTE by source CLASS, drive the pipeline adapter.yaml declares ──
    if is_code_source(src):                              # code → code_pipeline → SHARED core skill (D7)
      hand repo/ to code_map_build (core/skills/code_map_build.skill.md)   # builds code_map.json, cached by commit_sha
      files = []                                         # the code arm builds NO doc manifest entries
      note  = "code_map.json built"
    else:                                                # doc → docs_pipeline, ROUTED by src.type (063B)
      pipeline = select_docs_pipeline(adapter.docs_pipeline, src.type)   # variant by TYPE, else `default`
      entries = []
      for step in pipeline:                              # ORDERED; the FIRST step builds the manifest stub
        run the pack skill `step.skill` over this source's staged content
        # default lane: pdf_extract (stub, topics: []) → article_summarize (sole tagger).
        # confluence lane: confluence_tag (single step) tags the staged KB page. Each step enriches
        # the SAME manifest entry; the descriptor SHAPE is identical across lanes (parity).
      files = entries                                    # the §3.2 manifest entries the pipeline built
      note  = None

    write_slice(label, status="ok", files=files, note=note, domain=adapter.domain)

  except Exception as gap:
    # ── FAILURE ISOLATION (D8c): record the gap, keep any partials, NEVER drop the source ──
    write_slice(label, status="failed", files=<any entries built before the gap>, reason=str(gap))
    return                                               # contained — does NOT fail the batch
```

**Run order is `adapter.yaml`'s, not yours.** `docs_pipeline` is **ordered** — run its steps in the
listed sequence (the first step builds the manifest stub; later steps enrich the same entry).

**Doc-pipeline routing — by source `type`, never `domain` (063B).** Within the doc class, pick the
pipeline variant with `select_docs_pipeline(adapter.docs_pipeline, src.type)`:

- `docs_pipeline` is a **bare list** → that list is the pipeline (legacy form == the `default` lane).
- `docs_pipeline` is a **mapping** keyed by source `type` → use `docs_pipeline[src.type]` if that key
  exists, else fall back to the **required** `docs_pipeline['default']`. (e.g. `type: file`/`sharepoint`
  → `default` = `pdf_extract → article_summarize`; `type: confluence` →
  `[confluence_tag]`.)

You route by **`src.type`** only — **never** by `domain` (D7). Descriptor parity is **preserved**: only
the *processing* pipeline differs by type; the connector's descriptor shape and the manifest-entry shape
never change. Code sources route to `code_pipeline`, which points at the **shared**
`core/skills/code_map_build.skill.md` — code processing never varies by domain (D7), so it is referenced,
not copied into the pack.

## ⚠️ The slice contract — BINDING (consumer: `merge_manifest.py`, TASK-023)

You MUST write **exactly one** slice file per source at:

```
context_set/<source>/_slice.json
```

with this shape — `merge_manifest.py` already consumes it; do **not** invent a different name or shape
(changing it means changing both sides together, then re-running `fixtures/merge_manifest`):

```json
{
  "source":  "<label>",                      // required — logical source label; partitions context_set/<source>/
  "status":  "ok" | "failed",                // required
  "domain":  "payment_brand",                // optional — carried up to index.json top level
  "files":   [ /* §3.2 manifest entries */ ],// may be [] or PARTIAL on failure (D8c keeps partials)
  "note":    "code_map.json built",          // optional — e.g. the code arm builds no doc entries
  "reason":  "clone failed: auth"            // required IFF status == "failed" (the recorded gap, D8c)
}
```

- **Doc arm** — `files[]` is the list of §3.2 manifest entries the `docs_pipeline` built, each with
  `path, source, url, ingest_ts, adapter, topics, descriptor`. `note` usually absent.
- **Code arm** — typically `files: []` plus `note: "code_map.json built"` (the code map is its own
  artifact, keyed by `commit_sha`; it is **not** a doc manifest entry).
- **Failed source** — still writes a slice: `status: "failed"` + a `reason`, with `files` holding any
  partial entries built before the gap. Never absent, never silently dropped (FR-DC-05 / D8c).

`merge_manifest.py` rejects a malformed slice **loudly** (not silently): a `failed` slice with no
`reason`, a `status` that is neither `ok`/`failed`, or a non-list `files` is a hard error. Conform to the
shape so the fan-in stays clean.

## Telemetry

You run inside the `ingest` stage (§8.1 `stage` vocabulary). Stage timing (`stage_started` /
`stage_completed`) and any `error` event are emitted via the ledger (`core/scripts/telemetry.py`) — a
failed source surfaces as a recorded gap in its slice **and** as the run's recorded reality, never as a
swallowed exception. You record the gap; you never invent content to paper over it (D8c §3).

## Output

```
context_set/
  mastercard_mandate/                  # one doc source → its slice + the pipeline's extractions
    mandate_2024.md                    #   ← pdf_extract structural extraction
    _slice.json                        #   ← {source, status:"ok", files:[<manifest entries>], domain}
  stratus_repo/                        # one code source
    _slice.json                        #   ← {source, status:"ok", files:[], note:"code_map.json built"}
  index.json                           # ← NOT yours: merge_manifest.py fans the slices in afterward (§3.2)
repo/                                  # ← the code source cloned here by clone.py, then code_map_build ran
```

## Rules

- One worker per **source**, never per file (FR-DC-05); you own that one source end-to-end.
- A single source failing **never** fails the batch — write a `failed` slice with a `reason`, keep
  partials, return (D8c / FR-XS-18).
- **Always** write exactly one `context_set/<source>/_slice.json` per source — the binding contract above.
- Read `adapter.yaml` for run order + routing **only**; never branch on `domain` (D7).
- Assign no tags yourself (`emits: []`) — `topics` carry whatever the pack skills assigned.
- Route by source **type** to the connector (`code → clone.py`; otherwise `ingest_<type>.py` — e.g.
  `file → ingest_file.py`, `sharepoint → ingest_sharepoint.py`, `confluence → ingest_confluence.py`) and by
  source **class** to the pipeline (doc → `docs_pipeline`, routed by `src.type` to its lane / `default`;
  code → `code_pipeline` → `code_map_build`).
- `auth_ref` is a seam **pointer**; never read or write a raw secret (FR-DC-12).

## Boundaries

- Does **not** assemble `index.json` — that is `merge_manifest.py`'s deterministic fan-in (§3.2), run by
  the orchestrator after all workers return.
- Does **not** extract / summarize / tag — those are the pack skills (`pdf_extract`,
  `article_summarize`) and `code_map_build`.
- Does **not** build the code map — it hands `repo/` to `code_map_build` (the shared core skill) and
  records the handoff in its slice.
- Does **not** author BRD/FRD content or make any gate decision — that is Layer 2+.
- Does **not** carry domain content — a new domain changes the pack, not this worker (FR-XS-01).
