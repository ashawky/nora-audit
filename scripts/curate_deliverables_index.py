"""
curate_deliverables_index.py — يطبّق تصحيحات المراجعة البشرية على فهرس المخرجات.

Source: extracted/primary-spec/deliverables-index.json (raw extractor output)
Target: knowledge/deliverables-index.json (human-curated baseline)

التصحيحات مأخوذة من agencies/_review/deliverables_review.md (املأها زيدان يدويا).
يُحفظ extracted كـ raw للتوثيق، curated يصبح المرجع للـ schemas اللاحقة.
"""

from __future__ import annotations

import json
import sys
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

# استيراد classifier لإعادة تصنيف phase بعد تعديل الاسم
sys.path.insert(0, str(Path(__file__).parent))
from extract_deliverables_index import classify_phase  # noqa: E402


# -----------------------------------------------------------------------------
# مواصفات التصحيحات
# -----------------------------------------------------------------------------

# تصحيحات الأسماء
NAME_EDITS: dict[str, str] = {
    "DEL-PRE-004": "اشتراطات فريق عمل الوحدة التنظيمية للبنية المؤسسية",
    "DEL-DOC-003": "وثائق الاستراتيجيات الرقمية",
    "DEL-DEC-003": "قرار تعيين كبير مهندسي البنية المؤسسية (مدير الوحدة التنظيمية)",
    "DEL-DEC-005": "قرار تشكيل لجنة حوكمة البنية المؤسسية",
    "DEL-DEC-006": "قرار تعميم ونشر نموذج الحوكمة",
    "DEL-RPT-005": "تقرير حالات دراسية لتطبيقات التقنيات الناشئة والحديثة",
    "DEL-RPT-006": "تقرير دراسة مقارنة معيارية وتحديد أداة البنية المؤسسية وتقييمها",
    "DEL-RPT-009": "تقرير الامتثال لمبادئ البنية المؤسسية",
    "DEL-MIN-002": "محاضر اجتماعات اللجان الرقمية (آخر 4 اجتماعات لكل لجنة)",
    "DEL-EVI-003": "رقمنة خدمات البنية المؤسسية",
    "DEL-EVI-004": "رقمنة إجراءات عمل البنية المؤسسية",
}

# قوائم جهات الاعتماد النهائية (تستبدل الموجود)
AUTHORITY_EDITS: dict[str, list[str]] = {
    "DEL-DOC-001": ["المسؤول الأول أو من ينيب عنه"],
    "DEL-DOC-002": ["المسؤول الأول أو من ينيب عنه"],
    "DEL-DOC-003": ["المسؤول الأول أو من ينيب عنه"],
    "DEL-DOC-004": ["لجنة التحول الرقمي / التعاملات الإلكترونية", "لجنة حوكمة البنية المؤسسية"],
    "DEL-DOC-005": ["المسؤول الأول أو من ينيب عنه"],
    "DEL-DOC-006": ["لجنة حوكمة البنية المؤسسية", "الوحدة التنظيمية ذات العلاقة"],
    "DEL-DOC-007": ["لجنة حوكمة البنية المؤسسية"],
    "DEL-DOC-008": ["لجنة حوكمة البنية المؤسسية"],
    "DEL-DOC-009": ["لجنة حوكمة البنية المؤسسية", "مدير البنية المؤسسية"],
    "DEL-DOC-010": ["لجنة حوكمة البنية المؤسسية"],
    "DEL-DOC-011": ["مدير البنية المؤسسية", "الوحدة التنظيمية ذات العلاقة"],
    "DEL-DOC-012": ["لجنة حوكمة البنية المؤسسية"],
    "DEL-DOC-013": ["لجنة حوكمة البنية المؤسسية"],
    "DEL-DOC-014": ["لجنة حوكمة البنية المؤسسية"],
    "DEL-DOC-015": ["لجنة حوكمة البنية المؤسسية"],
    "DEL-DOC-016": ["لجنة حوكمة البنية المؤسسية"],
    "DEL-DOC-017": ["لجنة حوكمة البنية المؤسسية"],
    "DEL-DOC-018": ["لجنة حوكمة البنية المؤسسية"],
    "DEL-DOC-019": ["لجنة حوكمة البنية المؤسسية"],
    "DEL-DOC-020": ["لجنة حوكمة البنية المؤسسية"],
    "DEL-RPT-001": ["لجنة حوكمة البنية المؤسسية"],
    "DEL-RPT-002": ["لجنة حوكمة البنية المؤسسية"],
    "DEL-RPT-003": ["لجنة حوكمة البنية المؤسسية"],
    "DEL-RPT-004": ["لجنة حوكمة البنية المؤسسية"],
    "DEL-RPT-005": ["لجنة حوكمة البنية المؤسسية"],
    # DEL-RPT-006: لا تغيير (الملاحظة لم تذكر جهة)
    "DEL-RPT-007": ["لجنة حوكمة البنية المؤسسية"],
    "DEL-RPT-008": ["لجنة حوكمة البنية المؤسسية"],
    "DEL-RPT-009": [
        "مدير البنية المؤسسية",
        "لجنة حوكمة البنية المؤسسية (في حالة التصعيد أو طلب من لجنة)",
    ],
    "DEL-DEC-003": ["المسؤول الأول أو من ينيب عنه"],
    "DEL-DEC-004": ["المسؤول الأول أو من ينيب عنه"],
    "DEL-DEC-005": ["المسؤول الأول أو من ينيب عنه"],
    "DEL-DEC-006": ["الإدارة المعنية"],
    "DEL-MIN-001": ["لجنة التحول الرقمي", "لجنة حوكمة البنية المؤسسية"],
    "DEL-MIN-002": ["لجنة التحول الرقمي", "لجنة حوكمة البنية المؤسسية", "اللجان الرقمية الأخرى"],
}

