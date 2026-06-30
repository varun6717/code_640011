#!/usr/bin/env python3
"""build_checks.py — the five §10 build checks in one runner (FR-DC-09, FR-XS-01/20, NFR-06).

"Author by hand; verify by spec." This runner is the *verify* half: it executes all five
§10 checks over the registered seam and exits non-zero if ANY fails, naming every offender.
It is the build's single green/red signal that the seam is internally consistent before the
spine runs on it.

  §10.1  vocabulary containment   — profile topics + adapter emit-tags (+ code_map) ⊆ V.
                                    (delegated to checks/check_vocab_containment.py, TASK-046)
  §10.2  overlay parity           — both overlays realize every role at the same shared skill.
                                    (delegated to checks/check_overlay_parity.py, TASK-047)
  §10.3  domain artifact presence — the seam files for UI_INPUT.domain exist (jira excluded
                                    this slice — only when L4/Jira is in run scope).
  §10.4  connector coverage       — every UI_INPUT source type has a non-domain-branching
                                    connector (code type → clone.py).
  §10.5  adapter coverage/no-drift— adapter emits ⊆ V; every required topic has a producing
                                    skill; the emit-map agrees per-tag with vocabulary
                                    `emitted_by` (the F1 reconciliation, TASK-017); every
                                    adapter skill file exists.

§10.3/10.4/10.5 are implemented here; §10.1/10.2 reuse the dedicated check modules. Domain
and sources are read from a UI_INPUT (default ``fixtures/UI_INPUT.example.yaml``).
"""
from __future__ import annotations

import ast
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence

import yaml

SCRIPTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS_DIR.parent.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from checks.check_vocab_containment import check_containment            # §10.1
from checks.check_overlay_parity import check_parity                    # §10.2
from checks.check_vocab_containment import adapter_emit_tags, load_vocabulary, profile_topics

# Source types whose connector is the shared git clone (D7 / §10.4 "code type → clone.py").
CODE_SOURCE_TYPES = {"bitbucket"}


@dataclass
class CheckResult:
    name: str
    ok: bool
    violations: list[str] = field(default_factory=list)


# ──────────────────────────────────────────────────────────────────────────────
# §10.3 — domain artifact presence (§6.6.1)
# ──────────────────────────────────────────────────────────────────────────────
def check_domain_artifacts(domain: str, *, jira_in_scope: bool = False,
                           repo_root: Path = REPO_ROOT) -> CheckResult:
    pdir = repo_root / "core" / "profiles" / domain
    required = [
        pdir / f"brd_profile.{domain}.yaml",
        pdir / f"frd_profile.{domain}.yaml",
        pdir / f"vocabulary.{domain}.yaml",
        pdir / "adapter" / "adapter.yaml",
    ]
    if jira_in_scope:   # ONLY when L4 (Jira) is in run scope — out of slice by default
        required.append(repo_root / "core" / "templates" / domain / f"jira_template.{domain}.yaml")
    missing = [str(p.relative_to(repo_root)) for p in required if not p.exists()]
    return CheckResult("§10.3 domain artifacts", not missing,
                       [f"missing seam artifact for domain {domain!r}: {m}" for m in missing])


# ──────────────────────────────────────────────────────────────────────────────
# §10.4 — connector coverage (§6.6.2, D7)
# ──────────────────────────────────────────────────────────────────────────────
def _refs_domain(node: ast.AST) -> bool:
    """True iff the expression subtree references an identifier/attribute named ``domain``."""
    for n in ast.walk(node):
        if isinstance(n, ast.Name) and n.id == "domain":
            return True
        if isinstance(n, ast.Attribute) and n.attr == "domain":
            return True
    return False


def branches_on_domain(path: Path) -> bool:
    """Static, comment-immune check: does the connector BRANCH on ``domain`` (D7 forbids it)?

    Parses the AST and inspects every conditional's test (``if`` / ternary / ``match`` /
    comprehension filter). A connector that merely mentions ``domain`` in a docstring or
    comment is fine; one that *branches* on it is a domain fork (FR-DC-11 violation).
    """
    tree = ast.parse(path.read_text())
    for node in ast.walk(tree):
        if isinstance(node, (ast.If, ast.IfExp)) and _refs_domain(node.test):
            return True
        if isinstance(node, ast.Match) and _refs_domain(node.subject):
            return True
        if isinstance(node, ast.comprehension) and any(_refs_domain(c) for c in node.ifs):
            return True
    return False


def _connector_for(source_type: str, repo_root: Path) -> Path:
    name = "clone.py" if source_type in CODE_SOURCE_TYPES else f"ingest_{source_type}.py"
    return repo_root / "core" / "scripts" / name


