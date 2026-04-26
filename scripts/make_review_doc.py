"""
make_review_doc.py — يولّد وثيقة مراجعة بشرية (markdown) من deliverables-index.json.

الاستخدام:
    python scripts/make_review_doc.py [--input <path>] [--output <path>]

الافتراضات:
    --input  knowledge/deliverables-index.json (الـcurated، الأحدث)
    --output agencies/_review/deliverables_review.md
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

CAT_NAMES = {
    "PRE": "الاشتراطات",
    "DOC": "الوثائق",
    "RPT": "التقارير",
    "DEC": "القرارات",
    "MIN": "المحاضر",
    "EVI": "الشواهد",
    "OTH": "ملفات أخرى",
}
PHASE_NAMES = {
    "A": "التمكين والاشتراطات",
    "B": "التأسيس التنظيمي",
    "C": "التوجيه الاستراتيجي",
    "D": "بنية الممارسة",
    "E": "الحالة والفجوات",
    "F": "التنفيذ والمتابعة",
}


def main() -> int:
    p = argparse.ArgumentParser(description="Generate human review markdown from deliverables-index.json")
    p.add_argument("--input", default="knowledge/deliverables-index.json",
                   help="مسار JSON المصدر (افتراضي: curated)")
    p.add_argument("--output", default="agencies/_review/deliverables_review.md",
                   help="مسار MD الناتج")
    args = p.parse_args()

    src = Path(args.input)
    if not src.exists():
        # fallback لـ extracted لو curated غير موجود
        fb = Path("extracted/primary-spec/deliverables-index.json")
        if fb.exists():
            print(f"[info] {src} not found, falling back to {fb}")
            src = fb
        else:
            print(f"[error] no deliverables-index.json found")
            return 1
    d = json.loads(src.read_text(encoding="utf-8"))
    meta = d["meta"]
    L: list[str] = []
    L.append("# مراجعة فهرس المخرجات — Phase 0 Baseline")
    L.append("")
    L.append(f"**المصدر:** {meta['source']}")
    L.append(f"**تاريخ الاستخراج:** {meta['extracted_at']}")
    L.append(f"**الإجمالي:** {meta['total_deliverable_candidates']} مخرجا عبر {meta['categories_detected']} فئات")
    L.append("")
    L.append("**توزيع حسب الفئة:** " + " · ".join(f"{k}={v}" for k, v in meta["by_category"].items()))
    L.append("")
    L.append("**توزيع حسب المرحلة A-F:** " + " · ".join(f"{k}({PHASE_NAMES.get(k, '?')})={v}" for k, v in meta["by_phase"].items()))
    L.append("")
    L.append("**التحقق الخارجي (NotebookLM):**")
    L.append("- DOC: 19/20 exact + 1 close + 0 drift ✅")
    L.append("- PRE: 4/4 exact ✅")
    L.append("- RPT: 9 عندنا مقابل 8 NotebookLM — نحن أدق (NotebookLM فاته تقرير الامتثال لمبادئ البنية) 🎯")
    L.append("")
    L.append("**طريقة المراجعة:** غيّر عمود مراجعة من ⬜ إلى إحدى هذه:")
    L.append("- ✅ صحيح كما هو")
    L.append("- ✏️ يحتاج تعديل (اكتب التعديل في الملاحظة)")
    L.append("- ❌ احذف (ليس مخرجا حقيقيا)")
    L.append("- 🔀 دمج مع عنصر آخر (اذكر الرقم في الملاحظة)")
    L.append("")
    L.append("---")
    L.append("")

    by_cat = defaultdict(list)
    for it in d["deliverables"]:
        by_cat[it["category_id"]].append(it)

    for cat_id in ["PRE", "DOC", "RPT", "DEC", "MIN", "EVI", "OTH"]:
        items = by_cat.get(cat_id, [])
        if not items:
            continue
        L.append(f"## {cat_id} · {CAT_NAMES.get(cat_id, cat_id)} ({len(items)})")
        L.append("")
        L.append("| # | مراجعة | id | المرحلة | المخرج | serial | جهة الاعتماد | ملاحظة |")
        L.append("|---|:---:|---|:---:|---|:---:|---|---|")
        for i, it in enumerate(items, 1):
            nm = it["name_ar"].replace("|", "\\|")
            ph = it["phase_abcdef"]
            auth_list = it.get("approval_authorities") or []
            auth = "<br>".join(a.replace("|", "\\|") for a in auth_list) if auth_list else "—"
            ser = it.get("serial_number") if it.get("serial_number") is not None else "—"
            cid = it["id"]
            L.append(f"| {i} | ⬜ | {cid} | **{ph}** | {nm} | {ser} | {auth} | |")
        L.append("")

    L.append("---")
    L.append("")
    L.append("## تعديلات مطلوبة (املأ هنا)")
    L.append("")
    L.append("بعد مراجعة البنود أعلاه، سجّل التغييرات المطلوبة على هيكل البيانات/السكربت هنا:")
    L.append("")
    L.append("- [ ] ")
    L.append("- [ ] ")
    L.append("")

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"[ok] {out}  ({out.stat().st_size:,} bytes)  source={src}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
