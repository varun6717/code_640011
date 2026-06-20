"""Frozen C extractor — tree-sitter-c → structural fields only (TASK-009).

The deterministic, model-free structural extractor for the C language (TECH_SPEC
§5.5, FR-DC-15/FR-DC-17). Toolchain is **tree-sitter + tree-sitter-c per ADR-001**
(replacing the original ctags/cscope plan): a pure-pip, in-policy parser that runs
inside the already-allowed ``python.exe`` on the AppLocker-locked VDI and is
identical in both the external build and the VDI (§5.7 port check = "import
succeeds in the venv").

Division of labor (frozen here in code, never model-rewritten at runtime):

  - This extractor owns the **structural fields only**:
    ``path / module / interfaces / depends_on / coverage`` and a ``coverage_report``.
  - ``used_by`` is left empty — the deterministic ``merge_edges`` closure (TASK-011)
    fills it from the collected ``depends_on`` (§5.5; the oracle's populated
    ``used_by`` is the *post-merge* map, not raw extractor output).
  - ``purpose`` + ``tags`` are the **model's** sole territory (TASK-011); this
    extractor never sets them.

Input contract (ADR-002): ``run(files, repo_root)`` is handed the **C-language
partition** — the list of repo-relative C file paths the dispatcher routed here —
*not* a self-glob of the repo. Output is one raw entry per file plus the aggregate
``coverage_report``; ``core.extractors.normalize`` maps each raw entry to the §3.3
file-entry shape.

Blind spots are reported, never hidden. tree-sitter is purely syntactic, so it has
the same fundamental blind spots as ctags/cscope on the six designed hazards
(function-pointer table dispatch, callback-registered vtables, computed/opaque
dispatch, codec-table dispatch, macro-generated functions, ``#ifdef``/vendor
escapes). Each is detected structurally, marks the file ``coverage: coarse``, and
contributes an ``unresolved_patterns`` line — per ADR-001 a macro that generates a
function surfaces as a detectable ``ERROR`` node, a *positive* signal rather than a
silent omission.
"""

from __future__ import annotations

import os
from typing import Optional, Sequence

import tree_sitter_c
from tree_sitter import Language, Node, Parser

# Frozen toolchain handle. Built once per process; the grammar is immutable.
_C_LANGUAGE = Language(tree_sitter_c.language())
_PARSER = Parser(_C_LANGUAGE)

_C_SOURCE_EXTS = (".c",)
_C_HEADER_EXTS = (".h",)


# ──────────────────────────────────────────────────────────────────────────────
# Path → module / identity (the cross-file reference scheme the oracle uses).
#   module   = the coarse bucket shown in code_map (`routing`, `settlement`, …).
#   identity = `module/stem` — how one file names another in depends_on/used_by
#              (e.g. a call into reconciler.c becomes the edge `settlement/reconciler`).
# ──────────────────────────────────────────────────────────────────────────────

def _parts(rel_path: str) -> list[str]:
    return rel_path.replace("\\", "/").split("/")


def _module_of(rel_path: str) -> str:
    parts = _parts(rel_path)
    head = parts[0].lower()
    if head == "include":
        return "shared"            # cross-module contract headers
    if head == "vendor":
        return "vendor"            # out-of-tree shim
    if head == "src" and len(parts) >= 3:
        return parts[1]            # src/<module>/<file>
    # Fallback: the immediate parent directory, or "" for a bare top-level file.
    return parts[-2] if len(parts) >= 2 else ""


def _stem(rel_path: str) -> str:
    return os.path.splitext(_parts(rel_path)[-1])[0]


def _identity_of(rel_path: str) -> str:
    """`module/stem` — the token other files use to reference this one (the
    depends_on/used_by edge key; no extension)."""
    return f"{_module_of(rel_path)}/{_stem(rel_path)}"


def _hazard_ref(rel_path: str) -> str:
    """`module/file.c` — how a hazard names its file in unresolved_patterns
    (module-relative, *with* extension), matching the oracle's phrasing."""
    return f"{_module_of(rel_path)}/{os.path.basename(rel_path)}"


# ──────────────────────────────────────────────────────────────────────────────
# CST helpers.
# ──────────────────────────────────────────────────────────────────────────────

def _text(node: Node, src: bytes) -> str:
    return src[node.start_byte:node.end_byte].decode("utf-8", "replace")


