#!/usr/bin/env python3
"""merge_manifest.py — deterministic fan-in of per-source slices → ``index.json`` (§3.2).

After the orchestrator fans out one ``source_processor`` worker per source (FR-DC-05),
each worker writes **its own source's slice** to disk and returns. This script is the
deterministic **fan-in**: it reads every per-source slice and assembles the single
``context_set/index.json`` manifest (§3.2) the authoring agents load and route off.

It is **plumbing, not judgment** (FR-XS-03 / NFR-07): it concatenates, counts, sorts,
and writes. It assigns no tags, makes no authoring call, and branches on no ``domain``.
Re-running it over the *same* slices reproduces the *same* ``index.json`` byte-for-byte
(NFR-01) — see "Determinism" below.

A **failed source is recorded, never dropped** (FR-DC-05 / D8c): every slice contributes
exactly one ``sources_status`` row, including ``status:"failed"`` with its ``reason``. A
failure is a recorded gap the operator decides on (retry-or-proceed, D8c §2) — it is not
a silent hole in the manifest.

────────────────────────────────────────────────────────────────────────────────────────
Per-source **slice** contract (defined here; honored by ``source_processor``, §6 / TASK-033)
────────────────────────────────────────────────────────────────────────────────────────
§3.2 pins the *output* (``index.json``). Each fan-out worker writes one slice file:

    context_set/<source>/_slice.json

with this shape::

    {
      "source":  "confluence",            # required — the logical source label
      "status":  "ok" | "failed",         # required
      "domain":  "payment_brand",         # optional — carried up to index.json top level
      "files":   [ <manifest entry §3.2>, ... ],   # may be [] or PARTIAL (D8c: partials kept)
      "note":    "code_map.json built",   # optional — e.g. the code arm builds no doc entries
      "reason":  "clone failed: auth"     # required iff status == "failed"
    }

Each entry in ``files[]`` is a §3.2 manifest entry the adapter pipeline built
(``path``, ``source``, ``url``, ``ingest_ts``, ``adapter``, ``topics``,
``descriptor`` — the doc arm; a code source typically carries no doc entries and instead
sets ``note``). This script does not author or mutate entries; it passes them through with
a canonical, deterministic key order.

────────────────────────────────────────────────────────────────────────────────────────
Determinism (NFR-01 / NFR-07) — the binding acceptance for this task
────────────────────────────────────────────────────────────────────────────────────────
Same slices in ⇒ identical ``index.json`` out. To guarantee it, nothing here reads the
wall clock or the environment:

  * ``files[]`` is sorted by ``path`` (stable, total order).
  * ``sources_status[]`` is sorted by ``source``.
  * every dict is emitted in a fixed key order (no ``sort_keys`` reshuffle of the §3.2
    shape; unknown extra keys are appended sorted, so they too are deterministic).
  * ``generated_at`` is **derived from the inputs** — the max ``ingest_ts`` across all
    entries (the manifest is "generated as of" its newest input) — never ``now()``. It
    can be pinned explicitly with ``--generated-at`` for an exact replay.

``run_id`` and ``domain`` come from the caller (``--run-id`` / ``--domain``), falling back
to ``ledger/run_state.json`` (run_id) and any slice's ``domain`` field respectively — all
deterministic functions of on-disk state.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Canonical key order for a §3.2 manifest entry. Known fields emit in this order; any
# extra fields a future adapter adds are appended in sorted order (still deterministic).
_ENTRY_FIELD_ORDER = (
    "path", "source", "url", "ingest_ts", "adapter", "topics", "descriptor",
)

# Canonical key order for a sources_status row (matches the §3.2 example shape).
_STATUS_FIELD_ORDER = ("source", "status", "files", "note", "reason")

SLICE_FILENAME = "_slice.json"     # the per-source slice each fan-out worker writes


def _ordered(d: dict, field_order: tuple[str, ...]) -> dict:
    """Return ``d`` re-keyed in ``field_order`` first, then any remaining keys sorted.

    Deterministic by construction: the output key order is a pure function of ``d``'s
    keys, independent of insertion order. Drops nothing — extra keys are preserved.
    """
    out: dict = {}
    for k in field_order:
        if k in d:
            out[k] = d[k]
    for k in sorted(d):
        if k not in out:
            out[k] = d[k]
    return out


def load_slice(path: str | Path) -> dict:
    """Load and minimally validate one per-source slice file.

    Plumbing-level validation only (shape, not meaning): ``source`` and ``status`` are
    required; a ``failed`` slice must carry a ``reason`` (so the recorded gap is
    actionable, D8c). Raises ``ValueError`` on a malformed slice — a broken slice is a
    loud error, never a silently-dropped source.
    """
    p = Path(path)
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"slice is not valid JSON: {p} ({exc})") from exc
    if not isinstance(data, dict):
        raise ValueError(f"slice must be a JSON object: {p}")
    if not data.get("source"):
        raise ValueError(f"slice missing required 'source': {p}")
    status = data.get("status")
    if status not in ("ok", "failed"):
        raise ValueError(f"slice 'status' must be 'ok' or 'failed' (got {status!r}): {p}")
    if status == "failed" and not data.get("reason"):
        raise ValueError(f"failed slice must carry a 'reason': {p}")
    files = data.get("files", [])
    if not isinstance(files, list):
        raise ValueError(f"slice 'files' must be a list: {p}")
    return data


def discover_slices(context_set: str | Path) -> list[Path]:
    """Return every ``<context_set>/<source>/_slice.json``, sorted (deterministic order)."""
    root = Path(context_set)
    return sorted(root.glob(f"*/{SLICE_FILENAME}"))


def _status_row(slice_data: dict) -> dict:
    """Build the one ``sources_status`` row for a slice — every slice yields exactly one."""
    row: dict = {"source": slice_data["source"], "status": slice_data["status"]}
    n = len(slice_data.get("files", []))
    if n:                                       # omit the count for arms that carry no doc entries (e.g. code)
        row["files"] = n
    if slice_data.get("note"):
        row["note"] = slice_data["note"]
    if slice_data["status"] == "failed":
        row["reason"] = slice_data["reason"]    # guaranteed present by load_slice
    return _ordered(row, _STATUS_FIELD_ORDER)


def _derive_generated_at(entries: list[dict]) -> str | None:
    """Max ``ingest_ts`` across entries — a deterministic stand-in for a wall-clock stamp.

    ISO-8601 UTC ``...Z`` timestamps sort correctly as plain strings. Returns ``None`` if
    no entry carries an ``ingest_ts`` (the caller may still pin one via ``--generated-at``).
    """
    stamps = [e["ingest_ts"] for e in entries if isinstance(e, dict) and e.get("ingest_ts")]
    return max(stamps) if stamps else None


def merge(
    slices: list[dict],
    *,
    run_id: str,
    domain: str | None = None,
    generated_at: str | None = None,
) -> dict:
    """Assemble the §3.2 ``index.json`` object from loaded per-source slices.

    Deterministic: output is a pure function of the inputs (no clock, no env). ``files``
    is the union of every slice's entries sorted by ``path``; ``sources_status`` is one
    row per slice sorted by ``source`` (failed sources included — D8c). ``domain`` falls
    back to the first slice that declares one; ``generated_at`` falls back to the max
    ``ingest_ts`` across all entries.
    """
    # union of all entries, normalized to the canonical §3.2 key order, sorted by path
    entries: list[dict] = []
    for s in slices:
        for entry in s.get("files", []):
            entries.append(_ordered(dict(entry), _ENTRY_FIELD_ORDER))
    entries.sort(key=lambda e: e.get("path", ""))

    # one status row per slice, sorted by source — nothing dropped
    statuses = sorted((_status_row(s) for s in slices), key=lambda r: r["source"])

    if domain is None:
        for s in slices:
            if s.get("domain"):
                domain = s["domain"]
                break
    if generated_at is None:
        generated_at = _derive_generated_at(entries)

    index: dict = {"run_id": run_id}
    if domain is not None:
        index["domain"] = domain
    if generated_at is not None:
        index["generated_at"] = generated_at
    index["files"] = entries
    index["sources_status"] = statuses
    return index


def _run_id_from_run_state(context_set: Path) -> str | None:
    """Best-effort: read ``run_id`` from the sibling ``ledger/run_state.json`` (§3.5)."""
    rs = context_set.parent / "ledger" / "run_state.json"
    if rs.is_file():
        try:
            return json.loads(rs.read_text(encoding="utf-8")).get("run_id")
        except (json.JSONDecodeError, OSError):
            return None
    return None


def dumps(index: dict) -> str:
    """Canonical serialization: indent 2, UTF-8 preserved, fixed key order, trailing NL."""
    return json.dumps(index, ensure_ascii=False, indent=2) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Deterministic fan-in of per-source slices → context_set/index.json (§3.2).",
    )
    ap.add_argument(
        "--context-set", default="context_set",
        help="run's context_set/ dir; discovers <source>/_slice.json (default: context_set)",
    )
    ap.add_argument(
        "--slice", action="append", dest="slices", metavar="PATH",
        help="explicit slice file (repeatable); overrides discovery under --context-set",
    )
    ap.add_argument("--run-id", help="run id (else read from ledger/run_state.json)")
    ap.add_argument("--domain", help="domain (else taken from a slice's 'domain' field)")
    ap.add_argument(
        "--generated-at", help="pin generated_at (else max ingest_ts across entries)",
    )
    ap.add_argument(
        "-o", "--out",
        help="write index.json here (default: <context-set>/index.json; '-' for stdout)",
    )
    args = ap.parse_args(argv)

    context_set = Path(args.context_set)
    try:
        slice_paths = [Path(p) for p in args.slices] if args.slices else discover_slices(context_set)
        if not slice_paths:
            raise ValueError(f"no per-source slices found under {context_set}/ (looked for */{SLICE_FILENAME})")
        slices = [load_slice(p) for p in slice_paths]

        run_id = args.run_id or _run_id_from_run_state(context_set)
        if not run_id:
            raise ValueError("run_id not given and not found in ledger/run_state.json; pass --run-id")

        index = merge(slices, run_id=run_id, domain=args.domain, generated_at=args.generated_at)
    except (ValueError, OSError) as exc:
        print(f"merge_manifest.py: {exc}", file=sys.stderr)
        return 1

    payload = dumps(index)
    out = args.out or str(context_set / "index.json")
    if out == "-":
        sys.stdout.write(payload)
    else:
        Path(out).write_text(payload, encoding="utf-8")
        print(f"merge_manifest.py: wrote {out} "
              f"({len(index['files'])} entries, {len(index['sources_status'])} sources)",
              file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
