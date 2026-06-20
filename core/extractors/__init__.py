"""Code-map extractor dispatcher (TASK-008).

The deterministic spine of the code-map build (TECH_SPEC §5.5). This package is
the **only place language varies** (§5.5): adding a language = "write one more
extractor + register it"; the core, the schema, and ``code_impact`` are untouched.

Division of labor (FR-DC-15 / FR-DC-17), enforced here in code so it cannot waver:

  - ``detect_language``  — deterministic, model-free (file-glob histogram +
                           build-manifest signals); the single dominant language.
  - ``partition_by_language`` — deterministic per-language file map (ADR-002), so a
                           polyglot repo routes each language independently.
  - ``extractor_for``    — registry lookup; returns a frozen extractor or ``None``.
  - ``normalize``        — maps any extractor's raw output → the §3.3 file-entry shape.
  - ``merge_edges``      — deterministic ``depends_on ↔ used_by`` closure.

What this module does NOT do (downstream tasks own these, wired here as slots):

  - run the C extractor                       → TASK-009  (``c_extractor.py``)
  - model-only fallback structure             → TASK-010  (``else`` branch below)
  - model enrichment (``purpose`` + ``tags``) → TASK-011  (the model, not code)
  - the 3-branch onboarding gate              → TASK-013

The agentic skill ``core/skills/code_map_build.skill.md`` orchestrates the flow
and *invokes* these functions; it does not re-implement them in prose.
"""

from __future__ import annotations

import os
from collections import Counter
from typing import Callable, Mapping, Optional, Sequence

# Raw extractor entry — whatever a per-language extractor emits before normalization.
RawEntry = Mapping[str, object]
# An extractor is any callable that, given its language partition (the repo-relative
# file list the dispatcher routed to it, per ADR-002) and the repo root, returns
# ``{"entries": [raw file entry, ...], "coverage_report": {...}}``. It owns the
# structural fields + the coverage_report; the model owns purpose/tags (TASK-011).
Extractor = Callable[[Sequence[str], str], Mapping[str, object]]

# ──────────────────────────────────────────────────────────────────────────────
# §3.3 file-entry shape — the normalization target. Structural fields are owned
# by the extractor; ``purpose``/``tags`` are filled later by the model (TASK-011),
# so normalize() seeds them empty. The two reserved cross-repo fields (FR-DC-13)
# are emitted empty so the deferred C5 extension is additive, not a reshape.
# ──────────────────────────────────────────────────────────────────────────────
STRUCTURAL_FIELDS = ("path", "module", "interfaces", "depends_on", "used_by", "coverage")
MODEL_FIELDS = ("purpose", "tags")            # set by model_enrich (TASK-011), not here
RESERVED_FIELDS = ("external_calls", "exposes")  # FR-DC-13, unpopulated in MVP


# ──────────────────────────────────────────────────────────────────────────────
# Language detection — deterministic, model-free (FR-DC-15).
# ──────────────────────────────────────────────────────────────────────────────

# Extension → language. Slice 1 only onboards ``c``; the rest of the map lets
# detection name a language even when no extractor is registered yet, so the
# dispatcher routes such repos to the model-only fallback (TASK-010) rather than
# guessing. Extend this table when a language is onboarded.
_EXTENSION_LANGUAGE: Mapping[str, str] = {
    ".c": "c",
    ".h": "c",
    ".py": "python",
    ".java": "java",
    ".js": "javascript",
    ".ts": "typescript",
    ".go": "go",
    ".rb": "ruby",
    ".rs": "rust",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".hpp": "cpp",
}

# Build-manifest filenames → the language they signal. Used only to break ties
# in the extension histogram (e.g. a C repo whose headers outnumber its sources,
# or a vendored tree). A deterministic nudge, never an override of a clear majority.
_BUILD_MANIFEST_SIGNALS: Mapping[str, str] = {
    "makefile": "c",
    "cmakelists.txt": "c",
    "configure.ac": "c",
    "pom.xml": "java",
    "build.gradle": "java",
    "setup.py": "python",
    "pyproject.toml": "python",
    "go.mod": "go",
    "cargo.toml": "rust",
    "package.json": "javascript",
}

# Build/VCS/tooling trees that carry no mappable source. Pruned by *both* stages.
_NON_SOURCE_DIRS = frozenset({
    ".git", "node_modules", "build", "dist", "__pycache__", ".venv", "venv",
})

# Out-of-tree dependency trees. Excluded from `detect_language`'s histogram so a
# large vendored tree cannot swing the *dominant* language — but NOT excluded from
# `partition_by_language`: an out-of-tree shim a repo references (e.g. the Stratus
# compat header in fixtures/c_repo) is real source the code-map must still cover,
# and the signed oracle counts it as an extracted file. Detection ignores it;
# extraction enumerates it (ADR-002 — the ignore rationale is about detection only).
_VENDOR_DIRS = frozenset({"vendor", "third_party"})

