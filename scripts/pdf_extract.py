"""
pdf_extract.py — استخراج PDF عربي إلى JSON منظم (PyMuPDF-based)

يُنتج: meta (مصدر + hash + توقيت) + pages[] (text منظّف + tables + اختياريا blocks)
الترتيب منطقي RTL مباشرة من PyMuPDF. تطبيع Unicode: NFC + إزالة tatweel + PUA + zero-width.

الاستخدام:
    python pdf_extract.py <input.pdf> [-o <output.json>] [--max-pages N] [--with-blocks] [-v]
"""

import argparse
import hashlib
import json
import logging
import re
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

import fitz  # PyMuPDF

# Windows cp1252 لا يدعم العربية — إجبار UTF-8 على stdout/stderr
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

# كتم تحذيرات MuPDF من نوع "No common ancestor in structure tree"
# (تحذيرات structure tree للـ accessibility — لا تؤثر على استخراج النص)
for _method in ("mupdf_display_warnings", "mupdf_display_errors"):
    try:
        getattr(fitz.TOOLS, _method)(False)
    except Exception:
        pass

logger = logging.getLogger("pdf_extract")


# ----------------------------------------------------------------------
# تطبيع Unicode للعربية
# ----------------------------------------------------------------------

TATWEEL = "\u0640"  # ـ  زخرفة، لا تحمل معنى
_PUA_RANGE = re.compile(r"[\uE000-\uF8FF]")  # Private Use Area (glyph subs)
_ZERO_WIDTH = re.compile(r"[\u200B-\u200F\u202A-\u202E\u2060-\u206F\uFEFF]")
_MULTI_SPACE = re.compile(r"[ \t]+")
_MULTI_NEWLINE = re.compile(r"\n{3,}")
_TRAILING_SPACE_BEFORE_NL = re.compile(r" +\n")

# إصلاح تبديل ligature lam-alef في PDFs عربية:
# المُستخرَج: ا + <hamza-variant> + ل   (مثل "األ" = U+0627 U+0623 U+0644)
# الصحيح   : ا + ل + <hamza-variant>   (مثل "الأ" = U+0627 U+0644 U+0623)
# الـ hamza-variants: ء (U+0621) أ (U+0623) آ (U+0622) إ (U+0625) ؤ (U+0624) ئ (U+0626)
_LAM_ALEF_SWAP = re.compile(r"ا([\u0621-\u0626])ل")


def normalize_text(text: str) -> str:
    """تطبيع محافظ للعربية (آمن دلاليا — لا hamza folding).

    يشمل:
    - NFC توحيد التطبيع.
    - إزالة PUA + zero-width + tatweel.
    - توحيد المسافات والأسطر.
    - إصلاح تبديل lam-alef ligature في PDFs (األ → الأ، اإل → الإ، اآل → الآ).
    """
    if not text:
        return ""
    text = unicodedata.normalize("NFC", text)
    text = _PUA_RANGE.sub("", text)
    text = _ZERO_WIDTH.sub("", text)
    text = text.replace(TATWEEL, "")
    # إصلاح تبديل lam-alef (يُطبَّق قبل collapse whitespace لأن الأنماط محلية)
    text = _LAM_ALEF_SWAP.sub(r"ال\1", text)
    text = _MULTI_SPACE.sub(" ", text)
    text = _TRAILING_SPACE_BEFORE_NL.sub("\n", text)
    text = _MULTI_NEWLINE.sub("\n\n", text)
    return text.strip()


# ----------------------------------------------------------------------
# استخراج الجداول
# ----------------------------------------------------------------------

def extract_page_tables(page) -> list[dict]:
    """كل جدول: bbox + n_rows + n_cols + rows (كل خلية مطبّعة)."""
    try:
        finder = page.find_tables()
    except Exception as e:
        logger.debug(f"find_tables failed on page {page.number + 1}: {e}")
        return []
    if finder is None:
        return []
    out: list[dict] = []
    for t in finder.tables:
        try:
            rows = t.extract() or []
        except Exception as e:
            logger.debug(f"table extract failed on page {page.number + 1}: {e}")
            continue
        clean_rows = [
            [normalize_text(c) if isinstance(c, str) else "" for c in row]
            for row in rows
        ]
        if not any(any(cell for cell in row) for row in clean_rows):
            continue  # جدول فارغ كليا
        out.append({
            "bbox": [round(v, 2) for v in t.bbox],
            "n_rows": len(clean_rows),
            "n_cols": max((len(r) for r in clean_rows), default=0),
            "rows": clean_rows,
        })
    return out


# ----------------------------------------------------------------------
# استخراج blocks مع font-size (لكشف العناوين لاحقا)
# ----------------------------------------------------------------------