def _find_function_declarator(node: Optional[Node]) -> Optional[Node]:
    """Descend a declarator subtree to the ``function_declarator`` (skips the
    ``pointer_declarator`` wrapper of pointer-returning functions)."""
    if node is None:
        return None
    if node.type == "function_declarator":
        return node
    decl = node.child_by_field_name("declarator")
    found = _find_function_declarator(decl)
    if found is not None:
        return found
    for child in node.children:
        if child.type in ("function_declarator", "pointer_declarator", "parenthesized_declarator"):
            found = _find_function_declarator(child)
            if found is not None:
                return found
    return None


def _declarator_identifier(node: Optional[Node]) -> Optional[Node]:
    """Innermost ``identifier`` of a declarator subtree (the declared name)."""
    if node is None:
        return None
    if node.type == "identifier":
        return node
    decl = node.child_by_field_name("declarator")
    if decl is not None:
        found = _declarator_identifier(decl)
        if found is not None:
            return found
    for child in node.children:
        found = _declarator_identifier(child)
        if found is not None:
            return found
    return None


def _is_static(node: Node) -> bool:
    """True if a definition/declaration carries the ``static`` storage class."""
    for child in node.children:
        if child.type == "storage_class_specifier" and child.text == b"static":
            return True
    return False


def _signature(func_decl: Node, src: bytes) -> Optional[str]:
    """``name(p1, p2)`` — function name + parameter *identifier* names. ``void``
    and unnamed/abstract parameters contribute nothing."""
    name_node = _declarator_identifier(func_decl.child_by_field_name("declarator"))
    if name_node is None:
        return None
    name = _text(name_node, src)
    params: list[str] = []
    plist = func_decl.child_by_field_name("parameters")
    if plist is not None:
        for p in plist.children:
            if p.type != "parameter_declaration":
                continue
            pid = _declarator_identifier(p.child_by_field_name("declarator"))
            if pid is not None:
                params.append(_text(pid, src))
    return f"{name}({', '.join(params)})"


def _walk(node: Node):
    stack = [node]
    while stack:
        n = stack.pop()
        yield n
        stack.extend(reversed(n.children))


# Preprocessor conditionals (`#ifndef` include guards, `#ifdef` blocks) are
# transparent containers for declaration discovery: a header wraps its whole API
# in an include guard, so the real prototypes live one level down. This flattens
# translation-unit children, descending through preproc conditionals.
_PREPROC_BLOCKS = ("preproc_ifdef", "preproc_if", "preproc_elif", "preproc_else")


def _toplevel(node: Node):
    for c in node.children:
        if c.type in _PREPROC_BLOCKS:
            yield from _toplevel(c)
        else:
            yield c


def _function_name(func_def: Node, src: bytes) -> Optional[str]:
    fd = _find_function_declarator(func_def.child_by_field_name("declarator"))
    if fd is None:
        return None
    name_node = _declarator_identifier(fd.child_by_field_name("declarator"))
    return _text(name_node, src) if name_node is not None else None


# ──────────────────────────────────────────────────────────────────────────────
# Pass 1 — global symbol table: non-static function *definitions* across the
# partition, mapping symbol → defining file identity. This is what resolves a
# direct call into a cross-file ``depends_on`` edge. Static (file-local) and
# header-only declarations are intentionally absent — a call resolving to neither
# is an external/macro/indirect reference, not an edge.
# ──────────────────────────────────────────────────────────────────────────────

def _definitions(tree_root: Node, src: bytes) -> list[tuple[str, bool]]:
    """[(name, is_static)] for every top-level function *definition* in a file."""
    out: list[tuple[str, bool]] = []
    for child in _toplevel(tree_root):
        if child.type != "function_definition":
            continue
        name = _function_name(child, src)
        if name is not None:
            out.append((name, _is_static(child)))
    return out


def _source_interfaces(tree_root: Node, src: bytes) -> list[str]:
    """Public interface of a ``.c`` file: non-static function *definitions* only
    (in document order). Forward declarations of functions defined elsewhere are
    ``declaration`` nodes, so they are excluded by construction."""
    out: list[str] = []
    for child in _toplevel(tree_root):
        if child.type != "function_definition" or _is_static(child):
            continue
        fd = _find_function_declarator(child.child_by_field_name("declarator"))
        sig = _signature(fd, src) if fd is not None else None
        if sig is not None:
            out.append(sig)
    return out


