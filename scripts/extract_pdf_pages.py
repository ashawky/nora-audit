"""extract_pdf_pages.py — استخراج صفحات PDF كنص أو صور (PyMuPDF).

أداة **تكميلية** بجانب `pdf_extract.py`:
- استعملها حين الـ text layer مكسور (Presentation Forms، glyph order معكوس،
  أو نص PDF مرفوض بقراءة ngram عربية) → اخرج صور PNG وحلّلها بنموذج visual.

Usage:
    # text → stdout (page = ===== PAGE N ===== block)
    python scripts/extract_pdf_pages.py <pdf> <pages>

    # text → file
    python scripts/extract_pdf_pages.py <pdf> <pages> --out FILE

    # images → directory of page-NNN.png
    python scripts/extract_pdf_pages.py <pdf> <pages> --mode images --out-dir DIR [--dpi 200]

Pages spec: 7 | 6-13 | 6-13,39-46 | all
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import fitz  # PyMuPDF

# Windows cp1252 → UTF-8 (مطلوب لأي طباعة عربية لاحقا)
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass


def parse_pages(spec: str, total: int) -> list[int]:
    if spec.strip().lower() == "all":
        return list(range(1, total + 1))
    out: list[int] = []
    for chunk in spec.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        if "-" in chunk:
            a, b = chunk.split("-", 1)
            out.extend(range(int(a), int(b) + 1))
        else:
            out.append(int(chunk))
    seen: set[int] = set()
    return [p for p in out if not (p in seen or seen.add(p))]


def extract_text(pdf_path: Path, pages: list[int]) -> str:
    doc = fitz.open(pdf_path)
    total = doc.page_count
    chunks: list[str] = []
    for p in pages:
        if not 1 <= p <= total:
            chunks.append(f"===== PAGE {p} (out of range; doc has {total}) =====\n")
            continue
        page = doc.load_page(p - 1)
        text = page.get_text("text")
        chunks.append(f"===== PAGE {p} =====\n{text.rstrip()}\n")
    doc.close()
    return "\n".join(chunks)


def render_images(pdf_path: Path, pages: list[int], out_dir: Path, dpi: int) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(pdf_path)
    total = doc.page_count
    written: list[Path] = []
    zoom = dpi / 72.0
    matrix = fitz.Matrix(zoom, zoom)
    for p in pages:
        if not 1 <= p <= total:
            print(f"skip page {p} (out of range; doc has {total})", file=sys.stderr)
            continue
        page = doc.load_page(p - 1)
        pix = page.get_pixmap(matrix=matrix, alpha=False)
        out_path = out_dir / f"page-{p:03d}.png"
        pix.save(out_path)
        written.append(out_path)
    doc.close()
    return written


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("pdf", type=Path)
    ap.add_argument("pages")
    ap.add_argument("--mode", choices=["text", "images"], default="text")
    ap.add_argument("--out", type=Path, default=None, help="text mode: write to file")
    ap.add_argument("--out-dir", type=Path, default=None, help="image mode: write PNGs here")
    ap.add_argument("--dpi", type=int, default=200, help="image mode resolution")
    args = ap.parse_args()

    if not args.pdf.is_file():
        print(f"error: pdf not found: {args.pdf}", file=sys.stderr)
        return 2

    doc = fitz.open(args.pdf)
    total = doc.page_count
    doc.close()
    pages = parse_pages(args.pages, total)
    if not pages:
        print("error: no pages selected", file=sys.stderr)
        return 2

    if args.mode == "text":
        text = extract_text(args.pdf, pages)
        if args.out:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(text, encoding="utf-8")
            print(f"wrote {len(text)} chars across {len(pages)} pages -> {args.out}", file=sys.stderr)
        else:
            print(text)
    else:  # images
        if args.out_dir is None:
            print("error: --out-dir required for image mode", file=sys.stderr)
            return 2
        written = render_images(args.pdf, pages, args.out_dir, args.dpi)
        for p in written:
            print(p)
        print(f"rendered {len(written)} pages @ {args.dpi}dpi -> {args.out_dir}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
