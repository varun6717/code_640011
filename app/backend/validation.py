"""validation.py — §3.1 ``UI_INPUT`` config validator (TASK-050).

The backend accepts posted config and must reject anything that does not conform to
``TECH_SPEC`` §3.1 with a **422 naming the failing field** (TASK-050 acceptance). This
module is the single source of that shape check: it returns a list of human-readable
``field — reason`` strings (empty list == valid). It validates *shape and vocabulary*
only — it is **plumbing, not judgment** (FR-XS-03): it never branches on ``domain``
semantics, never resolves a source, never touches a secret. Deeper failures (a domain
with no registered profile, an unreachable registry) surface later from ``generate.py``
and the build checks, not here.

Kept deliberately dependency-free (stdlib only) so it can be imported by the FastAPI app,
the proof harness, or a CLI without pulling the web stack.
"""
from __future__ import annotations

from typing import Any

# §6.4 / FR-XS-06 — the only two runtime tools the overlays realize.
_RUNTIME_TOOLS = ("claude", "copilot")

# §3.1 ``project_metadata`` block — config-only governance identity (all required).
_PROJECT_METADATA_KEYS = (
    "project_name",
    "application_name",
    "line_of_business",
    "requestor",
    "requestor_sid",
)

# §3.1 ``frame`` — the operator's authoritative seed. title + intent orient BRD authoring;
# scope_hints/stakeholders/key_dates are optional refinements (the author fills the rest).
_FRAME_REQUIRED_KEYS = ("title", "intent")

# Per-source-type required instance fields (§3.1 ``sources[]``, §6.6.2 connector contract).
# Every source carries a ``type``; the rest is what that type's connector needs to locate the
# content. ``auth_ref`` is required for the networked connectors (never inline — §7) and is
# absent only for a direct ``file`` path. Keyed by ``type`` so adding a source type stays a
# pure data edit (no domain fork — D7).
_SOURCE_REQUIRED_FIELDS: dict[str, tuple[str, ...]] = {
    "file": ("path",),
    "bitbucket": ("repo_url", "auth_ref"),
    "sharepoint": ("url", "auth_ref"),
    "confluence": ("url", "auth_ref"),
}


def _is_nonempty_str(value: Any) -> bool:
    return isinstance(value, str) and value.strip() != ""


def validate_ui_input(config: Any) -> list[str]:
    """Validate ``config`` against §3.1. Returns ``[]`` if valid, else ``field — reason`` strings.

    The first element of each message is the dotted field path (e.g. ``sources[1].repo_url``)
    so the API can surface *which* field failed (TASK-050 acceptance: "422 naming the field").
    """
    errors: list[str] = []

    if not isinstance(config, dict):
        return ["config — must be a mapping of §3.1 fields"]

    # run_id is "assigned by Generate" (§3.1) — optional on input (the service assigns one when
    # absent); when present it must be a usable string since it names the run + ledger.
    if "run_id" in config and not _is_nonempty_str(config["run_id"]):
        errors.append("run_id — must be a non-empty string when provided")

    # schema_version pins the contract revision; slice 1 is exactly 1.
    if config.get("schema_version") != 1:
        errors.append("schema_version — must be 1 (§3.1)")

    for field in ("working_path", "domain", "registry_sha"):
        if not _is_nonempty_str(config.get(field)):
            errors.append(f"{field} — required non-empty string (§3.1)")

    runtime_tool = config.get("runtime_tool")
    if runtime_tool not in _RUNTIME_TOOLS:
        errors.append(
            f"runtime_tool — must be one of {list(_RUNTIME_TOOLS)} (FR-XS-06); got {runtime_tool!r}"
        )

    # registry_url / registry_ref are OPTIONAL: when absent, Generate falls back to the env /
    # repo-root registry. When present they must be usable strings (registry_ref = the branch/tag
    # the registry lives on, for a one-repo/two-feature layout).
    for field in ("registry_url", "registry_ref"):
        if field in config and not _is_nonempty_str(config[field]):
            errors.append(f"{field} — must be a non-empty string when provided (§3.1)")

    errors.extend(_validate_project_metadata(config.get("project_metadata")))
    errors.extend(_validate_frame(config.get("frame")))
    errors.extend(_validate_sources(config.get("sources")))
    errors.extend(_validate_gates(config.get("gates")))

    return errors


def _validate_project_metadata(pm: Any) -> list[str]:
    if not isinstance(pm, dict):
        return ["project_metadata — required mapping (§3.1)"]
    return [
        f"project_metadata.{k} — required non-empty string (§3.1)"
        for k in _PROJECT_METADATA_KEYS
        if not _is_nonempty_str(pm.get(k))
    ]


def _validate_frame(frame: Any) -> list[str]:
    if not isinstance(frame, dict):
        return ["frame — required mapping (§3.1)"]
    return [
        f"frame.{k} — required non-empty string (§3.1)"
        for k in _FRAME_REQUIRED_KEYS
        if not _is_nonempty_str(frame.get(k))
    ]


def _validate_sources(sources: Any) -> list[str]:
    if not isinstance(sources, list) or not sources:
        return ["sources — required non-empty list of source descriptors (§3.1)"]

    errors: list[str] = []
    for i, src in enumerate(sources):
        where = f"sources[{i}]"
        if not isinstance(src, dict):
            errors.append(f"{where} — must be a mapping")
            continue
        stype = src.get("type")
        if not _is_nonempty_str(stype):
            errors.append(f"{where}.type — required (§3.1)")
            continue
        required = _SOURCE_REQUIRED_FIELDS.get(stype)
        if required is None:
            errors.append(
                f"{where}.type — unknown source type {stype!r}; "
                f"known: {sorted(_SOURCE_REQUIRED_FIELDS)} (§6.6.2)"
            )
            continue
        errors.extend(
            f"{where}.{field} — required for type {stype!r} (§3.1, §6.6.2)"
            for field in required
            if not _is_nonempty_str(src.get(field))
        )
    return errors


def _validate_gates(gates: Any) -> list[str]:
    if not isinstance(gates, dict):
        return ["gates — required mapping with score_threshold (§3.1, §9)"]
    threshold = gates.get("score_threshold")
    if not isinstance(threshold, int) or isinstance(threshold, bool) or not (0 <= threshold <= 100):
        return ["gates.score_threshold — required integer in [0, 100] (§9)"]
    return []