# تعديلات الـ serial (نادرة)
SERIAL_EDITS: dict[str, int] = {
    "DEL-DEC-006": 5,  # كان 4 (مكرّر)
}

# عمليات الدمج: primary_id يحتفظ، secondary_id يُحذف
MERGES: list[dict] = [
    {
        "primary_id": "DEL-DEC-001",
        "secondary_id": "DEL-DEC-002",
        "new_name": "قرارات تعيين و/أو تكليف رسمي لفريق عمل الوحدة التنظيمية للبنية المؤسسية",
        "new_authorities": ["المسؤول الأول أو من ينيب عنه"],
        "new_serial": 1,
    },
    {
        "primary_id": "DEL-OTH-001",
        "secondary_id": "DEL-OTH-002",
        "new_name": "عقود تشغيلية و/أو استشارية لفريق عمل الوحدة التنظيمية للبنية المؤسسية",
        "new_authorities": ["الوحدة التنظيمية ذات العلاقة", "مدير إدارة البنية المؤسسية"],
        "new_serial": 1,
    },
]

# عناصر جديدة (تُضاف لنهاية فئتها قبل إعادة الترقيم)
ADDITIONS: list[dict] = [
    {
        "category_id": "OTH",
        "category": "ملفات أخرى",
        "name_ar": "نماذج موحدة لحصر بيانات مكونات البنية المؤسسية",
        "phase_abcdef": "B",
        "approval_authorities": [],
        "serial_number": 3,
        "content_preview": "",
        "raw_section_ref": {
            "source_file": "مخرجات ممارسة البنية المؤسسية - مارس 2026.pdf",
            "manual_addition": True,
        },
        "status": "manually_added",
    },
    {
        "category_id": "OTH",
        "category": "ملفات أخرى",
        "name_ar": "بطاقات الوصف الوظيفي",
        "phase_abcdef": "B",
        "approval_authorities": ["الوحدة التنظيمية ذات العلاقة"],
        "serial_number": 4,
        "content_preview": "",
        "raw_section_ref": {
            "source_file": "مخرجات ممارسة البنية المؤسسية - مارس 2026.pdf",
            "manual_addition": True,
        },
        "status": "manually_added",
    },
]


# -----------------------------------------------------------------------------
# منطق المعالجة
# -----------------------------------------------------------------------------

