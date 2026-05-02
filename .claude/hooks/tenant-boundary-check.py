#!/usr/bin/env python3
"""Tenant-isolation PreToolUse hook for NORA-Audit.

Blocks Edit/Write/MultiEdit on core paths when current branch starts with `client/`.
Per master plan §3.5, this enforces the one-way knowledge boundary: tenant work
on client/<name> branches cannot silently modify core regulator-grade artifacts.

Behavior:
  - On main (or any non-client branch): always allow.
  - On client/*: block writes to knowledge/, scripts/, DGA-Resources/, extracted/.
  - Allow-list (agencies/, learnings-from-agencies/, .claude/) takes precedence
    over deny-list — handles edge cases like agencies/<name>/knowledge/ subfolders.
  - Fail-open on any error (parse failure, git failure, detached HEAD): the hook
    is a usability safeguard, not a fortress. Defense-in-depth via /promote-learning
    review still gates anything that reaches main.
"""
import json
import os
import subprocess
import sys

ALLOWED = ("agencies/", "learnings-from-agencies/", ".claude/")
DENIED = ("knowledge/", "scripts/", "dga-resources/", "extracted/")


def fail_open(reason):
    print(f"tenant-boundary-check: fail-open: {reason}", file=sys.stderr)
    sys.exit(0)


def deny(branch, file_path):
    msg = (
        f"Tenant-isolation boundary: branch '{branch}' cannot modify core path "
        f"'{file_path}'. To propose this change to core, capture it as a candidate "
        f"via the tenant-learning-capture skill (output: "
        f"learnings-from-agencies/<agency>-<YYYY-MM-DD>/candidates.md), then run "
        f"/promote-learning <id> from main after switching branches."
    )
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": msg,
        }
    }))
    print(
        f"tenant-boundary-check: branch={branch}, path={file_path}, decision=deny",
        file=sys.stderr,
    )
    sys.exit(0)


def get_relative_path(file_path):
    """Return project-relative lowercase path, or None if outside project tree."""
    fp = file_path.replace("\\", "/")
    cwd = os.getcwd().replace("\\", "/").rstrip("/")
    if fp.startswith(cwd + "/"):
        return fp[len(cwd) + 1:].lower()
    if os.path.isabs(fp):
        return None
    if fp.startswith("./"):
        fp = fp[2:]
    return fp.lower()


def main():
    try:
        tool_input = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, ValueError) as e:
        return fail_open(f"json parse: {e}")

    file_path = tool_input.get("tool_input", {}).get("file_path", "")
    if not file_path:
        return fail_open("no file_path in tool_input")

    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, timeout=5,
        )
        branch = result.stdout.strip() if result.returncode == 0 else ""
    except (subprocess.SubprocessError, OSError) as e:
        return fail_open(f"git rev-parse failed: {e}")

    if not branch.startswith("client/"):
        sys.exit(0)

    rel = get_relative_path(file_path)
    if rel is None:
        sys.exit(0)

    # Path-traversal defense: reject .. segments before deny/allow checks.
    if ".." in rel.split("/"):
        return deny(branch, file_path)

    # Allow-list takes precedence over deny-list (handles agencies/<name>/knowledge/...)
    for prefix in ALLOWED:
        if rel.startswith(prefix):
            sys.exit(0)

    for prefix in DENIED:
        if rel.startswith(prefix):
            return deny(branch, file_path)

    # Top-level files (CLAUDE.md, .gitignore, etc.) — allow.
    sys.exit(0)


if __name__ == "__main__":
    main()
