"""
nlm_diff.py — مقارنة مقترحات NotebookLM مع فهرسنا (deliverables-index.json).

يقرأ:
  - agencies/_ensemble/nlm_docs_verify.json   (إجابة NotebookLM)
  - extracted/primary-spec/deliverables-index.json (فهرسنا)

يستخرج أسماء الوثائق من نص إجابة NotebookLM عبر regex، ويطابقها
بالترتيب مع 20 مخرج DOC عندنا، ويُنتج تقرير diff.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


# -----------------------------------------------------------------------------
# استخراج أسماء NotebookLM من markdown
# -----------------------------------------------------------------------------

# نمطان محتملان (أي من الحقل 1:)
NAME_PATTERNS = [
    re.compile(r"\*\*اسم الوثيقة كما ورد حرفيا:\*\*\s*([^\n\[]+)"),
    re.compile(r"\*\*اسم الوثيقة:\*\*\s*([^\n\[]+)"),
]


def _normalize_for_match(s: str) -> str:
    """تطبيع خفيف للمقارنة — إزالة الفواصل، الاقتباسات، tatweel، وتوحيد ـ ال/اال."""
    s = s.strip()
    s = re.sub(r"[•\[\]\.\,،]", " ", s)        # إزالة رموز ترقيم
    s = re.sub(r"\s+", " ", s)
    s = s.replace("\u0640", "")                # tatweel
    s = s.replace("اال", "الا")                # تطبيع lam-alef المفكّك
    s = s.replace("األ", "الأ")
    s = s.replace("إلا", "الإ")
    s = s.strip()
    return s


def extract_nlm_names(answer: str) -> list[str]:
    names: list[str] = []
    for pat in NAME_PATTERNS:
        for m in pat.finditer(answer):
            name = m.group(1).strip()
            name = re.sub(r"\s*\[\d+(,\s*\d+)*\]\s*$", "", name)  # إزالة [2] في النهاية
            name = name.strip()
            names.append(name)
        if names:
            break
    return names


def load_our_docs(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return [d for d in data["deliverables"] if d["category_id"] == "DOC"]


def main() -> int:
    nlm_path = Path("agencies/_ensemble/nlm_docs_verify.json")
    ours_path = Path("extracted/primary-spec/deliverables-index.json")

    nlm = json.loads(nlm_path.read_text(encoding="utf-8"))
    nlm_names = extract_nlm_names(nlm["nlm_answer"])
    ours = load_our_docs(ours_path)

    print(f"NotebookLM items : {len(nlm_names)}")
    print(f"Our DOC items    : {len(ours)}")
    print(f"Count match      : {'✅ YES' if len(nlm_names) == len(ours) else '❌ NO'}")
    print()

    # مقارنة بالترتيب (كلاهما يتتبع نفس ترتيب الظهور في PDF)
    print(f"{'#':>3}  {'match':<7}  {'nlm (clean)':<50}  {'ours (noisy)':<50}")
    print(f"{'-'*3}  {'-'*7}  {'-'*50}  {'-'*50}")
    exact = close = drift = 0
    diff_rows = []
    for i in range(max(len(nlm_names), len(ours))):
        nlm_name = nlm_names[i] if i < len(nlm_names) else ""
        our_name = ours[i]["name_ar"] if i < len(ours) else ""
        n_norm = _normalize_for_match(nlm_name)
        o_norm = _normalize_for_match(our_name)
        # مطابقة
        if n_norm == o_norm:
            mark = "=="
            exact += 1
        elif n_norm in o_norm or o_norm in n_norm:
            mark = "≈ sub"
            close += 1
        else:
            # تحقق إن كان الاسم الخاص بنا "مقطوع" (substring-prefix من nlm)
            # e.g., ours = "وثيقة استراتيجية التحول" و nlm = "... التحول الرقمي"
            tokens_ours = o_norm.split()
            tokens_nlm = n_norm.split()
            if tokens_ours and tokens_nlm and tokens_ours == tokens_nlm[: len(tokens_ours)]:
                mark = "≈ cut"
                close += 1
            elif tokens_ours and tokens_nlm and tokens_ours[:3] == tokens_nlm[:3]:
                mark = "≈ ~3"
                close += 1
            else:
                mark = "❌ drift"
                drift += 1
        print(f"{i+1:>3}  {mark:<7}  {nlm_name[:48]:<50}  {our_name[:48]:<50}")
        diff_rows.append({
            "idx": i + 1,
            "nlm_name": nlm_name,
            "our_name": our_name,
            "our_id": ours[i]["id"] if i < len(ours) else None,
            "our_phase": ours[i]["phase_abcdef"] if i < len(ours) else None,
            "match_kind": mark,
        })

    print()
    print(f"SUMMARY: exact={exact}  close(sub/cut)={close}  drift={drift}  total={max(len(nlm_names), len(ours))}")

    # حفظ التقرير
    out = Path("agencies/_ensemble/nlm_docs_diff.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(
            {
                "counts": {
                    "nlm": len(nlm_names),
                    "ours": len(ours),
                    "exact": exact,
                    "close": close,
                    "drift": drift,
                },
                "rows": diff_rows,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"\n[saved] {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
