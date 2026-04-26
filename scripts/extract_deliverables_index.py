"""
extract_deliverables_index.py — يبني الفهرس المبدئي للمخرجات من PDF المرجعي.

الاستراتيجية:
1. كشف حدود الفئات السبع عبر font-size=28 + bold (عناوين معيارية .0X<name>)
2. تقسيم النص حسب الفئة (عبر page-range + y-position داخل الصفحة عند الدمج)
3. اكتشاف عناوين المخرجات داخل كل فئة عبر أنماط محتوى (regex)
4. تصنيف كل مخرج على مراحل A-F (حسب الفئة + كلمات مفتاحية)
5. إخراج JSON مع status="extracted_pending_review" — يتطلب مراجعة بشرية

المدخل: extracted/primary-spec/primary-spec.extracted.json (مع --with-blocks)
المخرج: extracted/primary-spec/deliverables-index.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass


# -----------------------------------------------------------------------------
# قواميس الفئات والمراحل
# -----------------------------------------------------------------------------

# أنماط عناوين الفئات كما تظهر في blocks font-size=28
# ملاحظة: النص المُستخرَج يحوي "اال" بدل "الا" أحيانا (تفكيك ligature)
CATEGORY_PATTERNS = [
    # (id, name_ar_canonical, regex)
    ("PRE", "الاشتراطات", re.compile(r"\.?\s*0?1\s*(ا?ا|ا)الشتراطات")),
    ("DOC", "الوثائق", re.compile(r"\.?\s*0?2\s*(ا?ا|ا)لوثائق")),
    ("RPT", "التقارير", re.compile(r"\.?\s*0?3\s*التقارير")),
    ("DEC", "القرارات", re.compile(r"\.?\s*0?4\s*القرارات")),
    ("MIN", "المحاضر", re.compile(r"\.?\s*0?5\s*المحاضر")),
    ("EVI", "الشواهد", re.compile(r"\.?\s*0?6\s*شواهد")),
    ("OTH", "ملفات أخرى", re.compile(r"\.?\s*0?7\s*ملفات\s*أخرى")),
]

# تصنيف الفئة → مرحلة افتراضية من A-F (يُدقّق لاحقا بالكلمات المفتاحية)
CATEGORY_TO_DEFAULT_PHASE = {
    "PRE": "A",   # Pre-conditions
    "DOC": "C",   # Strategic Direction افتراضي (يُحسّن بالكلمات المفتاحية)
    "RPT": "F",   # Run & Monitor
    "DEC": "B",   # Organizational Setup
    "MIN": "F",   # Run & Monitor (minutes = monitoring artifacts)
    "EVI": "F",   # Run & Monitor (evidence = execution proof)
    "OTH": "B",   # Other files (roles, contracts, stakeholder lists)
}

# قواعد ترقية/تخفيض المرحلة بناء على كلمات مفتاحية في عنوان/نص المخرج
PHASE_KEYWORDS = [
    # (phase, pattern_ar) — أولوية: أول match يفوز
    # E = As-Is / To-Be / Gap / Roadmap
    ("E", re.compile(r"خارطة\s+الطريق|الحالة\s+(الراهنة|المستهدفة)|الفجوات")),
    # D = Practice Blueprint: models, perspectives, requirements, cycles, operational plan/model
    ("D", re.compile(
        r"النموذج\s+(العام|التشغيلي)"
        r"|مناظير"
        r"|متطلبات"
        r"|جدوى"
        r"|(دورة|دورات)\s+تطوير"
        r"|النماذج\s+المرجعية"
        r"|الخطة\s+التشغيلية|خطة\s+التشغيل"
    )),
    # C = Strategic Direction: strategy, charter, policy, principles, training/comm/awareness plans
    ("C", re.compile(
        r"استراتيجية"
        r"|ميثاق"
        r"|إطار\s+الحوكمة"
        r"|خطة\s+(التدريب|التواصل|تعزيز|تطوير\s+القدرات)"
        r"|سياسة"
        r"|مبادئ"
    )),
    # B = Organizational Setup: decisions, appointments, roles, lists, contracts, stakeholders
    ("B", re.compile(
        r"قرار"
        r"|تعيين|تكليف|تأسيس|تشكيل"
        r"|الهيكل\s+التنظيمي"
        r"|الوصف\s+الوظيفي"
        r"|قائمة|قوائم"
        r"|عقد|عقود"
        r"|أصحاب\s+المصلحة|المستفيدين"
        r"|أدوار"
    )),
]

# أنماط بدء عناوين المخرجات (heuristic) — للتقسيم داخل النص
DELIVERABLE_START_PATTERNS = {
    "DOC": re.compile(r"^\s*(وثائق?|سياسة|ميثاق)\b"),
    "RPT": re.compile(r"^\s*(التقرير|تقرير|تقارير)\b"),
    "DEC": re.compile(r"^\s*(قرار|قرارات)\b"),
    "MIN": re.compile(r"^\s*(محضر|محاضر)\b"),
    "EVI": re.compile(r"^\s*(إنجاز|انجاز|رقمنة|توثيق)\b"),
    "OTH": re.compile(r"^\s*(قائمة|عقد|وصف|دليل)\b"),
}

# أنماط جهات الاعتماد (approval authority) — لأكتشف نهاية مخرج
APPROVAL_AUTHORITY_PATTERNS = [
    re.compile(r"المسؤول\s+الأول(\s+أو\s+من\s+ينوب\s+عنه)?"),
    re.compile(r"لجنة\s+(حوكمة\s+)?البنية\s+المؤسسية"),
    re.compile(r"لجنة\s+التحول\s+الرقمي"),
    re.compile(r"مدير\s+البنية\s+المؤسسية"),
    re.compile(r"الوحدة\s+التنظيمية"),
]


# -----------------------------------------------------------------------------
# دوال مساعدة
# -----------------------------------------------------------------------------

def detect_section_markers(pages: list[dict]) -> list[dict]:
    """يمشي على blocks بحثا عن عناوين الفئات الكبيرة (fs≥25 + bold).
    يُرجع markers مرتبة ومُدمجة (running headers تتكرر بنفس الفئة → نحتفظ بأول ظهور فقط).
    """
    raw_markers = []
    for p in pages:
        for b in p.get("blocks", []):
            if not b.get("is_bold"):
                continue
            if b.get("max_font_size", 0) < 25:
                continue
            text = (b.get("text") or "").strip()
            for cat_id, name_ar, rgx in CATEGORY_PATTERNS:
                if rgx.search(text):
                    bbox = b.get("bbox") or [0, 0, 0, 0]
                    raw_markers.append({
                        "cat_id": cat_id,
                        "name_ar": name_ar,
                        "page": p["page_number"],
                        "y_top": bbox[1],
                        "y_bottom": bbox[3],
                        "raw_text": text,
                    })
                    break
    raw_markers.sort(key=lambda m: (m["page"], m["y_top"]))

    # إزالة running headers: إذا تتالت markers بنفس cat_id، احتفظ بالأولى فقط
    # (نفس الفئة تتكرر في صفحاتها → نريد بداية الفئة فقط)
    deduped = []
    last_cat = None
    for m in raw_markers:
        if m["cat_id"] == last_cat:
            continue
        deduped.append(m)
        last_cat = m["cat_id"]
    return deduped


def categorize_pages(pages: list[dict], markers: list[dict]) -> list[dict]:
    """لكل marker يحدد نطاق الصفحات/المناطق التي تتبعه حتى الـ marker التالي."""
    regions = []
    for i, m in enumerate(markers):
        if i + 1 < len(markers):
            nxt = markers[i + 1]
            end_page = nxt["page"]
            end_y = nxt["y_top"] if nxt["page"] == m["page"] else None
        else:
            end_page = pages[-1]["page_number"]
            end_y = None
        regions.append({
            **m,
            "end_page": end_page,
            "end_y": end_y,
        })
    return regions


def collect_region_lines(pages: list[dict], region: dict) -> tuple[list[dict], list[int]]:
    """يجمع أسطر الفئة (line-level مع bbox) — مرتبة بـ y-band ثم x_right تنازليا للـRTL.

    يُرجع list[{text, bbox, page}] جاهزة لاستهلاك المكثّف مع فلترة الأعمدة.
    """
    start_p = region["page"]
    end_p = region["end_page"]
    start_y = region["y_bottom"]
    end_y = region["end_y"]

    all_lines: list[dict] = []
    pages_used: list[int] = []

    for p in pages:
        pno = p["page_number"]
        if pno < start_p or pno > end_p:
            continue
        blocks = p.get("blocks", [])
        page_had_content = False
        for b in blocks:
            b_bbox = b.get("bbox") or [0, 0, 0, 0]
            b_y_top = b_bbox[1]
            b_y_bot = b_bbox[3]
            if pno == start_p and b_y_top < start_y:
                continue
            if pno == end_p and end_y is not None and b_y_bot > end_y:
                continue
            # أسطر داخلية مع bbox لكل واحد
            for ln in b.get("lines", []):
                ln_bbox = ln.get("bbox") or b_bbox
                ln_text = (ln.get("text") or "").strip()
                if not ln_text:
                    continue
                all_lines.append({
                    "text": ln_text,
                    "bbox": ln_bbox,
                    "page": pno,
                })
                page_had_content = True
        if page_had_content:
            pages_used.append(pno)

    # ترتيب: page أولا، ثم y-band (10 px) داخل الصفحة، ثم x_right تنازليا (RTL)
    all_lines.sort(
        key=lambda l: (
            l["page"],
            int((l["bbox"][1] + l["bbox"][3]) / 2 / 10) * 10,
            -l["bbox"][2],
        )
    )
    return all_lines, pages_used


def collect_region_text(pages: list[dict], region: dict) -> tuple[str, list[int]]:
    """Backward-compat: يُرجع النص مسطّحا (ليس المفضّل — استخدم collect_region_lines)."""
    lines_data, pages_used = collect_region_lines(pages, region)
    return "\n".join(l["text"] for l in lines_data), pages_used


# -----------------------------------------------------------------------------
# اكتشاف المخرجات داخل الفئة
# -----------------------------------------------------------------------------

# كلمات تشير لبدء "صف" جديد داخل الجدول (بداية عنوان مخرج)
TITLE_LEADING_WORDS = {
    "DOC": ["وثيقة", "وثائق", "سياسة", "ميثاق"],
    "RPT": ["التقرير", "تقرير"],
    "DEC": ["قرار", "قرارات"],
    "MIN": ["محضر", "محاضر", "اجتماع"],
    "EVI": ["إنجاز", "انجاز", "رقمنة", "توثيق", "شواهد"],
    "OTH": ["قائمة", "عقد", "عقود", "وصف", "دليل", "بطاقة", "سجل"],
}

# كلمات تشير لجهة اعتماد (نهاية صف)
AUTHORITY_MARKERS = [
    "المسؤول الأول", "المسؤول الاول",
    "لجنة حوكمة البنية", "لجنة حوكمة",
    "لجنة التحول الرقمي",
    "مدير البنية المؤسسية",
    "الوحدة التنظيمية",
]

# رؤوس الأعمدة — تُعامَل كضجيج أثناء اكتشاف المخرجات
COLUMN_HEADERS = frozenset({
    "اسم الوثيقة", "محتوى الوثيقة", "مستوى الاعتماد", "مستوى االعتماد",
    "القرار", "محتوى القرار",
    "المحضر", "محتوى المحضر",
    "الشواهد", "اثباتات الشواهد",
    "اسم الملف", "محتوى الملف",
    "اسم التقرير", "محتوى التقرير",
})

# تذييل الصفحة وما شابه — نشمل "ة 06" (استمرارية footer المقطوع على سطرين)
FOOTER_RE = re.compile(
    r"^(Public\s*-?\s*عام"
    r"|مخرجات\s+ممارسة.*\d+"
    r"|ة\s*\d{1,2}"
    r")$"
)

# عناوين الأقسام الكبرى (".02الوثائق" إلخ) — تظهر كـ running headers
SECTION_HEADER_RE = re.compile(
    r"\.\s*0?\d\s*(الاشتراطات|الوثائق|التقارير|القرارات|المحاضر|شواهد|الشواهد|ملفات)"
)

# Fragments عربية شائعة غير مستقلة ككلمة — تُدمَج مع ما قبلها (ازالة الفراغ الزائف)
# مستخلصة من diff مع NotebookLM على 20 مخرج DOC
FRAGMENT_WHITELIST = frozenset({
    # 1-char word-finals
    "ة", "ي", "ى", "ا", "و", "ه",
    # 2-char common suffixes
    "ية", "ات", "ين", "ون", "ني", "ير", "يل", "ان", "نا", "نة",
    # 3-char fragments
    "سية", "مية", "رية", "فية", "جية", "نية", "بية", "تية", "وية",
    # 4-char observed
    "سسية",
})


# ----------------------------------------------------------------------
# مساعدات تنظيف العناوين (post-NotebookLM diff fixes)
# ----------------------------------------------------------------------

def _fix_intra_word_spaces(text: str) -> str:
    """ادمج كسور الكلمات المعروفة مع سابقها (مثل 'المؤ سسية' → 'المؤسسية').
    آمن: لا يدمج كلمات مستقلة — يعتمد على whitelist من fragments غير مستقلة.
    """
    tokens = text.split()
    if len(tokens) < 2:
        return text
    result: list[str] = []
    for tok in tokens:
        if tok in FRAGMENT_WHITELIST and result:
            result[-1] = result[-1] + tok
        else:
            result.append(tok)
    return " ".join(result)


def _strip_title_noise(text: str) -> str:
    """إزالة رموز ترقيم الزائدة في طرفي العنوان (•، .، :، إلخ)."""
    noise_chars = "•.:,،;؛"
    text = text.strip()
    while text and text[-1] in noise_chars:
        text = text[:-1].rstrip()
    while text and text[0] in noise_chars:
        text = text[1:].lstrip()
    return text


def _is_continuation_terminator(ln: str) -> bool:
    """هل هذا السطر ينهي تراكم العنوان (bullet, رقم، جهة اعتماد)؟"""
    if ln.startswith("•"):
        return True
    if re.fullmatch(r"\d{1,2}", ln):
        return True
    if any(a in ln for a in AUTHORITY_MARKERS):
        return True
    return False


def _all_title_starters() -> frozenset[str]:
    s: set[str] = set()
    for words in TITLE_LEADING_WORDS.values():
        s.update(words)
    return frozenset(s)


_TITLE_STARTERS_ALL = _all_title_starters()


# عتبة x_right لعمود العنوان في جداول RTL (يمين الصفحة).
# نستخدم x_right بدل x_left لأن بعض الأسطر تمتد لليسار (عبر خلايا مدموجة)
# لكن حافتها اليمنى في عمود العناوين. محتوى الجداول الأخرى x_right ≤ 382،
# وعمود العنوان x_right ≥ 415 → عتبة 400 آمنة.
TITLE_COLUMN_X_RIGHT_MIN = 400.0


def _is_in_title_column(bbox: list) -> bool:
    """هل bbox هذا السطر يقع في عمود العناوين (يمين الصفحة في جدول RTL)؟
    نعتمد على x_right لا x_left: الـ blocks المدموجة تبدأ من اليسار أحيانا
    لكن نص العنوان يمتد للحافة اليمنى.
    """
    if not bbox or len(bbox) < 4:
        return False
    x_right = bbox[2]
    return x_right >= TITLE_COLUMN_X_RIGHT_MIN


def _accumulate_title_xaware(
    lines_data: list[dict],
    start_idx: int,
    leaders: list[str],
    max_parts: int = 5,
    scan_limit: int = 15,
) -> tuple[str, set[int]]:
    """يتراكم العنوان عبر السطور — فقط من عمود العنوان (x_right >= 400).
    قيود حاسمة:
    - لا يعبر حدود الصفحة (page boundary) → يتوقف عند أول صفحة مختلفة.
    - يتوقف على section headers (مثل .02الوثائق) بصفتها running headers.
    - يتخطى (لا يمتص) سطور خارج عمود العنوان و FOOTERs و COLUMN_HEADERs.
    يُرجع (العنوان المُدمَج، set من indexes للسطور المُستهلَكة).
    """
    start_line = lines_data[start_idx]
    start_page = start_line["page"]
    parts: list[str] = [start_line["text"]]
    absorbed: set[int] = {start_idx}
    i = start_idx + 1
    scanned = 0
    while i < len(lines_data) and scanned < scan_limit and len(parts) < max_parts:
        nxt = lines_data[i]
        # حد الصفحة — لا نعبر
        if nxt["page"] != start_page:
            break
        ln = nxt["text"].strip()

        # تخطَّ السطور خارج عمود العنوان (content/authority/serial) — لا تتوقف
        if not _is_in_title_column(nxt["bbox"]):
            i += 1
            scanned += 1
            continue

        # داخل عمود العنوان: تحقق إن كان استمرارية أم terminator
        first = ln.split()[0] if ln.split() else ""
        if first in _TITLE_STARTERS_ALL and not ln.startswith("•"):
            break  # مخرج جديد
        if _is_continuation_terminator(ln):
            break  # bullet/رقم/جهة
        if SECTION_HEADER_RE.search(ln):
            break  # .02الوثائق / .03التقارير … إلخ — running header
        if ln in COLUMN_HEADERS or FOOTER_RE.match(ln):
            i += 1
            scanned += 1
            continue
        # استمرارية عنوان شرعية
        parts.append(ln)
        absorbed.add(i)
        i += 1
        scanned += 1
    return " ".join(parts), absorbed


def split_deliverables_from_region(lines_data: list[dict], cat_id: str) -> list[dict]:
    """تقسيم heuristic لأسطر الفئة إلى مخرجات مرشحة (x-aware — v3).

    يأخذ list[{text, bbox, page}] مرتبة بالفعل (y-band, -x_right).
    - العناوين تُكشَف فقط من عمود العنوان (x_left >= TITLE_COLUMN_X_MIN).
    - تراكم العنوان يتخطى السطور خارج العمود (content/authority) دون التوقف.
    - السطور التي لم تُستوعَب في عنوان تُعالَج كـ content/authority/serial للمخرج الحالي.
    """
    leading = TITLE_LEADING_WORDS.get(cat_id, [])
    if not leading:
        return _split_prerequisites([l["text"] for l in lines_data])

    candidates: list[dict] = []
    current: dict | None = None
    absorbed_into_title: set[int] = set()
    # في ترتيبنا (y-band, -x_right)، رقم التسلسل غالبا يسبق عنوانه بالسطر
    # (x_right للسريال=564 > x_right للعنوان=533). لذا نأخّر ربطه للعنوان القادم.
    pending_serial: int | None = None
    i = 0
    while i < len(lines_data):
        if i in absorbed_into_title:
            i += 1
            continue
        ln_obj = lines_data[i]
        ln = ln_obj["text"].strip()

        if ln in COLUMN_HEADERS or FOOTER_RE.match(ln) or SECTION_HEADER_RE.search(ln):
            i += 1
            continue

        first_word = ln.split()[0] if ln.split() else ""
        is_new_title = (
            _is_in_title_column(ln_obj["bbox"])
            and any(first_word == w or first_word.startswith(w) for w in leading)
            and not ln.startswith("•")
        )

        if is_new_title:
            if current and current.get("name_ar"):
                candidates.append(current)
            title_raw, absorbed = _accumulate_title_xaware(lines_data, i, leading)
            absorbed_into_title.update(absorbed)
            title_clean = _strip_title_noise(_fix_intra_word_spaces(title_raw))
            current = {
                "name_ar": title_clean,
                "body_lines": [],
                "authorities": [],
                "serial": pending_serial,  # استهلك أي رقم تسلسلي معلّق
            }
            pending_serial = None
            i += 1
            continue

        # رقم تسلسلي (عمود السريال) — احتفظ به للعنوان القادم
        if re.fullmatch(r"\d{1,2}", ln):
            pending_serial = int(ln)
            i += 1
            continue

        if current is None:
            i += 1
            continue

        # جهة اعتماد؟
        hit_auth = next((a for a in AUTHORITY_MARKERS if a in ln), None)
        if hit_auth:
            cleaned_auth = _strip_title_noise(ln)
            if cleaned_auth and cleaned_auth not in current["authorities"]:
                current["authorities"].append(cleaned_auth)
            i += 1
            continue
        # محتوى
        current["body_lines"].append(ln)
        i += 1

    if current and current.get("name_ar"):
        candidates.append(current)

    # تنظيف + فلترة ضجيج
    cleaned: list[dict] = []
    for c in candidates:
        name = (c["name_ar"] or "").strip()
        if not name:
            continue
        if len(name) < 8 or len(name.split()) < 2:
            continue
        body_text = "\n".join(c["body_lines"]).strip()
        cleaned.append({
            "name_ar": name,
            "content_raw": body_text[:2000],
            "approval_authorities": list(c["authorities"]) or [],
            "serial_number": c["serial"],
        })
    return cleaned


def _split_prerequisites(lines: list[str]) -> list[dict]:
    """اشتراطات منظمة بأرقام 1.X — نتعامل معها كـ sub-sections.
    النص قد يفصل '1.X' عن عنوان القسم على سطرين → ندعم التركيب.
    """
    items: list[dict] = []
    current = None
    # النمط: '1.X' يتبعه إما نص على نفس السطر أو قيمة فارغة
    pattern = re.compile(r"^1\.(\d+)\s*(.*)$")
    awaiting_title = False  # إذا كان '1.X' وحيدا، خذ السطر التالي كعنوان

    for ln in lines:
        m = pattern.match(ln.strip())
        if m:
            if current:
                items.append(current)
            sub_num = m.group(1)
            inline_title = m.group(2).strip().rstrip(":")
            current = {
                "name_ar": inline_title,  # قد يكون فارغا
                "content_raw": "",
                "approval_authorities": [],
                "serial_number": None,
                "sub_section": f"1.{sub_num}",
            }
            awaiting_title = not inline_title
        elif current is None:
            continue
        elif awaiting_title:
            # أول سطر غير فارغ بعد '1.X' فارغ = عنوان القسم
            current["name_ar"] = ln.strip().rstrip(":")
            awaiting_title = False
        else:
            current["content_raw"] = (current["content_raw"] + "\n" + ln).strip()[:2000]

    if current:
        items.append(current)
    return items


# -----------------------------------------------------------------------------
# تصنيف المرحلة A-F
# -----------------------------------------------------------------------------

def classify_phase(cat_id: str, name_ar: str, content: str) -> str:
    """تصنيف المرحلة A-F — طبيعة الفئة أولا، ثم الكلمات المفتاحية على الاسم.
    فئات ثابتة (PRE→A، RPT/MIN/EVI→F) لأن طبيعتها تحدد المرحلة بشكل حاسم.
    الفئات المتغيرة (DOC، DEC، OTH) تُدقَّق بالكلمات المفتاحية على الاسم.
    """
    FIXED_PHASE = {"PRE": "A", "RPT": "F", "MIN": "F", "EVI": "F"}
    if cat_id in FIXED_PHASE:
        return FIXED_PHASE[cat_id]
    for phase, rgx in PHASE_KEYWORDS:
        if rgx.search(name_ar):
            return phase
    return CATEGORY_TO_DEFAULT_PHASE.get(cat_id, "?")


# -----------------------------------------------------------------------------
# بناء الفهرس النهائي
# -----------------------------------------------------------------------------

def make_code(cat_id: str, name_ar: str, idx: int) -> str:
    """كود مختصر بالإنجليزية — مؤقت، سيُحسّن بشريا لاحقا."""
    # للبساطة: CAT-NN (زيدان سيعيد التسمية في مرحلة التدقيق)
    return f"{cat_id}-{idx:02d}"


def build_index(extracted_path: Path, source_pdf_name: str) -> dict:
    raw = json.loads(extracted_path.read_text(encoding="utf-8"))
    pages = raw["pages"]
    meta_src = raw["meta"]

    markers = detect_section_markers(pages)
    regions = categorize_pages(pages, markers)

    deliverables: list[dict] = []
    idx_counter = {cat: 0 for cat, _, _ in CATEGORY_PATTERNS}
    regions_report = []

    for region in regions:
        cat_id = region["cat_id"]
        name_ar = region["name_ar"]
        region_lines, pages_used = collect_region_lines(pages, region)
        candidates = split_deliverables_from_region(region_lines, cat_id)

        regions_report.append({
            "cat_id": cat_id,
            "name_ar": name_ar,
            "start_page": region["page"],
            "end_page": region["end_page"],
            "pages_with_content": pages_used,
            "candidates_count": len(candidates),
        })

        for cand in candidates:
            idx_counter[cat_id] += 1
            i = idx_counter[cat_id]
            phase = classify_phase(cat_id, cand["name_ar"], cand.get("content_raw", ""))
            deliverables.append({
                "id": f"DEL-{cat_id}-{i:03d}",
                "code": make_code(cat_id, cand["name_ar"], i),
                "name_ar": cand["name_ar"],
                "category": name_ar,
                "category_id": cat_id,
                "phase_abcdef": phase,
                "approval_authorities": cand.get("approval_authorities") or [],
                "serial_number": cand.get("serial_number"),
                "content_preview": (cand.get("content_raw") or "")[:500],
                "raw_section_ref": {
                    "source_file": source_pdf_name,
                    "start_page": region["page"],
                    "end_page": region["end_page"],
                    "sub_section": cand.get("sub_section"),
                },
                "status": "extracted_pending_review",
            })

    return {
        "meta": {
            "source": source_pdf_name,
            "source_sha256_16": meta_src.get("source_sha256_16"),
            "extracted_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "extractor_script": Path(__file__).name,
            "extraction_status": "draft_requires_human_review",
            "categories_detected": len(regions),
            "total_deliverable_candidates": len(deliverables),
            "by_category": _sum_by_key(regions_report, "cat_id", "candidates_count"),
            "by_phase": _count_by(deliverables, "phase_abcdef"),
        },
        "categories": [
            {"cat_id": cat_id, "name_ar": name_ar}
            for cat_id, name_ar, _ in CATEGORY_PATTERNS
        ],
        "regions_report": regions_report,
        "deliverables": deliverables,
    }


def _count_by(items: list[dict], key: str) -> dict:
    out: dict = {}
    for it in items:
        k = it.get(key) or "?"
        out[k] = out.get(k, 0) + 1
    return dict(sorted(out.items()))


def _sum_by_key(items: list[dict], group_key: str, value_key: str) -> dict:
    out: dict = {}
    for it in items:
        k = it.get(group_key) or "?"
        out[k] = out.get(k, 0) + int(it.get(value_key) or 0)
    return dict(sorted(out.items()))


# -----------------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------------

def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="بناء فهرس مخرجات الدليل الرئيسي (مسودة للمراجعة)")
    p.add_argument("--extracted", default="extracted/primary-spec/primary-spec.extracted.json",
                   help="مسار JSON من pdf_extract.py")
    p.add_argument("-o", "--output", default="extracted/primary-spec/deliverables-index.json")
    p.add_argument("--source", default="مخرجات ممارسة البنية المؤسسية - مارس 2026.pdf",
                   help="اسم PDF المصدر (للتوثيق)")
    args = p.parse_args(argv)

    extracted_path = Path(args.extracted)
    if not extracted_path.exists():
        print(f"[error] extracted JSON not found: {extracted_path}")
        return 1

    index = build_index(extracted_path, args.source)

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")

    m = index["meta"]
    print(f"[ok] deliverables-index.json written → {out}")
    print(f"     categories detected : {m['categories_detected']}")
    print(f"     total candidates    : {m['total_deliverable_candidates']}")
    print(f"     by category         : {m['by_category']}")
    print(f"     by phase A-F        : {m['by_phase']}")
    print(f"     status              : {m['extraction_status']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
