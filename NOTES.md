# Working notes

## TASK-034 flags — RESOLVED 2026-06-22 (V-approved)

- **Flag A — `adapter` field (RESOLVED).** `change_type_assess.skill.md` no longer overwrites
  `adapter`; it stays `article_summarize` per §3.2 (the field records the *summarizing* adapter that
  authored the `descriptor`, not the last skill to touch the entry).
- **Flag B — PDF source label (RESOLVED).** Oracle provenance label reconciled `"pdf"` → `"sharepoint"`
  to match locked `UI_INPUT.example.yaml` + `brd_profile` routing sources. Run workspace + oracle
  realigned; selective-read routing verified to select doc sections.

## Open design question (from Flag B) — keeping provenance labels aligned, and non-PDF inputs

Flag B exposed that three axes are distinct and must stay aligned:

1. **source `type`** (`file | bitbucket | confluence | sharepoint`) — *how to ingest*; selects the
   connector (`ingest_<type>.py`). Covered by build check §10.4 (every configured type has a connector).
2. **source provenance label** (`source: sharepoint`) — *the logical bucket* entries are tagged with and
   that profiles route off (`section.sources`). **No build check guards this today** — a run can
   configure a `source:` label no profile section lists, and those entries route nowhere (silent).
3. **document format** (PDF / DOCX / HTML) — *how to extract structure*; owned by the docs_pipeline
   step-1 extraction skill (`pdf_extract`). Orthogonal to (1) and (2).

**Proposed alignment mechanism (P4/P5 build check — not built yet):** extend the domain-seam checks
with a *provenance-label containment* check, the source-label analogue of §10.1 topic containment:
assert every `section.sources[]` value across `brd_profile`/`frd_profile` is a recognized label, and
warn when a run's `UI_INPUT.sources[].source` is a label no section routes off ("ingested but
unroutable"). This makes Flag-B-style drift a loud build failure instead of a silent routing miss.

**On non-PDF inputs from SharePoint:** provenance (`sharepoint`) is independent of format. A `.docx`
from SharePoint keeps the same `source: sharepoint` label and routes identically — only docs_pipeline
**step 1** changes: generalize `pdf_extract` into a format-dispatching `doc_extract` (or add a sibling
extraction skill), leaving `article_summarize` / `change_type_assess` untouched. Same "write one more
extractor" seam pattern as the connectors. (Forward-compat note; deferred — see §11.)

## TASK-035 — clone idempotency caveat (open item, low priority)

D8b specifies clone idempotency as "re-clone/pull to pinned SHA; **skip if present & matching**."
`clone.py` instead implements **protective** idempotency: it raises `FileExistsError` on a populated
`repo/` (won't silently double-clone/clobber). The *skip-if-present* decision is the `source_processor`
worker's responsibility (orchestrator level) and isn't encoded in the skill yet. For the external build
the local fixture clones with `commit_sha: null`, so there is no SHA to "match" anyway — full D8b
skip-if-matching is a **port-time** behavior (real git repo + SHA). Recommend: add a worker-level
"repo/ present at pinned SHA → skip clone" check when repo SHAs become real. V to decide if/when.
