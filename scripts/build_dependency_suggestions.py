"""
build_dependency_suggestions.py — يبني طبقتي اقتراحات اعتماديات (أ) و (ب).

(أ) قواعد المراحل من plan §5.0: لكل مخرج، المخرجات upstream حسب phase.
(ب) إشارات نصية: تطابقات لأسماء مخرجات أخرى داخل content_preview لكل مخرج.

المدخل: knowledge/deliverables-index.json (curated)
المخرج: knowledge/dep_suggestions_ab.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from datetime import datetime, timezone

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


# قواعد دورة الحياة من plan §5.0:
# - A: gate (شرط مسبق للجميع، لكن ليس "depends_on" بمعنى الاعتمادية المحتوى)
# - B → C, D, E
# - C → D, E, F
# - D → E
# - E → F
# - F → feedback لـ C/E (ليس upstream)
PHASE_UPSTREAM_DIRECT = {
    "A": [],
    "B": [],          # B لا يعتمد على شيء (A gate فقط، نفصلها)
    "C": ["B"],
    "D": ["B", "C"],
    "E": ["B", "C", "D"],
    "F": ["C", "E"],  # رسميا: B, D ينتقلان عبر C، نتركها للمراجع
}
GATE_PHASE = "A"  # A تُذكر كـ "prerequisite"، ليست "depends_on"


# بادئات شائعة تُحذف لاستخراج phrase دلالي
COMMON_PREFIXES = [
    "وثيقة", "وثائق", "تقرير", "التقرير", "قرار", "قرارات",
    "محاضر", "محضر", "إنجاز", "انجاز", "رقمنة",
    "عقود", "عقد", "قائمة", "سجل", "نماذج", "بطاقات",
    "اشتراطات", "ميثاق", "سياسة",
]

# عبارات شائعة جدا تُتجاهَل في تطابق layer (ب) (لتقليل false positives)
TOO_COMMON_PHRASES = {
    "البنية المؤسسية", "البنية", "المؤسسية",
    "الحوكمة", "الوحدة التنظيمية",
}


def extract_key_phrase(name: str) -> str:
    """يستخرج phrase دلالي من اسم المخرج (يحذف البادئة الشائعة)."""
    name = name.strip()
    for prefix in COMMON_PREFIXES:
        # حذف البادئة + المسافة الفاصلة بعدها (إن وُجدت)
        if name.startswith(prefix + " "):
            return name[len(prefix) + 1:].strip()
        if name == prefix:
            return name
        # بادئة بدون مسافة (نادر، نتجنب الخطأ)
    return name


def build_layer_a(items: list[dict]) -> dict[str, dict]:
    """طبقة (أ): لكل مخرج، اقتراحات upstream من قواعد المراحل."""
    by_phase: dict[str, list[str]] = {}
    for it in items:
        ph = it.get("phase_abcdef", "?")
        by_phase.setdefault(ph, []).append(it["id"])

    out: dict[str, dict] = {}
    for it in items:
        ph = it.get("phase_abcdef", "?")
        upstream_phases = PHASE_UPSTREAM_DIRECT.get(ph, [])
        depends_on = []
        for up_ph in upstream_phases:
            for cand_id in by_phase.get(up_ph, []):
                if cand_id != it["id"]:
                    depends_on.append({"target_id": cand_id, "from_phase": up_ph})
        # gate: A تُذكر كـ prerequisites (ليست depends_on)
        prereqs = []
        if ph != GATE_PHASE:
            for cand_id in by_phase.get(GATE_PHASE, []):
                prereqs.append({"target_id": cand_id})
        out[it["id"]] = {
            "depends_on": depends_on,
            "prerequisites": prereqs,
        }
    return out


def build_layer_b(items: list[dict]) -> dict[str, list[dict]]:
    """طبقة (ب): إشارات نصية في content_preview تطابق phrases لمخرجات أخرى."""
    # phrases لكل مخرج
    phrases: dict[str, str] = {}
    for it in items:
        kp = extract_key_phrase(it["name_ar"])
        phrases[it["id"]] = kp

    out: dict[str, list[dict]] = {}
    for it in items:
        my_id = it["id"]
        content = (it.get("content_preview") or "").strip()
        my_phrase = phrases[my_id]
        hits: list[dict] = []
        if not content:
            out[my_id] = []
            continue
        for other_id, other_phrase in phrases.items():
            if other_id == my_id:
                continue
            # تجاهل phrases قصيرة جدا أو شائعة جدا
            if len(other_phrase) < 8:
                continue
            if other_phrase in TOO_COMMON_PHRASES:
                continue
            if other_phrase.split() and len(other_phrase.split()) < 2:
                continue
            # تجاهل التطابقات الذاتية (overlapping phrases)
            if other_phrase == my_phrase or my_phrase in other_phrase or other_phrase in my_phrase:
                continue
            if other_phrase in content:
                hits.append({
                    "target_id": other_id,
                    "matched_phrase": other_phrase,
                })
        out[my_id] = hits
    return out


def main() -> int:
    src = Path("knowledge/deliverables-index.json")
    if not src.exists():
        print(f"[error] {src} not found")
        return 1
    d = json.loads(src.read_text(encoding="utf-8"))
    items = d["deliverables"]

    layer_a = build_layer_a(items)
    layer_b = build_layer_b(items)

    out = {
        "meta": {
            "source": str(src).replace("\\", "/"),
            "items_count": len(items),
            "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "method": "phase_rules + content_text_matching",
            "notes": "layer_a from plan §5.0; layer_b conservative substring match (filters too-common phrases)",
        },
        "layer_a_phase_rules": layer_a,
        "layer_b_text_signals": layer_b,
    }
    out_path = Path("knowledge/dep_suggestions_ab.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    # إحصاءات
    edges_a_dep = sum(len(v["depends_on"]) for v in layer_a.values())
    edges_a_pre = sum(len(v["prerequisites"]) for v in layer_a.values())
    items_with_b = sum(1 for v in layer_b.values() if v)
    edges_b = sum(len(v) for v in layer_b.values())
    print(f"[ok] {out_path}")
    print(f"     layer (أ) phase-rule depends_on  : {edges_a_dep} edges")
    print(f"     layer (أ) phase-rule prerequisites: {edges_a_pre} edges")
    print(f"     layer (ب) text-signal hits        : {edges_b} hits across {items_with_b}/{len(items)} items")
    return 0


if __name__ == "__main__":
    sys.exit(main())