def _prototypes(tree_root: Node, src: bytes) -> list[str]:
    """Function-prototype signatures for a header — top-level ``declaration``
    nodes whose declarator is a ``function_declarator`` (descending through the
    include guard). Excludes variable declarations and function-pointer typedefs
    (the latter parse as ``type_definition``, not ``declaration``)."""
    out: list[str] = []
    for child in _toplevel(tree_root):
        if child.type != "declaration" or _is_static(child):
            continue
        fd = _find_function_declarator(child.child_by_field_name("declarator"))
        if fd is None:
            continue
        sig = _signature(fd, src)
        if sig is not None:
            out.append(sig)
    return out


# ──────────────────────────────────────────────────────────────────────────────
# Hazard detection (the blind-spot signals → coverage bucket + unresolved_patterns).
#
# Three buckets (PATTERN_CATALOG §2):
#   extracted   — complete structural entry; no stored-pointer/computed/invisible gap.
#   fallback    — structure fine, but a *stored* fn-ptr binds to a known in-tree
#                 target the map ought to link but cannot.
#   unresolved  — the file's own declared structure is invisible/broken
#                 (macro-generated defs, vendor/#ifdef escape, computed/opaque target).
#
# A plain parameter callback (e.g. retry.c's `op(ctx)`) is NOT a hazard: there is
# no concrete in-tree target the map should have linked (PATTERN_CATALOG note).
# ──────────────────────────────────────────────────────────────────────────────

_EXTRACTED, _FALLBACK, _UNRESOLVED = "extracted", "fallback", "unresolved"


def _vendor_name(include_path: str) -> str:
    """`../../vendor/stratus/x.h` → `Stratus` (title-cased vendor segment)."""
    segs = [s for s in include_path.strip('"<>').replace("\\", "/").split("/") if s and s != ".."]
    for i, seg in enumerate(segs):
        if seg.lower() == "vendor" and i + 1 < len(segs):
            return segs[i + 1].capitalize()
    return "vendor"


def _local_var_names(func_def: Node) -> set[str]:
    """Names of variables declared *in the body* of a function (not parameters)."""
    body = func_def.child_by_field_name("body")
    names: set[str] = set()
    if body is None:
        return names
    for n in _walk(body):
        if n.type == "declaration":
            ident = _declarator_identifier(n.child_by_field_name("declarator"))
            if ident is not None:
                names.add(ident.text.decode())
    return names