def apply_curation(raw: dict) -> dict:
    out = deepcopy(raw)
    items = out["deliverables"]

    # 1) تطبيق دمج: أزل secondary، حدّث primary بالقيم الجديدة
    deleted_ids: set[str] = set()
    for merge in MERGES:
        pid = merge["primary_id"]
        sid = merge["secondary_id"]
        primary = next((it for it in items if it["id"] == pid), None)
        if primary is None:
            print(f"[warn] merge primary not found: {pid}")
            continue
        primary["name_ar"] = merge["new_name"]
        primary["approval_authorities"] = list(merge["new_authorities"])
        primary["serial_number"] = merge["new_serial"]
        primary["status"] = "curated_merged"
        primary["merged_from"] = [pid, sid]
        deleted_ids.add(sid)

    # 2) أزل secondary من القائمة
    items = [it for it in items if it["id"] not in deleted_ids]

    # 3) طبّق NAME_EDITS / AUTHORITY_EDITS / SERIAL_EDITS على ما تبقّى
    for it in items:
        old_id = it["id"]
        if old_id in NAME_EDITS:
            it["name_ar"] = NAME_EDITS[old_id]
            # إعادة تصنيف phase بناء على الاسم الجديد
            new_phase = classify_phase(it["category_id"], it["name_ar"], it.get("content_preview", ""))
            if new_phase != it.get("phase_abcdef"):
                it["phase_abcdef"] = new_phase
            it.setdefault("status", "curated")
            if it["status"] not in ("curated_merged",):
                it["status"] = "curated"
        if old_id in AUTHORITY_EDITS:
            it["approval_authorities"] = list(AUTHORITY_EDITS[old_id])
            it.setdefault("status", "curated")
        if old_id in SERIAL_EDITS:
            it["serial_number"] = SERIAL_EDITS[old_id]
            it.setdefault("status", "curated")

    # 4) أضف الإضافات
    for add in ADDITIONS:
        new_item = deepcopy(add)
        # سيُعاد توليد id في خطوة الترقيم لاحقا
        new_item["id"] = "TBD-" + new_item["category_id"]
        new_item.setdefault("code", "TBD")
        items.append(new_item)

    # 5) أعد ترقيم IDs و codes داخل كل فئة (حافظ على الترتيب الحالي)
    counters: dict[str, int] = {}
    for it in items:
        cat = it["category_id"]
        counters[cat] = counters.get(cat, 0) + 1
        n = counters[cat]
        new_id = f"DEL-{cat}-{n:03d}"
        new_code = f"{cat}-{n:02d}"
        old_id = it.get("id")
        if old_id and not old_id.startswith("TBD-") and old_id != new_id:
            it["renumbered_from"] = old_id
        it["id"] = new_id
        it["code"] = new_code

    out["deliverables"] = items

    # 6) حدّث meta
    cat_counts: dict[str, int] = {}
    phase_counts: dict[str, int] = {}
    for it in items:
        cat_counts[it["category_id"]] = cat_counts.get(it["category_id"], 0) + 1
        ph = it.get("phase_abcdef") or "?"
        phase_counts[ph] = phase_counts.get(ph, 0) + 1

    out["meta"] = {
        **raw["meta"],
        "extraction_status": "curated_human_reviewed",
        "curated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "curated_from": "extracted/primary-spec/deliverables-index.json",
        "curated_by_script": Path(__file__).name,
        "total_deliverable_candidates": len(items),
        "by_category": dict(sorted(cat_counts.items())),
        "by_phase": dict(sorted(phase_counts.items())),
    }
    return out


def main() -> int:
    src = Path("extracted/primary-spec/deliverables-index.json")
    if not src.exists():
        print(f"[error] source not found: {src}")
        return 1
    raw = json.loads(src.read_text(encoding="utf-8"))
    curated = apply_curation(raw)

    out = Path("knowledge/deliverables-index.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(curated, ensure_ascii=False, indent=2), encoding="utf-8")

    m = curated["meta"]
    print(f"[ok] curated index → {out}")
    print(f"     total           : {m['total_deliverable_candidates']}")
    print(f"     by_category     : {m['by_category']}")
    print(f"     by_phase A-F    : {m['by_phase']}")
    print(f"     status          : {m['extraction_status']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
