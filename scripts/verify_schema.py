#!/usr/bin/env python3
"""
Verify a NORA-Audit deliverable schema (fields.json) for structural integrity.

Checks (v0.3 baseline; v0.4+ checks activate when schema_version reflects them):
- Top-level required keys: schema_version, deliverable_id, scaffold_status, containers
- deliverable_id matches DEL-XXX-NNN pattern
- containers is a non-empty list
- each container has key, name_ar, weight
- container weights sum to exactly 100
- a top-level container with key="governance" exists (DD-3 project convention)
- no occurrence of deprecated `optional_per_guide` flag (DD-18)
- design_decisions_v* blocks have a `decisions` array; DD ids unique + match DD-N
- reports severity / severity_source distribution across all validation-bearing leaves

Usage:
    python scripts/verify_schema.py <fields.json> [--quiet]

Exit codes: 0 = pass (no errors), 1 = errors found, 2 = invocation error.
"""
import io
import json
import re
import sys
from collections import Counter
from pathlib import Path

# Force UTF-8 on Windows stdout/stderr to prevent cp1252 mojibake on Arabic content.
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")


def collect_validation_leaves(node, leaves):
    """Walk the tree collecting every dict that has a `validation` block."""
    if isinstance(node, dict):
        if "validation" in node and isinstance(node["validation"], dict):
            leaves.append(node)
        for v in node.values():
            collect_validation_leaves(v, leaves)
    elif isinstance(node, list):
        for item in node:
            collect_validation_leaves(item, leaves)


def find_deprecated_flags(node, hits, path="$"):
    """DD-18: `optional_per_guide` is deprecated. Record any occurrence with its path."""
    if isinstance(node, dict):
        if "optional_per_guide" in node:
            hits.append(f"{path} (key={node.get('key', '<unnamed>')})")
        for k, v in node.items():
            find_deprecated_flags(v, hits, f"{path}.{k}")
    elif isinstance(node, list):
        for i, item in enumerate(node):
            find_deprecated_flags(item, hits, f"{path}[{i}]")


def main():
    raw_args = sys.argv[1:]
    quiet = "--quiet" in raw_args
    positional = [a for a in raw_args if not a.startswith("--")]
    if not positional:
        print("Usage: python scripts/verify_schema.py <fields.json> [--quiet]")
        sys.exit(2)

    path = Path(positional[0])
    if not path.exists():
        print(f"ERROR: file not found: {path}")
        sys.exit(2)

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"ERROR: invalid JSON: {e}")
        sys.exit(1)

    errors = []
    warnings = []

    # Top-level required keys
    for k in ("schema_version", "deliverable_id", "scaffold_status", "containers"):
        if k not in data:
            errors.append(f"missing top-level key: {k}")

    schema_version = str(data.get("schema_version", "?"))
    deliverable_id = data.get("deliverable_id", "?")
    if not re.match(r"^DEL-[A-Z]{3}-\d{3}$", str(deliverable_id)):
        warnings.append(f"deliverable_id format unexpected: {deliverable_id}")

    containers = data.get("containers", [])
    if not isinstance(containers, list) or not containers:
        errors.append("containers must be a non-empty list")
        containers = []

    # Per-container structure + weight sum
    weight_sum = 0
    container_keys = []
    for idx, c in enumerate(containers):
        if not isinstance(c, dict):
            errors.append(f"container[{idx}] is not an object")
            continue
        for rk in ("key", "name_ar", "weight"):
            if rk not in c:
                errors.append(f"container[{idx}] missing required key: {rk}")
        if isinstance(c.get("weight"), int):
            weight_sum += c["weight"]
        elif "weight" in c:
            errors.append(f"container[{idx}] weight must be integer, got {type(c['weight']).__name__}")
        container_keys.append(c.get("key", f"<container[{idx}]>"))

    if weight_sum != 100:
        errors.append(f"container weights sum to {weight_sum}, expected exactly 100")

    # Governance convention (DD-3)
    if "governance" not in container_keys:
        errors.append("missing top-level container 'governance' (DD-3 project convention)")

    # optional_per_guide deprecation (DD-18)
    deprecated_hits = []
    find_deprecated_flags(data, deprecated_hits)
    if deprecated_hits:
        errors.append(
            f"deprecated `optional_per_guide` flag found in {len(deprecated_hits)} place(s): "
            f"{deprecated_hits[:3]}{'...' if len(deprecated_hits) > 3 else ''}"
        )

    # Design-decisions audit
    dd_ids_seen = []
    dd_blocks = sorted(k for k in data if k.startswith("design_decisions_v"))
    for bk in dd_blocks:
        block = data[bk]
        if not isinstance(block, dict) or "decisions" not in block:
            errors.append(f"{bk} missing `decisions` array")
            continue
        for d_idx, decision in enumerate(block.get("decisions", [])):
            did = decision.get("id", "")
            if not re.match(r"^DD-\d+$", did):
                warnings.append(f"{bk}.decisions[{d_idx}] id format unexpected: {did!r}")
                continue
            if did in dd_ids_seen:
                errors.append(f"duplicate DD id across blocks: {did}")
            else:
                dd_ids_seen.append(did)

    # Severity / source distribution report
    leaves = []
    collect_validation_leaves(data, leaves)
    sev = Counter(l.get("validation", {}).get("severity", "?") for l in leaves)
    src = Counter(l.get("validation", {}).get("severity_source", "?") for l in leaves)

    # v0.4+ checks (placeholder — activate when sub-container weights are introduced)
    if schema_version and schema_version >= "0.4":
        for c in containers:
            sub_weights = []
            for f in c.get("fields", []):
                if isinstance(f, dict) and "weight" in f:
                    sub_weights.append(f.get("weight", 0))
            if sub_weights:
                got = sum(w for w in sub_weights if isinstance(w, int))
                expected = c.get("weight", 0)
                if got != expected:
                    errors.append(
                        f"container '{c.get('key')}' sub-weights sum to {got}, "
                        f"expected parent weight {expected} (v0.4 rule)"
                    )

    # Output
    if not quiet:
        print(f"=== Schema verification: {path.name} ===")
        print(f"  deliverable_id     : {deliverable_id}")
        print(f"  schema_version     : {schema_version}")
        print(f"  scaffold_status    : {data.get('scaffold_status', '?')}")
        print(f"  containers         : {len(containers)}")
        for c in containers:
            print(f"    - {c.get('key', '?'):<25} weight={c.get('weight', '?')}")
        print(f"  weight sum         : {weight_sum}/100")
        print(f"  validation leaves  : {len(leaves)}")
        print(
            f"    severity         : must={sev.get('must', 0)}, "
            f"should={sev.get('should', 0)}, nice={sev.get('nice', 0)}"
        )
        print(
            f"    severity_source  : judgment={src.get('judgment', 0)}, "
            f"guide={src.get('guide', 0)}, primary_spec={src.get('primary_spec', 0)}"
        )
        print(f"  design decisions   : {len(dd_ids_seen)} across {len(dd_blocks)} version block(s)")

        if warnings:
            print()
            print(f"WARNINGS ({len(warnings)}):")
            for w in warnings:
                print(f"  ! {w}")
        if errors:
            print()
            print(f"ERRORS ({len(errors)}):")
            for e in errors:
                print(f"  X {e}")
        else:
            print()
            print("PASS — no structural errors")

    sys.exit(0 if not errors else 1)


if __name__ == "__main__":
    main()