# Histogram-ignore set (detection): build trees AND vendored deps.
_IGNORED_DIRS = _NON_SOURCE_DIRS | _VENDOR_DIRS


def detect_language(repo: str) -> Optional[str]:
    """Return the dominant source language of ``repo``, or ``None`` if undetectable.

    Deterministic and model-free (FR-DC-15): a histogram over source-file
    extensions, with build-manifest filenames used only to break ties. Same tree
    in → same answer out, every run.

    Slice 1 returns a single dominant language (single-repo, single-language is
    the MVP scope; polyglot per-file/per-subtree routing is Phase 5). The signature
    is ready to extend to a per-subtree map without changing callers' branch logic.
    """
    histogram: Counter[str] = Counter()
    manifest_signals: Counter[str] = Counter()

    for dirpath, dirnames, filenames in os.walk(repo):
        # Prune ignored dirs in place so os.walk does not descend into them.
        dirnames[:] = [d for d in dirnames if d.lower() not in _IGNORED_DIRS]
        for name in filenames:
            lang = _BUILD_MANIFEST_SIGNALS.get(name.lower())
            if lang is not None:
                manifest_signals[lang] += 1
            ext = os.path.splitext(name)[1].lower()
            file_lang = _EXTENSION_LANGUAGE.get(ext)
            if file_lang is not None:
                histogram[file_lang] += 1

    if not histogram:
        return None

    top = histogram.most_common()
    best_count = top[0][1]
    # Tie among the top extension languages → let a build-manifest signal decide;
    # otherwise fall back to a stable alphabetical pick so the result is deterministic.
    tied = sorted(lang for lang, count in top if count == best_count)
    if len(tied) == 1:
        return tied[0]
    for lang in sorted(manifest_signals, key=lambda l: (-manifest_signals[l], l)):
        if lang in tied:
            return lang
    return tied[0]


def partition_by_language(repo: str) -> dict[str, list[str]]:
    """Partition a repo's source files by language (ADR-002), deterministic + model-free.

    Returns ``{language: [relative_path, ...]}`` for every source language present, so
    the dispatcher can route each partition independently: a language with a frozen
    extractor goes through it (full coverage); the rest (the *residue*) routes to the
    model fallback marked coarse — no file is dropped (ADR-002 / §5.5).

    This is the polyglot generalization of ``detect_language``: ``detect_language``
    returns the single dominant language (top-level ``code_map.language``, gate input);
    ``partition_by_language`` returns the full per-language file map. Same deterministic
    signals (the extension table); files of unknown extension are omitted (non-source).
    Paths are repo-relative and each language's list is sorted for stable output.

    Enumeration prunes only ``_NON_SOURCE_DIRS`` (build/VCS/tooling), NOT vendored
    trees: an out-of-tree shim the repo references is real source the map covers,
    even though detection ignores it. Detection ignores vendor; extraction maps it.
    """
    partitions: dict[str, list[str]] = {}
    for dirpath, dirnames, filenames in os.walk(repo):
        dirnames[:] = [d for d in dirnames if d.lower() not in _NON_SOURCE_DIRS]
        for name in filenames:
            lang = _EXTENSION_LANGUAGE.get(os.path.splitext(name)[1].lower())
            if lang is None:
                continue
            rel = os.path.relpath(os.path.join(dirpath, name), repo)
            partitions.setdefault(lang, []).append(rel)
    for lang in partitions:
        partitions[lang].sort()
    return partitions


# ──────────────────────────────────────────────────────────────────────────────
# Extractor registry — the language seam (§5.5). ``extractor_for`` returns the
# frozen extractor for a language or ``None`` (→ model-only fallback, TASK-010).
# ──────────────────────────────────────────────────────────────────────────────

# Registered, frozen, per-language extractors. Populated as languages are
# onboarded (§5, human-gated). The C slot is filled at import time (below); an
# unregistered language is intentionally absent so its partition routes to the
# model fallback (TASK-010) rather than crashing.
_REGISTRY: dict[str, Extractor] = {}


def register_extractor(language: str, extractor: Extractor) -> None:
    """Register a frozen per-language extractor. Called once per onboarded language.

    TASK-009 will call ``register_extractor("c", c_extractor.run)``. Registration
    is the seam: the dispatcher never names a language directly.
    """
    _REGISTRY[language] = extractor