def _classify(rel_path: str, root: Node, src: bytes, defined_symbols: set[str]) -> tuple[str, Optional[str]]:
    """Return (bucket, unresolved_pattern|None) for one C source file.

    Detectors are structural, evaluated in priority order so the strongest
    defect wins. ``identity`` is the file's ``module/stem`` so the pattern reads
    in code-map terms, matching how the oracle names the hazard.
    """
    ref = _hazard_ref(rel_path)

    # (U-a) Macro that generates a whole function → unexpanded invocation surfaces
    #       as an ERROR node (ADR-001). The generated symbols are invisible.
    error_node = next((n for n in _walk(root) if n.type == "ERROR" or n.is_error), None)
    if error_node is not None:
        macro = next((_text(c, src) for c in _walk(error_node) if c.type == "identifier"), "MACRO")
        return _UNRESOLVED, f"macro-generated functions in {ref} ({macro} token-paste)"

    # (U-b) Include that escapes the index roots (a `..` vendor path), compounded
    #       by #ifdef-gated registration → vendor symbols never seen by the index.
    escaping = None
    has_ifdef = False
    for n in _walk(root):
        if n.type in ("preproc_ifdef", "preproc_if"):
            has_ifdef = True
        if n.type == "preproc_include":
            p = n.child_by_field_name("path")
            if p is not None and ".." in _text(p, src):
                escaping = _text(p, src)
    if escaping is not None:
        vendor = _vendor_name(escaping)
        gate = "#ifdef-gated registration + " if has_ifdef else ""
        return _UNRESOLVED, f"{gate}non-standard {vendor} include in {ref}"

    # Indirect-call analysis. For every fn-ptr *variable*, record the RHS node
    # kinds it was bound from and (for table reads) the RHS text; collect the
    # resolved direct calls that feed an opaque pointer. First hazard wins so the
    # description names the primary dispatch site, not a secondary one.
    computed_pattern: Optional[str] = None    # opaque/computed target  → unresolved
    stored_pattern: Optional[str] = None      # stored fn-ptr to in-tree → fallback

    assign_kinds: dict[str, set[str]] = {}
    assign_text: dict[str, str] = {}          # the table-read access, e.g. g_codecs[field].encode
    source_calls: list[str] = []              # resolved direct calls (opaque-ptr source)
    for n in _walk(root):
        if n.type in ("init_declarator", "assignment_expression"):
            lhs = n.child_by_field_name("declarator" if n.type == "init_declarator" else "left")
            rhs = n.child_by_field_name("value" if n.type == "init_declarator" else "right")
            ident = _declarator_identifier(lhs) if n.type == "init_declarator" else lhs
            if ident is not None and ident.type == "identifier" and rhs is not None:
                name = ident.text.decode()
                assign_kinds.setdefault(name, set()).add(rhs.type)
                if rhs.type in ("subscript_expression", "field_expression") and name not in assign_text:
                    assign_text[name] = _text(rhs, src)
        elif n.type == "call_expression":
            fn = n.child_by_field_name("function")
            if fn is not None and fn.type == "identifier" and fn.text.decode() in defined_symbols:
                source_calls.append(fn.text.decode())

    for n in _walk(root):
        if n.type != "call_expression":
            continue
        fn = n.child_by_field_name("function")
        if fn is None:
            continue
        args = n.child_by_field_name("arguments")
        if fn.type == "field_expression":
            # `a->b->c(...)`: dispatch through a struct member function pointer.
            callee = _text(fn, src)
            obj = fn.child_by_field_name("argument")
            obj_name = obj.text.decode() if obj is not None and obj.type == "identifier" else None
            if obj_name and "cast_expression" in assign_kinds.get(obj_name, set()):
                if computed_pattern is None:   # opaque void*-cast pointer
                    computed_pattern = f"computed function-pointer dispatch in {ref} ({callee})"
            elif stored_pattern is None:       # stored-table vtable pointer
                stored_pattern = f"function-pointer table dispatch in {ref} ({callee})"
        elif fn.type == "identifier":
            name = fn.text.decode()
            if name in defined_symbols:
                continue                       # resolved direct call — an edge, not a hazard
            kinds = assign_kinds.get(name)
            if not kinds:
                continue                       # parameter callback / macro / extern — not a hazard
            if ("conditional_expression" in kinds or "cast_expression" in kinds):
                if computed_pattern is None:   # computed member selection / opaque ptr
                    argtext = _text(args, src) if args is not None else "()"
                    src_call = source_calls[0] if source_calls else "lookup"
                    computed_pattern = (
                        f"computed function-pointer dispatch in {ref} "
                        f"({src_call}() then {name}{argtext})"
                    )
            elif any(k in kinds for k in ("subscript_expression", "field_expression")):
                if stored_pattern is None:     # fn-ptr read from a stored table
                    detail = assign_text.get(name, name)
                    stored_pattern = f"field-codec function-pointer table in {ref} ({detail})"

    # (U-c) Computed / opaque dispatch dominates a stored-table read in the same file.
    if computed_pattern is not None:
        return _UNRESOLVED, computed_pattern

    # (F-a/b) Stored fn-ptr to a known in-tree target.
    if stored_pattern is not None:
        return _FALLBACK, stored_pattern

    # (F-c) Callback registration: function identifiers that are referenced/stored
    #       but defined nowhere in the partition (forward-declared, macro-defined
    #       elsewhere) and bound into a struct/array initializer vtable.
    undefined_funcs = _vtable_bound_undefined(root, src, defined_symbols)
    if undefined_funcs:
        suffix = _common_suffix(undefined_funcs)
        return _FALLBACK, f"callback-registered brand vtables in {ref} -> macro-generated {suffix}"

    return _EXTRACTED, None


def _vtable_bound_undefined(root: Node, src: bytes, defined_symbols: set[str]) -> list[str]:
    """Function-name identifiers placed inside an ``initializer_list`` (a vtable
    binding) that are forward-declared in this file but defined nowhere in the
    partition — the macro-generated handlers the registry can't link."""
    forward_decls: set[str] = set()
    for child in _toplevel(root):
        if child.type != "declaration":
            continue
        fd = _find_function_declarator(child.child_by_field_name("declarator"))
        if fd is not None:
            ident = _declarator_identifier(fd.child_by_field_name("declarator"))
            if ident is not None:
                forward_decls.add(ident.text.decode())
    undefined = forward_decls - defined_symbols
    if not undefined:
        return []
    bound: list[str] = []
    for n in _walk(root):
        if n.type == "initializer_list":
            for ident in (c for c in _walk(n) if c.type == "identifier"):
                name = ident.text.decode()
                if name in undefined and name not in bound:
                    bound.append(name)
    return bound