def check_connector_coverage(sources: Sequence[dict], *,
                             repo_root: Path = REPO_ROOT) -> CheckResult:
    violations: list[str] = []
    for s in sources:
        stype = s.get("type", "?")
        conn = _connector_for(stype, repo_root)
        if not conn.exists():
            violations.append(f"source type {stype!r}: no connector at "
                              f"{conn.relative_to(repo_root)}")
            continue
        if branches_on_domain(conn):
            violations.append(f"connector {conn.name} branches on `domain` "
                              f"(must be source-type-keyed only, D7)")
    return CheckResult("§10.4 connector coverage", not violations, violations)


# ──────────────────────────────────────────────────────────────────────────────
# §10.5 — adapter coverage + consistency (§6.6.3, D5/FR-DC-09)
# ──────────────────────────────────────────────────────────────────────────────
def _vocab_emitted_by(vocab_path: Path) -> dict[str, set[str]]:
    data = yaml.safe_load(vocab_path.read_text()) or {}
    return {tag: set(meta.get("emitted_by") or [])
            for tag, meta in (data.get("tags") or {}).items()}


def _required_topics(repo_root: Path, domain: str) -> set[str]:
    pdir = repo_root / "core" / "profiles" / domain
    out: set[str] = set()
    for prof in (f"brd_profile.{domain}.yaml", f"frd_profile.{domain}.yaml"):
        data = yaml.safe_load((pdir / prof).read_text()) or {}
        for section in data.get("sections") or []:
            for req in section.get("requirements") or []:
                if req.get("required") and req.get("topic"):
                    out.add(req["topic"])
    return out


def check_adapter_coverage(domain: str = "payment_brand", *,
                           repo_root: Path = REPO_ROOT) -> CheckResult:
    pdir = repo_root / "core" / "profiles" / domain
    adapter_path = pdir / "adapter" / "adapter.yaml"
    A = yaml.safe_load(adapter_path.read_text()) or {}
    emit_map = {t: set(s) for t, s in adapter_emit_tags(adapter_path).items()}  # tag -> {skills}
    vocab = set(load_vocabulary(pdir / f"vocabulary.{domain}.yaml"))
    vocab_emitted = _vocab_emitted_by(pdir / f"vocabulary.{domain}.yaml")

    violations: list[str] = []

    # (a) emits(A) ⊆ V
    for tag in sorted(emit_map):
        if tag not in vocab:
            violations.append(f"adapter emits tag {tag!r} not in vocabulary")

    # (b) every required:true topic has a producing skill in the pack
    for topic in sorted(_required_topics(repo_root, domain)):
        if topic not in emit_map:
            violations.append(f"required topic {topic!r} has no producing adapter skill")

    # (c) per-tag no-drift: adapter emit-map == vocabulary `emitted_by` (F1 reconciliation)
    for tag in sorted(set(emit_map) | set(vocab_emitted)):
        a, v = emit_map.get(tag, set()), vocab_emitted.get(tag, set())
        if a != v:
            violations.append(f"emit-map drift on {tag!r}: adapter={sorted(a)} "
                              f"vs vocabulary.emitted_by={sorted(v)}")

    # (d) every adapter skill file exists. docs_pipeline skills live in the pack dir;
    #     code_pipeline skills are the SHARED core skill (referenced, not copied — D7).
    #     docs_pipeline may be a bare list (legacy = `default`) or a per-type mapping (TASK-063B);
    #     a mapping MUST carry a `default` fallback. Skills are checked across all variants.
    docs = A.get("docs_pipeline")
    if isinstance(docs, dict):
        if "default" not in docs:
            violations.append("docs_pipeline mapping must include a `default` pipeline (TASK-063B)")
        docs_variants = list(docs.values())
    else:
        docs_variants = [docs or []]
    docs_skills = {step.get("skill") for variant in docs_variants for step in (variant or [])
                   if isinstance(step, dict) and step.get("skill")}
    for skill in sorted(docs_skills):
        if not (pdir / "adapter" / f"{skill}.skill.md").exists():
            violations.append(f"missing docs_pipeline skill file: adapter/{skill}.skill.md")
    for step in A.get("code_pipeline") or []:
        skill = step.get("skill")
        if skill and not (repo_root / "core" / "skills" / f"{skill}.skill.md").exists():
            violations.append(f"missing code_pipeline (core) skill file: core/skills/{skill}.skill.md")

    return CheckResult("§10.5 adapter coverage/no-drift", not violations, violations)


# ──────────────────────────────────────────────────────────────────────────────
# Runner — all five
# ──────────────────────────────────────────────────────────────────────────────
def _safe(name: str, fn) -> CheckResult:
    """Run a check, converting any exception (e.g. a missing seam file) into a clean FAIL —
    a build runner reports red, it does not crash on a broken seam."""
    try:
        return fn()
    except Exception as exc:                       # noqa: BLE001 — any failure ⇒ red, named
        return CheckResult(name, False, [f"{type(exc).__name__}: {exc}"])


