"""
make_dependency_doc.py — يدمج طبقات الاقتراحات في وثيقة مراجعة + JSON منظم.

يقرأ:
  - knowledge/deliverables-index.json                (الفهرس المعتمد)
  - knowledge/dep_suggestions_ab.json                (طبقتي أ + ب)
  - knowledge/dep_suggestions_c.json                 (طبقة ج₁ literal — NotebookLM)
  - knowledge/dep_suggestions_c_inferential.json     (طبقة ج₂ inferential — NotebookLM)

يُنتج:
  - knowledge/dependency-suggestions.md   (للمراجعة البشرية)
  - knowledge/dependency-suggestions.json (نسخة منظمة قابلة للمعالجة)
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path
from datetime import datetime, timezone

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


CAT_NAMES = {
    "PRE": "الاشتراطات", "DOC": "الوثائق", "RPT": "التقارير",
    "DEC": "القرارات", "MIN": "المحاضر", "EVI": "الشواهد", "OTH": "ملفات أخرى",
}


def main() -> int:
    idx_path = Path("knowledge/deliverables-index.json")
    ab_path = Path("knowledge/dep_suggestions_ab.json")
    c1_path = Path("knowledge/dep_suggestions_c.json")             # literal
    c2_path = Path("knowledge/dep_suggestions_c_inferential.json")  # inferential

    if not idx_path.exists():
        print(f"[error] {idx_path} not found")
        return 1
    if not ab_path.exists():
        print(f"[error] {ab_path} not found — run build_dependency_suggestions.py first")
        return 1
    has_c1 = c1_path.exists()
    has_c2 = c2_path.exists()
    if not has_c1:
        print(f"[warn] {c1_path} not found — layer ج₁ (literal) skipped")
    if not has_c2:
        print(f"[warn] {c2_path} not found — layer ج₂ (inferential) skipped")

    idx = json.loads(idx_path.read_text(encoding="utf-8"))
    ab = json.loads(ab_path.read_text(encoding="utf-8"))
    c1_data = json.loads(c1_path.read_text(encoding="utf-8")) if has_c1 else {"results": {}}
    c2_data = json.loads(c2_path.read_text(encoding="utf-8")) if has_c2 else {"results": {}}

    items = idx["deliverables"]
    by_id = {it["id"]: it for it in items}

    # ابني قاموس candidates لكل مخرج
    layer_a = ab["layer_a_phase_rules"]
    layer_b = ab["layer_b_text_signals"]
    c1_results = c1_data.get("results", {})
    c2_results = c2_data.get("results", {})

    # هيكل منظم
    structured: dict[str, dict] = {}
    for it in items:
        my_id = it["id"]
        a_data = layer_a.get(my_id, {"depends_on": [], "prerequisites": []})
        b_hits = layer_b.get(my_id, [])
        c1_entry = c1_results.get(my_id, {})
        c2_entry = c2_results.get(my_id, {})

        # candidates set: cand_id → {layers: set(A/B/C1/C2)}
        candidates: dict[str, dict] = {}

        for d in a_data.get("depends_on", []):
            cid = d["target_id"]
            candidates.setdefault(cid, {"layers": set()})
            candidates[cid]["layers"].add("A")
            candidates[cid]["a_phase"] = d.get("from_phase", "")

        for h in b_hits:
            cid = h["target_id"]
            candidates.setdefault(cid, {"layers": set()})
            candidates[cid]["layers"].add("B")
            candidates[cid]["b_phrase"] = h.get("matched_phrase", "")

        for cid in c1_entry.get("matched_ids", []):
            candidates.setdefault(cid, {"layers": set()})
            candidates[cid]["layers"].add("C1")

        for cid in c2_entry.get("matched_ids", []):
            candidates.setdefault(cid, {"layers": set()})
            candidates[cid]["layers"].add("C2")

        # set → sorted list للمسلسل
        for cid, info in candidates.items():
            info["layers"] = sorted(info["layers"])

        structured[my_id] = {
            "id": my_id,
            "name_ar": it["name_ar"],
            "phase": it.get("phase_abcdef"),
            "category_id": it["category_id"],
            "candidates": candidates,
            "prerequisites": [p["target_id"] for p in a_data.get("prerequisites", [])],
            "nlm_literal_answer": c1_entry.get("raw_answer", "") if has_c1 else None,
            "nlm_inferential_answer": c2_entry.get("raw_answer", "") if has_c2 else None,
        }

    # احفظ الـ JSON المنظم
    out_json = Path("knowledge/dependency-suggestions.json")
    out_json.write_text(
        json.dumps({
            "meta": {
                "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "items_count": len(items),
                "layer_a_source": str(ab_path).replace("\\", "/"),
                "layer_b_source": str(ab_path).replace("\\", "/"),
                "layer_c1_source": str(c1_path).replace("\\", "/") if has_c1 else None,
                "layer_c2_source": str(c2_path).replace("\\", "/") if has_c2 else None,
                "method": "phase_rules + content_text + nlm_literal + nlm_inferential",
            },
            "items": structured,
        }, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"[ok] {out_json}")

    # ابني المايك داون
    L: list[str] = []
    L.append("# اقتراحات اعتماديات المخرجات — للمراجعة البشرية")
    L.append("")
    L.append(f"**المصدر:** {idx_path}  •  {len(items)} مخرجا")
    L.append("")
    L.append("**طبقات الاقتراحات:**")
    L.append("- **(أ)** قواعد المراحل من plan §5.0 — اقتراحات بنيوية بناء على A→B→...→F")
    L.append("- **(ب)** إشارات نصية: phrases من أسماء مخرجات أخرى ظهرت في content_preview")
    L.append("- **(ج₁)** NotebookLM literal: \"ما المخرجات التي يعتمد عليها صراحة؟\" (محافظ)")
    L.append("- **(ج₂)** NotebookLM inferential: \"ما يحتاج المراجِع للرجوع إليه عند تقييم X؟\" (موسّع)")
    L.append("")
    L.append("**كيفية القراءة:** كل مخرج له جدول مرشّحات. الأعمدة (أ)/(ب)/(ج₁)/(ج₂) تُظهر أي طبقة اقترحت كل مرشّح.")
    L.append("**اتفاق 3+ طبقات** = إشارة قوية جدا. **اتفاق 2 طبقات** = إشارة متوسطة. **طبقة واحدة** = يحتاج تقييمك.")
    L.append("")
    L.append("**في خانة \"اعتماد\":**")
    L.append("- ✅ نعم، اعتمادية حقيقية → ستُضاف في dependency-graph")
    L.append("- ❌ لا، رفض الاقتراح")
    L.append("- ❓ غير متأكد، يحتاج فحص أعمق")
    L.append("")
    L.append("---")
    L.append("")

    # تنظيم حسب الفئة
    by_cat: dict[str, list[dict]] = defaultdict(list)
    for s in structured.values():
        by_cat[s["category_id"]].append(s)

    for cat_id in ["PRE", "DOC", "RPT", "DEC", "MIN", "EVI", "OTH"]:
        items_cat = by_cat.get(cat_id, [])
        if not items_cat:
            continue
        L.append(f"# {cat_id} · {CAT_NAMES.get(cat_id, cat_id)} ({len(items_cat)})")
        L.append("")
        for s in items_cat:
            iid = s["id"]
            L.append(f"## {iid} · {s['name_ar']} `[{s['phase']}]`")
            L.append("")
            cands = s["candidates"]
            if not cands:
                L.append("> **لا توجد اقتراحات اعتماديات من أي طبقة.**")
                if s["prerequisites"]:
                    L.append(">")
                    L.append(f"> _Prerequisites (من فئة A، gates عامة):_ {', '.join(s['prerequisites'])}")
                if s.get("nlm_literal_answer"):
                    L.append(">")
                    L.append(f"> _NotebookLM literal:_ {s['nlm_literal_answer'].strip()[:200]}")
                if s.get("nlm_inferential_answer"):
                    L.append(">")
                    L.append(f"> _NotebookLM inferential:_ {s['nlm_inferential_answer'].strip()[:200]}")
                L.append("")
                L.append("**اعتمادية مؤكدة:** ⬜ لا يعتمد على غيره  /  ⬜ أضف يدويا في الملاحظات")
                L.append("")
                L.append("---")
                L.append("")
                continue

            # ترتيب المرشحين بحسب: عدد الطبقات DESC، ثم ID
            sorted_cands = sorted(
                cands.items(),
                key=lambda kv: (-len(kv[1]["layers"]), kv[0]),
            )
            L.append("| ID | الاسم | المرحلة | (أ) | (ب) | (ج₁) | (ج₂) | اعتماد |")
            L.append("|---|---|:---:|:---:|:---:|:---:|:---:|:---:|")
            for cid, info in sorted_cands:
                target = by_id.get(cid, {})
                tname = target.get("name_ar", cid)
                tphase = target.get("phase_abcdef", "?")
                a_mark = "✓" if "A" in info["layers"] else "—"
                b_mark = "✓" if "B" in info["layers"] else "—"
                c1_mark = "✓" if "C1" in info["layers"] else "—"
                c2_mark = "✓" if "C2" in info["layers"] else "—"
                tname_short = tname[:50].replace("|", "\\|")
                L.append(f"| {cid} | {tname_short} | {tphase} | {a_mark} | {b_mark} | {c1_mark} | {c2_mark} | ⬜ |")
            L.append("")
            if s["prerequisites"]:
                L.append(f"**Prerequisites (من فئة A، gates عامة):** {', '.join(s['prerequisites'])}")
                L.append("")
            if s.get("nlm_literal_answer"):
                ans = s["nlm_literal_answer"].strip()
                if len(ans) > 250:
                    ans = ans[:250] + "..."
                L.append(f"**NLM literal (ج₁):** {ans}")
                L.append("")
            if s.get("nlm_inferential_answer"):
                ans = s["nlm_inferential_answer"].strip()
                if len(ans) > 350:
                    ans = ans[:350] + "..."
                L.append(f"**NLM inferential (ج₂):** {ans}")
                L.append("")
            L.append("**ملاحظات/اعتماديات إضافية يدوية:**")
            L.append("- ")
            L.append("")
            L.append("---")
            L.append("")

    out_md = Path("knowledge/dependency-suggestions.md")
    out_md.write_text("\n".join(L), encoding="utf-8")
    print(f"[ok] {out_md}  ({out_md.stat().st_size:,} bytes)")
    # إحصاء سريع
    items_with_any_cand = sum(1 for s in structured.values() if s["candidates"])
    items_with_3_layer_agreement = 0
    items_with_2_layer_agreement = 0
    for s in structured.values():
        for info in s["candidates"].values():
            n = len(info["layers"])
            if n >= 3:
                items_with_3_layer_agreement += 1
                break
        else:
            for info in s["candidates"].values():
                if len(info["layers"]) >= 2:
                    items_with_2_layer_agreement += 1
                    break
    print(f"     items with any candidate: {items_with_any_cand}/{len(items)}")
    print(f"     items with 3-layer agreement: {items_with_3_layer_agreement}")
    print(f"     items with 2+layer agreement: {items_with_2_layer_agreement + items_with_3_layer_agreement}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