def _common_suffix(names: Sequence[str]) -> str:
    """`['visa_route','amex_route']` → `*_route`."""
    if not names:
        return "*"
    parts = [n.split("_") for n in names]
    tail: list[str] = []
    for col in range(1, min(len(p) for p in parts) + 1):
        seg = parts[0][-col]
        if all(p[-col] == seg for p in parts):
            tail.insert(0, seg)
        else:
            break
    return "*_" + "_".join(tail) if tail else "*"


# ──────────────────────────────────────────────────────────────────────────────
# Driver.
# ──────────────────────────────────────────────────────────────────────────────

def _parse(abs_path: str) -> tuple[Node, bytes]:
    with open(abs_path, "rb") as fh:
        src = fh.read()
    return _PARSER.parse(src).root_node, src


def run(files: Sequence[str], repo_root: str) -> dict:
    """Extract structural fields from the C partition (ADR-002 file list).

    ``files`` are repo-relative C paths the dispatcher routed here; ``repo_root``
    locates them on disk. Returns ``{"entries": [...], "coverage_report": {...}}``:
    each entry carries only the extractor-owned structural fields (``used_by`` is
    left empty for ``merge_edges``; ``purpose``/``tags`` for the model). The
    aggregate ``coverage_report`` records the extracted/fallback/unresolved split
    and the ``unresolved_patterns`` lines (§3.3 / §5.4).
    """
    parsed: dict[str, tuple[Node, bytes]] = {}
    for rel in files:
        parsed[rel] = _parse(os.path.join(repo_root, rel))

    # Pass 1 — global non-static definition table (symbol → defining identity).
    symbol_owner: dict[str, str] = {}
    for rel, (root, src) in parsed.items():
        if not rel.lower().endswith(_C_SOURCE_EXTS):
            continue
        identity = _identity_of(rel)
        for name, is_static in _definitions(root, src):
            if not is_static:
                symbol_owner.setdefault(name, identity)
    defined_symbols = set(symbol_owner)

    # Pass 2 — per-file structural entry + hazard classification.
    entries: list[dict] = []
    files_extracted = files_fallback = files_unresolved = 0
    unresolved_patterns: list[str] = []

    for rel in files:
        root, src = parsed[rel]
        identity = _identity_of(rel)
        is_header = rel.lower().endswith(_C_HEADER_EXTS)

        if is_header:
            interfaces = _prototypes(root, src)
            depends_on: list[str] = []
            bucket, pattern = _EXTRACTED, None
        else:
            interfaces = _source_interfaces(root, src)
            # depends_on: direct identifier calls that resolve to another file's
            # non-static definition (deterministic; dedup preserving discovery order).
            depends_on = []
            for n in _walk(root):
                if n.type != "call_expression":
                    continue
                fn = n.child_by_field_name("function")
                if fn is None or fn.type != "identifier":
                    continue
                owner = symbol_owner.get(fn.text.decode())
                if owner and owner != identity and owner not in depends_on:
                    depends_on.append(owner)
            bucket, pattern = _classify(rel, root, src, defined_symbols)

        if bucket == _UNRESOLVED:
            files_unresolved += 1
        elif bucket == _FALLBACK:
            files_fallback += 1
        else:
            files_extracted += 1
        if pattern is not None:
            unresolved_patterns.append(pattern)

        entries.append({
            "path": rel,
            "module": _module_of(rel),
            "interfaces": interfaces,
            "depends_on": depends_on,
            "used_by": [],            # closed by merge_edges (TASK-011)
            "coverage": "coarse",     # §5.5 / SIGNOFF #1 — only the deep pass promotes
        })

    files_seen = len(files)
    coverage = round(files_extracted / files_seen, 2) if files_seen else 0.0
    coverage_report = {
        "files_seen": files_seen,
        "files_extracted": files_extracted,
        "files_fallback": files_fallback,
        "files_unresolved": files_unresolved,
        "coverage": coverage,
        "unresolved_patterns": unresolved_patterns,
    }
    return {"entries": entries, "coverage_report": coverage_report}