def run_all(*, ui_input: str | Path | None = None, repo_root: Path = REPO_ROOT,
            jira_in_scope: bool = False, code_map_path: str | Path | None = None) -> list[CheckResult]:
    ui_path = Path(ui_input or (repo_root / "fixtures" / "UI_INPUT.example.yaml"))
    ui = yaml.safe_load(ui_path.read_text()) or {}
    domain = ui.get("domain", "payment_brand")
    sources = ui.get("sources") or []

    def r1():   # §10.1 + §10.2 reuse the dedicated modules; map their violations to strings.
        c = check_containment(domain, repo_root=repo_root, code_map_path=code_map_path)
        return CheckResult("§10.1 vocabulary containment", c.ok, [str(v) for v in c.violations])

    def r2():
        c = check_parity(repo_root=repo_root)
        return CheckResult("§10.2 overlay parity", c.ok, [str(v) for v in c.violations])

    return [
        _safe("§10.1 vocabulary containment", r1),
        _safe("§10.2 overlay parity", r2),
        _safe("§10.3 domain artifacts",
              lambda: check_domain_artifacts(domain, jira_in_scope=jira_in_scope, repo_root=repo_root)),
        _safe("§10.4 connector coverage",
              lambda: check_connector_coverage(sources, repo_root=repo_root)),
        _safe("§10.5 adapter coverage/no-drift",
              lambda: check_adapter_coverage(domain, repo_root=repo_root)),
    ]


def main(argv: Sequence[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Run all five §10 build checks")
    parser.add_argument("--ui-input", default=None, help="UI_INPUT.yaml (default: fixtures example)")
    parser.add_argument("--code-map", default=None, help="optional code_map.json for §10.1")
    parser.add_argument("--jira", action="store_true", help="treat L4/Jira as in scope (§10.3)")
    ns = parser.parse_args(argv)

    results = run_all(ui_input=ns.ui_input, jira_in_scope=ns.jira, code_map_path=ns.code_map)
    failed = [r for r in results if not r.ok]
    for r in results:
        print(f"  [{'PASS' if r.ok else 'FAIL'}] {r.name}")
        for v in r.violations:
            print(f"         - {v}", file=sys.stderr)
    if failed:
        print(f"\nBUILD CHECKS FAILED — {len(failed)}/{len(results)} check(s) red.", file=sys.stderr)
        return 1
    print(f"\nBUILD CHECKS PASSED — all {len(results)} §10 checks green.")
    return 0


# ──────────────────────────────────────────────────────────────────────────────
# Demonstration (TASK-048 fixture/proof — full seam green + each injected-failure red).
# Run: python3 core/scripts/build_checks.py --demo
# ──────────────────────────────────────────────────────────────────────────────
def _demo() -> None:
    import shutil
    import tempfile

    results = run_all()
    print("CLEAN (real seam):")
    for r in results:
        print(f"  [{'PASS' if r.ok else 'FAIL'}] {r.name}"
              + ("" if r.ok else f"  → {r.violations}"))
    assert all(r.ok for r in results), "the real seam must pass all five §10 checks"

    # Injected-failure variants (each check goes red in isolation), against a temp repo copy.
    with tempfile.TemporaryDirectory(prefix="build-checks-") as tmp:
        root = Path(tmp) / "repo"
        shutil.copytree(REPO_ROOT, root, ignore=shutil.ignore_patterns(
            ".git", "__pycache__", "node_modules", "runs"))

        def red(label: str, mutate) -> None:
            fresh = Path(tempfile.mkdtemp(prefix="bc-variant-"))
            shutil.copytree(root, fresh / "r")
            mutate(fresh / "r")
            res = run_all(repo_root=fresh / "r")
            bad = [r.name for r in res if not r.ok]
            print(f"  injected[{label}] → red checks: {bad}")
            assert bad, f"variant {label!r} should have failed at least one check"
            shutil.rmtree(fresh)

        # §10.3 — delete a seam artifact
        red("10.3 missing vocabulary",
            lambda r: (r / "core/profiles/payment_brand/vocabulary.payment_brand.yaml").unlink())
        # §10.4 — connector that branches on domain
        red("10.4 domain-branch connector",
            lambda r: (r / "core/scripts/ingest_file.py").write_text(
                "import sys\n\ndef run(domain):\n    if domain == 'payment_brand':\n        return 1\n    return 0\n"))
        # §10.5 — drift the adapter emit-map (drop a tag from a skill's emits)
        red("10.5 emit-map drift", _drift_adapter)

    print("\nPASS — real seam green on all five §10 checks; each injected variant goes red.")


def _drift_adapter(root: Path) -> None:
    p = root / "core/profiles/payment_brand/adapter/adapter.yaml"
    A = yaml.safe_load(p.read_text())
    A["code_pipeline"][0]["emits"] = [t for t in A["code_pipeline"][0]["emits"] if t != "settlement"]
    p.write_text(yaml.safe_dump(A, sort_keys=False))


if __name__ == "__main__":
    if "--demo" in sys.argv:
        _demo()
    else:
        raise SystemExit(main())
