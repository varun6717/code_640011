#!/usr/bin/env python3
"""§10.1 vocabulary-containment build check (D5, FR-DC-08 / FR-DC-09) — deterministic.

The hard, model-free containment gate: every concept the seam *uses* must already be a
tag in the frozen domain vocabulary. It is the opposite direction of the adequacy
detector (``vocab_adequacy.py``), which catches a concept the model could not tag; this
catches a topic/tag that escaped the dictionary — i.e. tag *invention*. A single
offender fails the build loudly (FR-DC-09) rather than silently mis-routing a section.

§10.1 (verbatim):

    load V = vocabulary.<domain>.yaml (the canonical tag set)
    assert topics(brd_profile.<domain>) ⊆ V
    assert topics(frd_profile.<domain>) ⊆ V
    assert tags(code_map.json)          ⊆ V         # checked when a map exists
    FAIL → name the offending topic/tag and the file.

This check also asserts every tag in the adapter emit-map (``adapter.yaml`` ``emits``)
∈ V — the third producer of vocabulary tags, kept in scope by FR-DC-09 / the TASK-046
``Do`` ("every tag emitted by adapter skills ∈ vocabulary"). (The complementary §10.5
checks the emit-map *agrees per-tag* with the vocabulary ``emitted_by`` column; here we
only assert containment.)

``topics`` is IMPLICIT in the profiles (the distinct set of ``sections[].requirements[]
.topic`` — there is no standalone ``topics:`` field, FR-BR-10). The loader reads the
canonical ``vocabulary.<domain>.yaml`` from disk (NOT the in-code D5 stub in
``core.extractors``) — this is the file-based cross-check that loader's docstring defers
to TASK-046. Generic over ``domain`` (FR-XS-01): paths are derived from the domain alone.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Mapping, Sequence

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]


def _profile_dir(domain: str, *, repo_root: Path = REPO_ROOT) -> Path:
    return repo_root / "core" / "profiles" / domain


# ──────────────────────────────────────────────────────────────────────────────
# Loaders — each returns a {item -> sorted locations} map so a violation can name
# the offending topic/tag AND where it was used (§10.1 "name the … and the file").
# ──────────────────────────────────────────────────────────────────────────────
def load_vocabulary(path: str | Path) -> frozenset[str]:
    """Return the canonical tag set V = keys of ``vocabulary.<domain>.yaml`` ``tags:``."""
    data = yaml.safe_load(Path(path).read_text()) or {}
    tags = data.get("tags") or {}
    if not isinstance(tags, Mapping):
        raise ValueError(f"{path}: `tags:` must be a mapping of tag -> definition")
    return frozenset(tags)


def profile_topics(path: str | Path) -> dict[str, list[str]]:
    """Map each ``sections[].requirements[].topic`` → the section ids that reference it.

    ``topics`` is the IMPLICIT distinct set of requirement topics (FR-BR-10) — there is
    no standalone ``topics:`` field to read.
    """
    data = yaml.safe_load(Path(path).read_text()) or {}
    out: dict[str, list[str]] = {}
    for section in data.get("sections") or []:
        sid = section.get("id", "?")
        for req in section.get("requirements") or []:
            topic = req.get("topic")
            if topic is not None:
                out.setdefault(topic, []).append(sid)
    return {t: sorted(set(locs)) for t, locs in out.items()}


def _pipeline_step_lists(data: Mapping) -> list[list]:
    """Every ordered step-list in an ``adapter.yaml``: bare top-level lists (``code_pipeline``,
    and a bare-list ``docs_pipeline``) AND the per-type variant lists inside a routed
    ``docs_pipeline`` mapping (``{default: [...], <type>: [...]}``, TASK-063B). Scalars like
    ``domain:`` are skipped. Back-compatible — a bare list is still one pipeline."""
    lists: list[list] = []
    for val in data.values():
        if isinstance(val, list):
            lists.append(val)
        elif isinstance(val, Mapping):                # routed docs_pipeline: union all variants
            for sub in val.values():
                if isinstance(sub, list):
                    lists.append(sub)
    return lists


def adapter_emit_tags(path: str | Path) -> dict[str, list[str]]:
    """Map each tag in any pipeline skill's ``emits`` → the skills that emit it.

    Unions across every pipeline AND every per-type variant of a routed ``docs_pipeline``
    (TASK-063B): a bare list is the legacy ``default`` form; a mapping keyed by source type
    contributes all variants' ``emits`` to the union, so §10.1/§10.5 see every producer."""
    data = yaml.safe_load(Path(path).read_text()) or {}
    out: dict[str, list[str]] = {}
    for pipeline in _pipeline_step_lists(data):
        for step in pipeline:
            if not isinstance(step, Mapping):
                continue
            skill = step.get("skill", "?")
            for tag in step.get("emits") or []:
                out.setdefault(tag, []).append(skill)
    return {t: sorted(set(s)) for t, s in out.items()}


def code_map_tags(path: str | Path) -> dict[str, list[str]]:
    """Map each tag in ``code_map.json`` ``files[].tags`` → the file paths carrying it."""
    import json

    data = json.loads(Path(path).read_text())
    out: dict[str, list[str]] = {}
    for entry in data.get("files") or []:
        fpath = entry.get("path", "?")
        for tag in entry.get("tags") or []:
            out.setdefault(tag, []).append(fpath)
    return {t: sorted(set(p)) for t, p in out.items()}