def extract_page_blocks(page) -> list[dict]:
    """يستخرج blocks مع lines داخلية (نص + bbox + font) — مهم لتصفية الأعمدة في الجداول."""
    try:
        data = page.get_text("dict")
    except Exception as e:
        logger.debug(f"get_text(dict) failed on page {page.number + 1}: {e}")
        return []
    blocks_out: list[dict] = []
    for b in data.get("blocks", []):
        if b.get("type") != 0:  # 0 = text, 1 = image
            continue
        lines_structured: list[dict] = []
        lines_text_only: list[str] = []
        all_sizes: list[float] = []
        any_bold = False
        for line in b.get("lines", []):
            span_texts: list[str] = []
            span_sizes: list[float] = []
            span_bold = False
            for span in line.get("spans", []):
                txt = span.get("text", "")
                if txt.strip():
                    span_texts.append(txt)
                    span_sizes.append(float(span.get("size", 0)))
                    if int(span.get("flags", 0)) & 16:
                        span_bold = True
            if not span_texts:
                continue
            ln_text = normalize_text(" ".join(span_texts))
            if not ln_text:
                continue
            ln_bbox = line.get("bbox") or [0, 0, 0, 0]
            lines_structured.append({
                "text": ln_text,
                "bbox": [round(v, 2) for v in ln_bbox],
                "max_font_size": round(max(span_sizes), 2) if span_sizes else 0.0,
                "is_bold": span_bold,
            })
            lines_text_only.append(ln_text)
            all_sizes.extend(span_sizes)
            if span_bold:
                any_bold = True
        if not lines_structured:
            continue
        blocks_out.append({
            "bbox": [round(v, 2) for v in b.get("bbox", [0, 0, 0, 0])],
            "text": "\n".join(lines_text_only),
            "lines": lines_structured,
            "max_font_size": round(max(all_sizes), 2) if all_sizes else 0.0,
            "avg_font_size": round(sum(all_sizes) / len(all_sizes), 2) if all_sizes else 0.0,
            "is_bold": any_bold,
        })
    return blocks_out


# ----------------------------------------------------------------------
# استخراج وثيقة كاملة
# ----------------------------------------------------------------------

def _sha256_short(path: Path, nibbles: int = 16) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()[:nibbles]


def extract_pdf(pdf_path: Path, max_pages: int | None = None, with_blocks: bool = False) -> dict:
    logger.info(f"opening {pdf_path.name}")
    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    end = min(max_pages, total_pages) if max_pages else total_pages

    pages_out: list[dict] = []
    try:
        for i in range(end):
            page = doc[i]
            raw = page.get_text("text") or ""
            norm = normalize_text(raw)
            tables = extract_page_tables(page)
            page_dict: dict = {
                "page_number": i + 1,
                "text": norm,
                "char_count": len(norm),
                "tables": tables,
                "n_tables": len(tables),
            }
            if with_blocks:
                page_dict["blocks"] = extract_page_blocks(page)
            pages_out.append(page_dict)
            if (i + 1) % 25 == 0:
                logger.info(f"  processed {i + 1}/{end}")
    finally:
        doc.close()

    sha = _sha256_short(pdf_path)

    return {
        "meta": {
            "source_path": str(pdf_path).replace("\\", "/"),
            "source_name": pdf_path.name,
            "source_size_bytes": pdf_path.stat().st_size,
            "source_sha256_16": sha,
            "extracted_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "extractor": f"pymupdf {fitz.__version__}",
            "extractor_script": Path(__file__).name,
            "total_pages": total_pages,
            "pages_extracted": end,
            "with_blocks": with_blocks,
            "normalization": {
                "unicode_form": "NFC",
                "strip_tatweel": True,
                "strip_pua": True,
                "strip_zero_width": True,
                "collapse_whitespace": True,
                "lam_alef_swap_fix": True,
            },
        },
        "pages": pages_out,
    }


# ----------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------

def _safe_print(msg: str) -> None:
    try:
        print(msg)
    except Exception:
        sys.stdout.buffer.write((msg + "\n").encode("utf-8", errors="replace"))


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="PDF → JSON منظم (PyMuPDF)")
    p.add_argument("input", help="مسار ملف PDF")
    p.add_argument("-o", "--output", help="مسار JSON الناتج (افتراضي: <input>.extracted.json بجانب المصدر)")
    p.add_argument("--max-pages", type=int, default=None, help="حد أقصى للصفحات (للاختبار)")
    p.add_argument("--with-blocks", action="store_true", help="يُضمّن blocks مع font-size (لكشف العناوين)")
    p.add_argument("-v", "--verbose", action="store_true")
    args = p.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(levelname)s: %(message)s",
    )

    pdf_path = Path(args.input)
    if not pdf_path.exists():
        logger.error(f"file not found: {pdf_path}")
        return 1
    if pdf_path.suffix.lower() != ".pdf":
        logger.warning(f"not a .pdf extension: {pdf_path.suffix}")

    out_path = Path(args.output) if args.output else pdf_path.with_suffix(".extracted.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        data = extract_pdf(pdf_path, max_pages=args.max_pages, with_blocks=args.with_blocks)
    except Exception as e:
        logger.error(f"extraction failed: {e}")
        return 2

    out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    n_pages = len(data["pages"])
    n_tables = sum(p["n_tables"] for p in data["pages"])
    n_chars = sum(p["char_count"] for p in data["pages"])
    size_kb = out_path.stat().st_size // 1024
    _safe_print(f"[ok] pages={n_pages}  tables={n_tables}  chars={n_chars:,}  json={size_kb}KB")
    _safe_print(f"     {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
