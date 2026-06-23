#!/usr/bin/env python3
"""verify_auth.py — TASK-052 proof: the ``jpmc_adapters`` auth seam resolves and never leaks.

Exercises ``core/adapters/jpmc_adapters/auth.py`` against a **stub secret backend** (no
network, no real store) and asserts the TASK-052 acceptance (FR-DC-12, §7):

  1. ``resolve_auth`` returns usable creds per ``auth_ref`` — a bitbucket and a sharepoint
     pointer each resolve to a handle whose ``reveal()`` is the configured secret.
  2. A **missing** secret fails loud, **named** — ``AuthResolutionError`` mentioning the
     service (not a silent ``None`` that would degrade to anonymous access).
  3. ``None``/absent ``auth_ref`` → ``None`` (the documented ambient/local passthrough).
  4. A malformed / unknown ``auth_ref`` is rejected (namespace + service validated).
  5. **No secret reaches disk.** A descriptor built the way ``clone.py`` builds one is
     written to a temp dir; the resolved secret string appears nowhere under it — only the
     ``auth_ref`` pointer and the handle's redacted ``pointer()`` view do.

Offline + deterministic. Run:  .venv/bin/python fixtures/auth/verify_auth.py
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO_ROOT / "core" / "adapters"))

from jpmc_adapters.auth import (  # noqa: E402
    AuthHandle,
    AuthResolutionError,
    get_backend,
    resolve_auth,
    set_backend,
)

# A secret that is unmistakable if it leaks onto disk.
_BITBUCKET_SECRET = "sekret-bb-TOKEN-9f3a-LEAKCANARY"
_SHAREPOINT_SECRET = "sekret-sp-TOKEN-b21c-LEAKCANARY"


class StubBackend:
    """In-memory secret source — stands in for env vars / the JPMC store."""

    def __init__(self, secrets: dict[str, str]) -> None:
        self._secrets = secrets

    def get(self, key: str) -> str | None:
        return self._secrets.get(key)


def _check(label: str, cond: bool) -> None:
    print(f"  [{'PASS' if cond else 'FAIL'}] {label}")
    if not cond:
        raise SystemExit(f"verify_auth: FAILED — {label}")


def main() -> int:
    print("verify_auth.py — TASK-052 auth seam proof")
    saved = get_backend()
    set_backend(StubBackend({"bitbucket": _BITBUCKET_SECRET, "sharepoint": _SHAREPOINT_SECRET}))
    try:
        # 1. usable creds per auth_ref
        bb = resolve_auth("jpmc_adapters:bitbucket")
        sp = resolve_auth("jpmc_adapters:sharepoint")
        _check("bitbucket auth_ref resolves to an AuthHandle", isinstance(bb, AuthHandle))
        _check("sharepoint auth_ref resolves to an AuthHandle", isinstance(sp, AuthHandle))
        _check("bitbucket handle reveals the configured secret", bb.reveal() == _BITBUCKET_SECRET)
        _check("sharepoint handle reveals the configured secret", sp.reveal() == _SHAREPOINT_SECRET)

        # 2. missing secret fails loud, named
        try:
            resolve_auth("jpmc_adapters:confluence")  # not in the stub
            _check("missing secret raises AuthResolutionError", False)
        except AuthResolutionError as exc:
            _check("missing secret raises AuthResolutionError", True)
            _check("error names the service ('confluence')", "confluence" in str(exc))

        # 3. ambient passthrough
        _check("None auth_ref → None (ambient/local passthrough)", resolve_auth(None) is None)
        _check("empty auth_ref → None (ambient/local passthrough)", resolve_auth("") is None)

        # 4. malformed / unknown rejected
        for bad in ("bitbucket", "jpmc_adapters:github", "github:bitbucket"):
            try:
                resolve_auth(bad)
                _check(f"malformed auth_ref {bad!r} rejected", False)
            except AuthResolutionError:
                _check(f"malformed auth_ref {bad!r} rejected", True)

        # 5. no secret reaches disk — mirror clone.py's descriptor + log the redacted handle
        with tempfile.TemporaryDirectory() as td:
            workspace = Path(td)
            descriptor = {
                "type": "bitbucket",
                "repo_url": "https://bitbucket.example/team/repo.git",
                "auth_ref": "jpmc_adapters:bitbucket",  # pointer only (FR-DC-12)
                "commit_sha": "deadbeef",
            }
            (workspace / "source_descriptor.json").write_text(
                json.dumps(descriptor, indent=2), encoding="utf-8"
            )
            # Simulate a careless caller logging the handle and recording its pointer view.
            (workspace / "ledger.jsonl").write_text(
                json.dumps({"event": "auth_resolved", "handle": str(bb), "pointer": bb.pointer()}) + "\n",
                encoding="utf-8",
            )

            leaked = []
            for p in workspace.rglob("*"):
                if p.is_file():
                    blob = p.read_text(encoding="utf-8", errors="ignore")
                    if _BITBUCKET_SECRET in blob or _SHAREPOINT_SECRET in blob:
                        leaked.append(p.name)
            _check("no resolved secret found anywhere under the workspace", not leaked)
            _check(
                "auth_ref pointer IS recorded (so the seam is auditable)",
                "jpmc_adapters:bitbucket" in (workspace / "source_descriptor.json").read_text(),
            )
            _check("handle repr/str is redacted", _BITBUCKET_SECRET not in str(bb) and "REDACTED" in str(bb))
    finally:
        set_backend(saved)

    print("verify_auth: ALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