# ──────────────────────────────────────────────────────────────────────────────
# Containment
# ──────────────────────────────────────────────────────────────────────────────
@dataclass(frozen=True)
class Violation:
    source: str                     # the file/artifact the offender came from
    item: str                       # the offending topic or tag
    kind: str                       # "topic" | "tag"
    locations: tuple[str, ...]      # where in the source it was used

    def __str__(self) -> str:
        where = ", ".join(self.locations) if self.locations else "—"
        return f"{self.source}: {self.kind} {self.item!r} ∉ vocabulary (used in: {where})"


@dataclass
class ContainmentResult:
    vocabulary: frozenset[str]
    violations: list[Violation] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.violations


def contain(
    items_by_loc: Mapping[str, Sequence[str]],
    vocabulary: Iterable[str],
    *,
    source: str,
    kind: str,
) -> list[Violation]:
    """Pure: every key of ``items_by_loc`` must be ∈ ``vocabulary``; name any that isn't."""
    V = frozenset(vocabulary)
    return [
        Violation(source=source, item=item, kind=kind, locations=tuple(locs))
        for item, locs in sorted(items_by_loc.items())
        if item not in V
    ]


def check_containment(
    domain: str = "payment_brand",
    *,
    repo_root: Path = REPO_ROOT,
    code_map_path: str | Path | None = None,
) -> ContainmentResult:
    """Run §10.1 over the real seam for ``domain``. Pure — computes, never writes.

    Asserts profile topics (BRD + FRD) and adapter emit-tags ⊆ V, plus ``code_map.json``
    tags ⊆ V when a map path is supplied (§10.1 "checked when a map exists"). Returns a
    :class:`ContainmentResult`; the caller (CLI / ``build_checks.py``) decides exit code.
    """
    pdir = _profile_dir(domain, repo_root=repo_root)
    vocab = load_vocabulary(pdir / f"vocabulary.{domain}.yaml")

    violations: list[Violation] = []
    violations += contain(
        profile_topics(pdir / f"brd_profile.{domain}.yaml"),
        vocab, source=f"brd_profile.{domain}.yaml", kind="topic",
    )
    violations += contain(
        profile_topics(pdir / f"frd_profile.{domain}.yaml"),
        vocab, source=f"frd_profile.{domain}.yaml", kind="topic",
    )
    violations += contain(
        adapter_emit_tags(pdir / "adapter" / "adapter.yaml"),
        vocab, source="adapter.yaml", kind="tag",
    )
    if code_map_path is not None:
        violations += contain(
            code_map_tags(code_map_path),
            vocab, source=str(code_map_path), kind="tag",
        )
    return ContainmentResult(vocabulary=vocab, violations=violations)


def main(argv: Sequence[str] | None = None) -> int:
    """CLI: run §10.1 on the real seam; exit non-zero (and name offenders) on any failure."""
    import argparse

    parser = argparse.ArgumentParser(description="§10.1 vocabulary-containment check")
    parser.add_argument("--domain", default="payment_brand")
    parser.add_argument("--code-map", default=None,
                        help="optional path to a code_map.json to also check")
    ns = parser.parse_args(argv)

    result = check_containment(ns.domain, code_map_path=ns.code_map)
    if result.ok:
        print(f"§10.1 PASS — {ns.domain}: all profile topics + adapter emit-tags"
              f"{' + code_map tags' if ns.code_map else ''} ⊆ vocabulary "
              f"({len(result.vocabulary)} tags).")
        return 0
    print(f"§10.1 FAIL — {ns.domain}: {len(result.violations)} containment violation(s):",
          file=sys.stderr)
    for v in result.violations:
        print(f"  - {v}", file=sys.stderr)
    return 1


# ──────────────────────────────────────────────────────────────────────────────
# Demonstration (TASK-046 fixture/proof). Run: python3 core/scripts/checks/check_vocab_containment.py --demo
#   - CLEAN: the real payment_brand seam → NO violation (acceptance: passes on the seam).
#   - CRAFTED: a bad-topic profile variant (a topic NOT in the vocabulary) → flagged,
#     naming the offending topic and the file (acceptance: fails on an injected out-of-
#     vocab topic). Same proof shape as assert_tags_in_vocabulary (TASK-011).
# ──────────────────────────────────────────────────────────────────────────────
def _demo() -> None:
    clean = check_containment("payment_brand")
    print("CLEAN  (real payment_brand seam):")
    print(f"  vocabulary={len(clean.vocabulary)} tags  violations={clean.violations}")
    assert clean.ok, f"real seam must be containment-clean; got {clean.violations}"

    vocab = clean.vocabulary
    injected = {
        "mandate": ["business_context"],          # real topic — must pass
        "tokenization": ["scope_objectives"],     # NOT in the 12-tag D5 set — must flag
    }
    bad = contain(injected, vocab,
                  source="brd_profile.payment_brand.yaml (injected)", kind="topic")
    print("\nCRAFTED (injected out-of-vocab topic 'tokenization'):")
    for v in bad:
        print(f"  VIOLATION {v}")
    assert any(v.item == "tokenization" for v in bad), \
        "the injected out-of-vocab topic must be flagged"
    assert all(v.item != "mandate" for v in bad), "a real topic must not be flagged"
    assert "scope_objectives" in bad[0].locations, "the violation must name the file/location"
    print("\nPASS — real seam contained; injected out-of-vocab topic flagged with its location.")


if __name__ == "__main__":
    if "--demo" in sys.argv:
        _demo()
    else:
        raise SystemExit(main())
