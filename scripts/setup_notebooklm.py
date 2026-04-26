"""setup_notebooklm.py — يطبّق التصحيحات اللازمة على notebooklm-py المثبَّتة.

الإطار:
- مكتبة `notebooklm-py` (unofficial) لها CLI `notebooklm login` يفتح Chromium
  (Playwright) للدخول على جوجل ثم يحفظ cookies في storage_state.json.
- على بيئات Windows مع SxS مكسور، Chromium يفشل بـ "side-by-side configuration
  is incorrect" حتى مع MSVC redist مثبت. الحل: استعمال Microsoft Edge النظامي
  عبر channel="msedge".
- خطوة `page.goto(GOOGLE_ACCOUNTS_URL)` بعد الـ ENTER قد تنقطع عندما يكون
  المستخدم مسجّل دخول مسبقا (يُعاد توجيهه لـ NotebookLM فورا) → نلفّ الاستدعاء
  في try/except لمنع crash.

السكربت idempotent: يبحث عن marker `[NORA patch]` ولا يُعيد التطبيق.
يتعامل مع أي مكان مثبَّت فيه notebooklm (--user أو global).

Usage:
    python scripts/setup_notebooklm.py            # apply
    python scripts/setup_notebooklm.py --check    # status only
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

PATCH_MARKER = "[NORA patch]"


def find_session_py_all() -> list[Path]:
    """يبحث في كل sys.path (user-site + global) عن notebooklm/cli/session.py.
    قد يوجد المكتبة في موقعين على Windows (Roaming --user + Lib/site-packages global).
    """
    found: list[Path] = []
    seen: set[str] = set()
    for entry in sys.path:
        if not entry or entry in seen:
            continue
        seen.add(entry)
        candidate = Path(entry) / "notebooklm" / "cli" / "session.py"
        if candidate.exists():
            found.append(candidate)
    return found


def apply_patches(session_path: Path) -> tuple[bool, list[str]]:
    """يُرجع (changed, messages)."""
    text = session_path.read_text(encoding="utf-8")
    msgs: list[str] = []

    if PATCH_MARKER in text:
        return False, ["already patched (skipping)"]

    # ---------------- Patch 1: channel="msedge" ----------------
    p1_old = (
        '            context = p.chromium.launch_persistent_context(\n'
        '                user_data_dir=str(browser_profile),\n'
        '                headless=False,\n'
    )
    p1_new = (
        '            context = p.chromium.launch_persistent_context(\n'
        '                user_data_dir=str(browser_profile),\n'
        '                channel="msedge",  # [NORA patch] use system Edge to avoid Chromium SxS\n'
        '                headless=False,\n'
    )
    if p1_old not in text:
        return False, ["patch 1 anchor not found — notebooklm-py version may differ"]
    text = text.replace(p1_old, p1_new, 1)
    msgs.append("patch 1 applied: channel=\"msedge\" added to launch_persistent_context")

    # ---------------- Patch 2: skip-goto safety ----------------
    p2_old = (
        '            # Force .google.com cookies for regional users (e.g. UK lands on\n'
        '            # .google.co.uk). Use "load" not "networkidle" to avoid analytics hangs.\n'
        '            page.goto(GOOGLE_ACCOUNTS_URL, wait_until="load")\n'
        '            page.goto(NOTEBOOKLM_URL, wait_until="load")\n'
    )
    p2_new = (
        '            # Force .google.com cookies for regional users (e.g. UK lands on\n'
        '            # .google.co.uk). Use "load" not "networkidle" to avoid analytics hangs.\n'
        '            # [NORA patch] ignore navigation-interrupted errors — these gotos are\n'
        '            # optional cookie-domain nudges; storage_state still has the auth.\n'
        '            for url in (GOOGLE_ACCOUNTS_URL, NOTEBOOKLM_URL):\n'
        '                try:\n'
        '                    page.goto(url, wait_until="load")\n'
        '                except Exception as _e:\n'
        '                    console.print(f"[dim](skip goto {url}: {type(_e).__name__})[/dim]")\n'
    )
    if p2_old not in text:
        return False, msgs + ["patch 2 anchor not found — notebooklm-py version may differ"]
    text = text.replace(p2_old, p2_new, 1)
    msgs.append("patch 2 applied: skip-goto safety wrapper")

    session_path.write_text(text, encoding="utf-8")
    return True, msgs


def main() -> int:
    ap = argparse.ArgumentParser(description="Patch installed notebooklm-py for NORA-Audit")
    ap.add_argument("--check", action="store_true", help="report status without modifying")
    args = ap.parse_args()

    paths = find_session_py_all()
    if not paths:
        print("error: notebooklm-py not installed in any sys.path location.")
        print("  install:  pip install \"notebooklm-py[browser]\"")
        return 2

    overall_rc = 0
    for sp in paths:
        print(f"\ntarget: {sp}")
        if args.check:
            text = sp.read_text(encoding="utf-8")
            print("status: " + ("PATCHED" if PATCH_MARKER in text else "UNPATCHED"))
            continue
        try:
            changed, msgs = apply_patches(sp)
        except Exception as e:
            print(f"  ! error: {type(e).__name__}: {e}")
            overall_rc = 1
            continue
        for m in msgs:
            print(f"  - {m}")
        if changed:
            print("  → ready: `python -m notebooklm login`")
    return overall_rc


if __name__ == "__main__":
    raise SystemExit(main())
