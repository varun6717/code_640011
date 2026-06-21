#!/usr/bin/env python3
"""clone.py — the code-source ingestion connector (Bitbucket → ``repo/``), §6.6.2.

Generic and **source-type-keyed** (D7 / FR-DC-11): this is the connector for code
sources (``type: bitbucket``). "Ingest" for code = **git clone** the SEAL-ID repo into
the run's ``repo/`` (FR-DC-02), pinned by the resolved ``commit_sha`` so the run is
reproducible (NFR-01 — the repo is pinned by ``commit_sha`` recorded at clone time).
The cloned tree is then handed to ``code_map_build`` via the adapter ``code_pipeline``
(§6.6.3). This script is the code analogue of the document connectors (``ingest_<type>.py``);
§10.4 maps every ``code`` source type to ``clone.py``.

Contract (§6.6.2):
  consumes : a ``UI_INPUT.sources[]`` entry of ``type: bitbucket`` (``repo_url``,
             ``seal_id``, ``auth_ref``) + auth via the seam (``auth_ref``, never an
             inline secret — FR-DC-12).
  produces : the repo staged on disk under ``repo/``; returns / prints a JSON source
             descriptor including the pinned ``commit_sha`` (NFR-01).

**Never branches on ``domain`` (D7).** This script does not read ``domain`` at all —
ingestion is identical for every domain; a new source type is one new connector in
``core/scripts/``, never a domain fork (FR-DC-11).

**Auth (FR-DC-12).** Per-instance auth is referenced by ``auth_ref`` (e.g.
``jpmc_adapters:bitbucket``) and resolved at the push/auth seam (§7); the secret never
appears here or in any artifact. ``auth_ref`` is recorded in the descriptor as a
**pointer only**. This external validation build clones over ambient git credentials /
local paths, so seam resolution is a documented passthrough (the VDI port wires the real
secret store behind the same ``auth_ref``).

**External-build convenience.** If ``repo_url`` is a local directory that is *not* a git
repo (e.g. the plain-dir ``fixtures/c_repo``), a tree copy stages it into ``repo/`` with
``commit_sha: null`` and a note — so the slice can be exercised end-to-end here without
forcing fixtures into git. A real URL / local git repo always takes the ``git clone`` path.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SOURCE_TYPE = "bitbucket"          # the source type this connector serves (source-type-keyed, D7)


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def resolve_auth(auth_ref: str | None) -> None:
    """Resolve per-instance auth at the seam (§7 / FR-DC-12). Pointer in, no secret out.

    ``auth_ref`` (e.g. ``jpmc_adapters:bitbucket``) points at the push/auth seam; the
    secret is resolved there and NEVER returned to or logged by the connector. In this
    external build there is no secret store, so resolution is a passthrough returning
    ``None`` (ambient git credentials / local paths). The VDI port binds the real store
    behind the same ``auth_ref`` without touching this connector.
    """
    return None


def _git(args: list[str], cwd: Path | None = None) -> str:
    """Run a git command, returning stripped stdout; raises on non-zero (with stderr)."""
    proc = subprocess.run(
        ["git", *args],
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {proc.stderr.strip()}")
    return proc.stdout.strip()


def clone_repo(
    repo_url: str,
    dest: str | Path,
    *,
    ref: str | None = None,
    seal_id: str | None = None,
    auth_ref: str | None = None,
    ts: str | None = None,
) -> dict:
    """Clone ``repo_url`` into ``dest`` and return a §6.6.2 source descriptor.

    ``git clone`` by default; if ``ref`` is given a full clone is used so the ref can be
    checked out. ``commit_sha`` is read back via ``git rev-parse HEAD`` and recorded for
    reproducibility (NFR-01). If ``repo_url`` is a local non-git directory, the tree is
    copied (external-build convenience) and ``commit_sha`` is ``null``. ``dest`` must not
    already exist (a run starts from a clean ``repo/``).
    """
    resolve_auth(auth_ref)                                  # seam passthrough; no secret returned
    dest = Path(dest)
    if dest.exists() and any(dest.iterdir()):
        raise FileExistsError(f"clone dest already populated: {dest} (a run clones into a clean repo/)")
    dest.parent.mkdir(parents=True, exist_ok=True)

    note: str | None = None
    src = Path(repo_url)
    is_local_nongit = src.exists() and src.is_dir() and not (src / ".git").exists()

    if is_local_nongit:
        # External-build convenience: stage a plain local tree (e.g. fixtures/c_repo).
        shutil.copytree(src, dest)
        commit_sha = None
        note = "local non-git directory staged by tree copy (external build); commit_sha unavailable"
    else:
        if ref:
            _git(["clone", repo_url, str(dest)])
            _git(["checkout", ref], cwd=dest)
        else:
            _git(["clone", "--depth", "1", repo_url, str(dest)])
        commit_sha = _git(["rev-parse", "HEAD"], cwd=dest)

    descriptor = {
        "type": SOURCE_TYPE,
        "seal_id": seal_id,
        "repo_url": repo_url,
        "dest": str(dest),
        "ref": ref,
        "commit_sha": commit_sha,          # NFR-01: pins the repo for reproducibility
        "auth_ref": auth_ref,              # pointer only — never the secret (FR-DC-12)
        "ingest_ts": ts or _now_iso(),
    }
    if note:
        descriptor["note"] = note
    return descriptor


def _source_from_ui_input(ui_input_path: str | Path) -> dict:
    """Load the single ``type: bitbucket`` source entry from a ``UI_INPUT.yaml`` (§3.1)."""
    import yaml  # local import: only the UI-INPUT path needs YAML

    cfg = yaml.safe_load(Path(ui_input_path).read_text(encoding="utf-8"))
    matches = [s for s in (cfg.get("sources") or []) if s.get("type") == SOURCE_TYPE]
    if not matches:
        raise ValueError(f"no source of type {SOURCE_TYPE!r} in {ui_input_path}")
    if len(matches) > 1:
        raise ValueError(f"slice-1 expects one {SOURCE_TYPE} source; found {len(matches)} in {ui_input_path}")
    return matches[0]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Code-source connector: git clone a Bitbucket repo into repo/ (§6.6.2).")
    ap.add_argument("--ui-input", help="path to UI_INPUT.yaml; pulls the single type:bitbucket source entry")
    ap.add_argument("--repo-url", help="repo URL or local git path (overrides UI_INPUT)")
    ap.add_argument("--dest", default="repo", help="clone destination (default: repo/)")
    ap.add_argument("--ref", help="branch/tag/commit to check out (default: clone HEAD)")
    ap.add_argument("--seal-id", help="SEAL ID for provenance (else from UI_INPUT)")
    ap.add_argument("--auth-ref", help="auth seam pointer, e.g. jpmc_adapters:bitbucket (else from UI_INPUT)")
    args = ap.parse_args(argv)

    repo_url, seal_id, auth_ref = args.repo_url, args.seal_id, args.auth_ref
    if args.ui_input:
        entry = _source_from_ui_input(args.ui_input)
        repo_url = repo_url or entry.get("repo_url")
        seal_id = seal_id or entry.get("seal_id")
        auth_ref = auth_ref or entry.get("auth_ref")
    if not repo_url:
        ap.error("need --repo-url or --ui-input with a type:bitbucket source")

    try:
        descriptor = clone_repo(
            repo_url, args.dest, ref=args.ref, seal_id=seal_id, auth_ref=auth_ref,
        )
    except (RuntimeError, FileExistsError, ValueError) as exc:
        print(f"clone.py: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(descriptor, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