def extractor_for(language: Optional[str]) -> Optional[Extractor]:
    """Return the frozen extractor for ``language``, or ``None`` if none is registered.

    ``None`` is the deterministic signal the dispatcher uses to take the
    model-only fallback branch (TASK-010) — never a guess.
    """
    if language is None:
        return None
    return _REGISTRY.get(language)


# Onboard the frozen C extractor (TASK-009, tree-sitter per ADR-001). The import
# is guarded: if the toolchain is absent/unprovisionable (§5.7), "c" simply stays
# unregistered and a C partition degrades to the model-only fallback — coarse
# coverage, never a hard failure. "import succeeds in the venv" is the port check.
try:  # pragma: no cover - exercised by environment, not unit logic
    from . import c_extractor as _c_extractor

    register_extractor("c", _c_extractor.run)
except ImportError:
    pass


# ──────────────────────────────────────────────────────────────────────────────
# Normalization contract (§5.5) — the seam that lets language vary without
# touching the core. Every extractor (deterministic or fallback) MUST emit file
# entries that normalize to the §3.3 shape. The extractor owns the structural
# fields; the model owns purpose/tags only (seeded empty here, filled in TASK-011).
# ──────────────────────────────────────────────────────────────────────────────

def normalize_entry(raw: RawEntry) -> dict:
    """Map one extractor's raw file entry to the §3.3 file-entry shape.

    Deterministic, model-free. Pulls only the structural fields the extractor
    owns; seeds ``purpose``/``tags`` empty (the model fills them in TASK-011) and
    emits the reserved cross-repo fields empty (FR-DC-13). ``path`` is mandatory;
    a raw entry without it is malformed.
    """
    if "path" not in raw:
        raise ValueError(f"extractor entry missing required 'path': {raw!r}")

    coverage = raw.get("coverage", "coarse")
    if coverage not in ("coarse", "deep"):
        raise ValueError(f"coverage must be 'coarse' or 'deep', got {coverage!r}")

    return {
        "path": raw["path"],
        "module": raw.get("module", ""),
        "interfaces": list(raw.get("interfaces", [])),
        "depends_on": list(raw.get("depends_on", [])),
        "used_by": list(raw.get("used_by", [])),
        "tags": [],          # MODEL owns this — set by model_enrich (TASK-011)
        "purpose": "",       # MODEL owns this — set by model_enrich (TASK-011)
        "coverage": coverage,
        "external_calls": [],  # RESERVED (FR-DC-13) — cross-repo, unpopulated in MVP
        "exposes": [],         # RESERVED (FR-DC-13) — integration seam, unpopulated in MVP
    }


def normalize(raw_entries: Sequence[RawEntry]) -> list[dict]:
    """Normalize a whole extractor output to §3.3 file entries, order preserved."""
    return [normalize_entry(e) for e in raw_entries]


# ──────────────────────────────────────────────────────────────────────────────
# Edge merge (§5.5) — DETERMINISTIC closure, not a per-file model judgment.
# Matches one file's outbound references (depends_on) to another file's exposed
# identity (its module) and back-fills the reverse direction (used_by) so the
# impact assessment has the closure (FR-DC-10).
# ──────────────────────────────────────────────────────────────────────────────

def merge_edges(entries: Sequence[dict]) -> list[dict]:
    """Resolve ``depends_on ↔ used_by`` closure across normalized entries.

    Deterministic merge step over the collected entries (§5.5): for every edge
    ``A.depends_on → B``, ensure ``B.used_by`` contains ``A``. Targets are matched
    by ``module`` (the identity other files reference) falling back to ``path``.
    Entries are mutated in place and also returned. Unresolved references (a
    ``depends_on`` target present in no entry — e.g. an external/cross-repo symbol)
    are left as-is; the extractor's ``coverage`` flag is what records that gap.
    """
    by_module: dict[str, dict] = {}
    by_path: dict[str, dict] = {}
    for e in entries:
        by_path[e["path"]] = e
        if e.get("module"):
            # First writer wins on a shared module name; deterministic by input order.
            by_module.setdefault(e["module"], e)

    for src in entries:
        for target in src["depends_on"]:
            dst = by_module.get(target) or by_path.get(target)
            if dst is None or dst is src:
                continue
            referrer = src.get("module") or src["path"]
            if referrer not in dst["used_by"]:
                dst["used_by"].append(referrer)

    # Keep used_by lists deterministic regardless of discovery order.
    for e in entries:
        e["used_by"] = sorted(dict.fromkeys(e["used_by"]))
    return list(entries)


__all__ = [
    "detect_language",
    "partition_by_language",
    "register_extractor",
    "extractor_for",
    "normalize_entry",
    "normalize",
    "merge_edges",
    "STRUCTURAL_FIELDS",
    "MODEL_FIELDS",
    "RESERVED_FIELDS",
]
