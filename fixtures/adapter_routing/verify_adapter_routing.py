#!/usr/bin/env python3
"""verify_adapter_routing.py — TASK-063B proof: per-source-type docs_pipeline routing.

Proves the additive per-type routing of `adapter.yaml`'s `docs_pipeline` (§6.6.3 amendment):

  1. **Two doc types → two distinct ordered pipelines.** `type: confluence` routes to the
     `[confluence_tag]` lane; `type: file`/`sharepoint` (and any unknown type) fall back to the
     `default` lane (`pdf_extract → article_summarize`).
  2. **Back-compat (parses identically).** A **bare-list** `docs_pipeline` (legacy form) produces
     the *exact same* emit-map as the equivalent `{default: <list>}` mapping — every existing pack
     stays valid byte-for-byte.
  3. **§10.5 union.** The no-drift emit-map unions across all variants — `error_handling` (code-only
     before) now also carries `confluence_tag`.
  4. **`default` is required.** A mapping `docs_pipeline` with no `default` lane fails §10.5 loudly.
  5. **Real seam green.** `check_adapter_coverage('payment_brand')` passes with the routed form.

Run:  python fixtures/adapter_routing/verify_adapter_routing.py
"""
from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

import yaml

_REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO_ROOT / "core" / "scripts"))
sys.path.insert(0, str(_REPO_ROOT / "core" / "scripts" / "checks"))

from check_vocab_containment import adapter_emit_tags  # noqa: E402
from build_checks import check_adapter_coverage  # noqa: E402

_PDIR = _REPO_ROOT / "core" / "profiles" / "payment_brand"
_ADAPTER = _PDIR / "adapter" / "adapter.yaml"


def select_docs_pipeline(docs, src_type):
    """Reference impl of source_processor's routing: bare list == the pipeline; a mapping →
    docs[src_type] if present, else the required docs['default']. By TYPE, never domain."""
    if isinstance(docs, list):
        return docs
    return docs.get(src_type, docs["default"])


def _check(label, cond):
    print(f"  [{'PASS' if cond else 'FAIL'}] {label}")
    if not cond:
        raise SystemExit(f"verify_adapter_routing: FAILED — {label}")


def _skills(pipeline):
    return [s["skill"] for s in pipeline]


def main() -> int:
    print("verify_adapter_routing.py — TASK-063B docs_pipeline routing proof")
    A = yaml.safe_load(_ADAPTER.read_text())
    docs = A["docs_pipeline"]

    # 1) Two doc types → two distinct ordered pipelines; unknown/sharepoint → default fallback.
    conf = _skills(select_docs_pipeline(docs, "confluence"))
    default = _skills(select_docs_pipeline(docs, "file"))
    _check("confluence lane is the tag-only [confluence_tag]", conf == ["confluence_tag"])
    _check("default lane is the ordered 2-step PDF pipeline (extract + sole tagger)",
           default == ["pdf_extract", "article_summarize"])
    _check("confluence and default are DISTINCT pipelines", conf != default)
    _check("sharepoint falls back to default", _skills(select_docs_pipeline(docs, "sharepoint")) == default)
    _check("unknown type falls back to default", _skills(select_docs_pipeline(docs, "lucid")) == default)

    # 2) Back-compat: a bare-list docs_pipeline parses to the SAME emit-map as {default: <list>}.
    bare_list = [
        {"skill": "pdf_extract", "emits": []},
        {"skill": "article_summarize", "emits": ["brand_rules", "mandate"]},
    ]
    base = {"domain": "x", "code_pipeline": [{"skill": "code_map_build", "emits": ["routing"]}]}
    with tempfile.TemporaryDirectory() as td:
        p_bare = Path(td) / "bare.yaml"
        p_map = Path(td) / "map.yaml"
        p_bare.write_text(yaml.safe_dump({**base, "docs_pipeline": bare_list}))
        p_map.write_text(yaml.safe_dump({**base, "docs_pipeline": {"default": bare_list}}))
        _check("bare-list emit-map == {default: list} emit-map (back-compat)",
               adapter_emit_tags(p_bare) == adapter_emit_tags(p_map))

    # 3) §10.5 union across variants: error_handling now carries confluence_tag (was code-only).
    emap = adapter_emit_tags(_ADAPTER)
    _check("emit-map unions both lanes (error_handling has code_map_build + confluence_tag)",
           emap.get("error_handling") == ["code_map_build", "confluence_tag"])
    _check("confluence_tag emits land in the union (card_brand)",
           "confluence_tag" in emap.get("card_brand", []))

    # 4) & 5) Real seam green; a `default`-less mapping fails loudly — checked on a temp profile copy.
    _check("real payment_brand seam §10.5 green (routed form)",
           check_adapter_coverage("payment_brand", repo_root=_REPO_ROOT).ok)

    with tempfile.TemporaryDirectory() as td:
        troot = Path(td)
        tpdir = troot / "core" / "profiles" / "payment_brand"
        shutil.copytree(_PDIR, tpdir)
        # Mapping with NO `default` → routing has no fallback → must fail §10.5.
        bad = yaml.safe_load(_ADAPTER.read_text())
        bad["docs_pipeline"] = {"file": bad["docs_pipeline"]["default"],
                                "confluence": bad["docs_pipeline"]["confluence"]}
        (tpdir / "adapter" / "adapter.yaml").write_text(yaml.safe_dump(bad))
        res = check_adapter_coverage("payment_brand", repo_root=troot)
        _check("docs_pipeline mapping without `default` fails §10.5", not res.ok)
        _check("the failure names the missing `default`",
               any("default" in v for v in res.violations))

    print("verify_adapter_routing: ALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
