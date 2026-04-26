"""
nlm_verify.py — مُحقِّق NotebookLM لفهرس المخرجات.

subcommands:
  list                         # اسرد دفاتر NotebookLM في حسابك (بعد login)
  ask <notebook_id> "<سؤال>"   # أرسل سؤالا واحدا وأطبع الإجابة
  verify-docs <notebook_id>    # تحقّق من قائمة مخرجات DOC ضد deliverables-index.json
  verify-deps <notebook_id>    # طبقة (ج): يسأل NotebookLM عن اعتماديات كل مخرج (resumable)

متطلبات:
  pip install "notebooklm-py[browser]"
  playwright install chromium
  notebooklm login            # مرة واحدة — يفتح متصفح للدخول على جوجل

المخرجات:
  list        → stdout + JSON
  ask         → stdout + optional -o ملف
  verify-docs → agencies/_ensemble/nlm_docs_verify.json
  verify-deps → knowledge/dep_suggestions_c.json (تراكمي قابل للاستئناف)
"""

from __future__ import annotations

import argparse
import asyncio
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

from notebooklm import (
    NotebookLMClient,
    AskResult,
    Notebook,
    AuthError,
    NotebookNotFoundError,
    DEFAULT_STORAGE_PATH,
)


# ----------------------------------------------------------------------
# مساعدات
# ----------------------------------------------------------------------

def _auth_hint() -> str:
    return (
        "لم يتم العثور على اعتماد NotebookLM. نفّذ أولا:\n"
        "    notebooklm login\n"
        f"ملف الاعتماد المتوقع: {DEFAULT_STORAGE_PATH}"
    )


async def _client(timeout: float = 30.0):
    """سياق client موحّد — يُرجع استثناء واضحا إن لم يكن مسجّلا.
    timeout: ثوانٍ لـ HTTP requests (الافتراضي 30، نرفعه لأسئلة مركّبة).
    """
    if not Path(DEFAULT_STORAGE_PATH).exists():
        raise SystemExit(_auth_hint())
    return await NotebookLMClient.from_storage(timeout=timeout)


# ----------------------------------------------------------------------
# list — سرد الدفاتر
# ----------------------------------------------------------------------

async def cmd_list(args) -> int:
    async with await _client() as client:
        notebooks: list[Notebook] = await client.notebooks.list()
    if not notebooks:
        print("[!] لا توجد دفاتر في الحساب.")
        return 0

    print(f"عُثر على {len(notebooks)} دفتر(ا):\n")
    print(f"  {'#':>3}  {'sources':>7}  {'owner':>5}  id                                        title")
    print(f"  {'-'*3}  {'-'*7}  {'-'*5}  {'-'*40}  {'-'*40}")
    for i, nb in enumerate(notebooks, 1):
        owner = "✓" if nb.is_owner else " "
        print(f"  {i:>3}  {nb.sources_count:>7}  {owner:>5}  {nb.id:<40}  {nb.title[:60]}")

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(
            json.dumps(
                [
                    {
                        "id": nb.id,
                        "title": nb.title,
                        "sources_count": nb.sources_count,
                        "is_owner": nb.is_owner,
                        "created_at": nb.created_at.isoformat() if nb.created_at else None,
                    }
                    for nb in notebooks
                ],
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        print(f"\n[json] {args.output}")
    return 0


# ----------------------------------------------------------------------
# ask — سؤال واحد عام
# ----------------------------------------------------------------------

async def cmd_ask(args) -> int:
    async with await _client() as client:
        try:
            result: AskResult = await client.chat.ask(args.notebook_id, args.question)
        except NotebookNotFoundError:
            print(f"[error] notebook not found: {args.notebook_id}")
            return 2

    print("=" * 80)
    print("QUESTION:")
    print(args.question)
    print("=" * 80)
    print("ANSWER:")
    print(result.answer)
    print("=" * 80)
    print(f"references: {len(result.references)}")
    print(f"conversation_id: {result.conversation_id}")
    print(f"turn_number: {result.turn_number}")

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "notebook_id": args.notebook_id,
            "question": args.question,
            "answer": result.answer,
            "conversation_id": result.conversation_id,
            "turn_number": result.turn_number,
            "references": [
                {
                    "chunk_id": r.chunk_id,
                    "citation_number": r.citation_number,
                    "cited_text": r.cited_text,
                    "start_char": r.start_char,
                    "end_char": r.end_char,
                }
                for r in result.references
            ],
        }
        Path(args.output).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n[json] {args.output}")
    return 0


# ----------------------------------------------------------------------
# verify-docs — المقارنة الجوهرية: مخرجات DOC من فهرسنا ضد إجابة NotebookLM
# ----------------------------------------------------------------------

VERIFY_QUESTION_DOCS = (
    "من وثيقة 'مخرجات ممارسة البنية المؤسسية - مارس 2026'، "
    "أدرج **جميع** المخرجات المذكورة ضمن فئة «الوثائق» (القسم .02). "
    "أعطني القائمة بصيغة مرقمة، كل بند يحتوي على:\n"
    "1) اسم الوثيقة كما ورد حرفيا\n"
    "2) رقم الصفحة التي تظهر فيها\n"
    "3) جهة الاعتماد\n"
    "4) مستوى النضج المطلوب (رقم)\n\n"
    "مهم: لا تخلط بين فئة «الوثائق» و«التقارير» و«القرارات»."
)


def _load_our_docs() -> list[dict]:
    path = Path("extracted/primary-spec/deliverables-index.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    return [d for d in data["deliverables"] if d["category_id"] == "DOC"]


async def cmd_verify_docs(args) -> int:
    our_docs = _load_our_docs()
    print(f"[info] مخرجات DOC في فهرسنا: {len(our_docs)}")
    print("[info] إرسال السؤال إلى NotebookLM ...\n")

    async with await _client() as client:
        result: AskResult = await client.chat.ask(args.notebook_id, VERIFY_QUESTION_DOCS)

    print("=" * 80)
    print("NotebookLM ANSWER:")
    print("=" * 80)
    print(result.answer)
    print("=" * 80)
    print(f"\nreferences: {len(result.references)}")

    out = Path(args.output or "agencies/_ensemble/nlm_docs_verify.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "notebook_id": args.notebook_id,
        "question": VERIFY_QUESTION_DOCS,
        "nlm_answer": result.answer,
        "nlm_references_count": len(result.references),
        "nlm_references": [
            {
                "citation_number": r.citation_number,
                "cited_text": (r.cited_text or "")[:300],
                "chunk_id": r.chunk_id,
            }
            for r in result.references
        ],
        "our_docs": [
            {"id": d["id"], "name_ar": d["name_ar"], "phase": d["phase_abcdef"]}
            for d in our_docs
        ],
        "our_docs_count": len(our_docs),
        "status": "awaiting_human_cross_check",
        "next_step": (
            "اقرأ nlm_answer، ضع علامة ✅/❌/⚠️ على كل عنصر من our_docs، "
            "وأضف العناصر التي ذكرها NotebookLM ولم تظهر في فهرسنا (extra)."
        ),
    }
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n[saved] {out}")
    return 0


# ----------------------------------------------------------------------
# verify-deps — طبقة (ج): اعتماديات كل مخرج عبر NotebookLM (resumable)
# ----------------------------------------------------------------------

DEPS_QUESTIONS = {
    # literal: ما الذي ينص الدليل صراحة على اعتماديته؟ (محافظ)
    "literal": (
        "في وثيقة 'مخرجات ممارسة البنية المؤسسية - مارس 2026'، "
        "ما المخرجات الأخرى التي يعتمد عليها '{name_ar}'؟ "
        "اذكر أسماءها فقط، كل اسم في سطر، بدون شرح. "
        "إن لم يعتمد على غيره، اكتب: لا يعتمد على غيره."
    ),
    # inferential: ما الذي يحتاج المراجِع للرجوع إليه استدلاليا؟ (موسّع)
    "inferential": (
        "بافتراض أنك ستراجع وتقيّم المخرج '{name_ar}' المذكور في وثيقة "
        "'مخرجات ممارسة البنية المؤسسية - مارس 2026'، "
        "ما المخرجات الأخرى من نفس الوثيقة التي ستحتاج للرجوع إليها لإتمام التقييم بشكل صحيح؟ "
        "(فكّر في كل ما يقدّم سياقا، أو مرجعا، أو يُحتسب ضمنه، أو يجب اتساقه معه.) "
        "اذكر أسماء هذه المخرجات فقط، كل اسم في سطر مرقّم، بدون شرح."
    ),
}
DEPS_QUESTION_TEMPLATE = DEPS_QUESTIONS["literal"]  # backward compat

# بادئات تُحذف من اسم المخرج لتوليد phrase قابلة للمطابقة بإجابة NotebookLM
_DEP_NAME_PREFIXES = (
    "وثيقة", "وثائق", "تقرير", "التقرير", "قرار", "قرارات",
    "محاضر", "محضر", "إنجاز", "انجاز", "رقمنة",
    "عقود", "عقد", "قائمة", "سجل", "نماذج", "بطاقات",
    "اشتراطات", "ميثاق", "سياسة",
)

# كلمات شائعة جدا تُتجاهَل في حساب التداخل (تخفّف false positives)
_DEP_STOPWORDS = {
    "البنية", "المؤسسية", "البنية المؤسسية", "وثيقة", "تقرير", "قرار",
    "إلى", "على", "مع", "من", "في", "أو", "و", "هو", "هي", "ال",
}

# لاكتشاف citations [1] [2,3] في إجابة NotebookLM
_CITATION_RE = re.compile(r"\[\d+(?:[،,]\s*\d+)*\]")
# lam-alef fix (نفس النمط في pdf_extract.py)
_LAM_ALEF_FIX = re.compile(r"ا([\u0621-\u0626])ل")


def _strip_prefix(name: str) -> str:
    for pfx in _DEP_NAME_PREFIXES:
        if name.startswith(pfx + " "):
            return name[len(pfx) + 1:].strip()
    return name


def _match_names_in_text(text: str, items: list[dict]) -> list[dict]:
    """تطابق phrase-based: نقسم نص الإجابة لعبارات، ثم نختار للمخرج الذي يداخله أكثر.

    الخوارزمية:
    1. lam-alef normalize للنص.
    2. استخراج "phrases" (سطر = phrase، نزع citations [N]).
    3. لكل phrase: نختار المخرج الذي يشاركه أكبر عدد من الكلمات (بعد إزالة stopwords).
    4. شرط الاعتراف: ≥ 2 كلمات مشتركة (غير stopword)، أو phrase مطابق substring لجسم الاسم.
    """
    if not text:
        return []
    text_n = _LAM_ALEF_FIX.sub(r"ال\1", text)

    # phrases من النص
    phrases: list[str] = []
    for line in text_n.split("\n"):
        clean = _CITATION_RE.sub("", line)
        clean = clean.strip(" .,،;؛-•*#0123456789()\t").strip()
        if len(clean) >= 8:
            phrases.append(clean)

    # phrase candidates لكل مخرج
    item_bodies: list[tuple[dict, str, set[str]]] = []
    for it in items:
        nm = it.get("name_ar") or ""
        if len(nm) < 8:
            continue
        body = _strip_prefix(nm)
        body_words = {w for w in body.split() if w not in _DEP_STOPWORDS and len(w) >= 3}
        item_bodies.append((it, body, body_words))

    matches: list[dict] = []
    seen_ids: set[str] = set()
    for phrase in phrases:
        phrase_words = {w for w in phrase.split() if w not in _DEP_STOPWORDS and len(w) >= 3}
        if not phrase_words:
            continue

        best_item: dict | None = None
        best_score = 0
        best_match_kind = ""
        for it, body, body_words in item_bodies:
            # شرط 1: substring مباشر (الأقوى)
            if len(body) >= 8 and body in phrase:
                score = 100  # max
                if score > best_score:
                    best_item, best_score, best_match_kind = it, score, "substring"
                continue
            if len(phrase) >= 8 and phrase in body:
                score = 90
                if score > best_score:
                    best_item, best_score, best_match_kind = it, score, "substring_rev"
                continue
            # شرط 2: تداخل كلمات (≥ 2)
            common = phrase_words & body_words
            if len(common) >= 2:
                score = len(common)
                if score > best_score:
                    best_item, best_score, best_match_kind = it, score, f"words({len(common)})"

        if best_item and best_item["id"] not in seen_ids:
            matches.append({
                "id": best_item["id"],
                "matched": phrase[:80],
                "name_ar": best_item["name_ar"],
                "match_kind": best_match_kind,
            })
            seen_ids.add(best_item["id"])
    return matches


async def cmd_verify_deps(args) -> int:
    idx_path = Path("knowledge/deliverables-index.json")
    if not idx_path.exists():
        print(f"[error] {idx_path} not found")
        return 2
    items = json.loads(idx_path.read_text(encoding="utf-8"))["deliverables"]

    mode = getattr(args, "mode", "literal")
    if mode not in DEPS_QUESTIONS:
        print(f"[error] unknown mode: {mode}")
        return 2
    template = DEPS_QUESTIONS[mode]
    default_out = f"knowledge/dep_suggestions_c_{mode}.json" if mode != "literal" else "knowledge/dep_suggestions_c.json"
    out_path = Path(args.output or default_out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"[info] mode={mode}  output={out_path}")

    # تحميل الحالة السابقة (إن وُجدت) للاستئناف
    state: dict = {"meta": {}, "results": {}}
    if out_path.exists():
        try:
            state = json.loads(out_path.read_text(encoding="utf-8"))
            print(f"[info] resuming from {out_path} ({len(state.get('results', {}))} done)")
        except Exception:
            print(f"[warn] couldn't load existing {out_path}, starting fresh")

    state["meta"] = {
        "source_index": str(idx_path).replace("\\", "/"),
        "items_total": len(items),
        "notebook_id": args.notebook_id,
        "last_updated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    results = state.setdefault("results", {})

    # تحديد العناصر المتبقية (نتجاهل أي erroneous للسماح بإعادة المحاولة)
    already_ok = sum(1 for v in results.values() if "error" not in v)
    pending = [it for it in items if it["id"] not in results or "error" in results.get(it["id"], {})]
    if args.limit:
        pending = pending[: args.limit]
    print(f"[info] {already_ok} already OK, {len(pending)} pending (incl. retries)")

    # timeout أعلى لأن السؤال يتطلب بحثا في الوثيقة
    async with await _client(timeout=90.0) as client:
        for k, it in enumerate(pending, 1):
            iid = it["id"]
            question = template.format(name_ar=it["name_ar"])
            print(f"[{k}/{len(pending)}] {iid}: {it['name_ar'][:50]} ... ", end="", flush=True)
            answer = None
            err = None
            for attempt in (1, 2):  # محاولتان كحد أقصى
                try:
                    result: AskResult = await client.chat.ask(args.notebook_id, question)
                    answer = result.answer or ""
                    refs = len(result.references or [])
                    err = None
                    break
                except Exception as e:
                    err = e
                    if attempt == 1:
                        print(f"retry({type(e).__name__}) ", end="", flush=True)
                        await asyncio.sleep(2)
                    else:
                        break
            if answer is not None:
                matches = _match_names_in_text(answer, items)
                results[iid] = {
                    "name_ar": it["name_ar"],
                    "raw_answer": answer,
                    "matched_ids": [m["id"] for m in matches if m["id"] != iid],
                    "matched_details": [m for m in matches if m["id"] != iid],
                    "n_references": refs,
                }
                print(f"OK ({len(matches)} matches)")
            else:
                print(f"FAIL: {type(err).__name__}: {err}")
                results[iid] = {
                    "name_ar": it["name_ar"],
                    "error": str(err),
                }
            # حفظ بعد كل عنصر (resumability)
            state["meta"]["last_updated"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
            state["meta"]["completed"] = sum(1 for v in results.values() if "error" not in v)
            out_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n[done] saved → {out_path}")
    print(f"       total processed: {len(results)}/{len(items)}")
    return 0


# ----------------------------------------------------------------------
# reparse-deps — إعادة المطابقة على raw_answers محفوظة (لا استعلامات جديدة)
# ----------------------------------------------------------------------

def cmd_reparse_deps(args) -> int:
    inp = Path(args.input)
    idx_path = Path("knowledge/deliverables-index.json")
    if not inp.exists() or not idx_path.exists():
        print(f"[error] missing {inp} or {idx_path}")
        return 2
    state = json.loads(inp.read_text(encoding="utf-8"))
    items = json.loads(idx_path.read_text(encoding="utf-8"))["deliverables"]
    results = state.get("results", {})

    changed = 0
    nonzero = 0
    for iid, r in results.items():
        ans = r.get("raw_answer", "")
        if not ans:
            continue
        new_matches = _match_names_in_text(ans, items)
        new_ids = [m["id"] for m in new_matches if m["id"] != iid]
        if new_ids != r.get("matched_ids", []):
            changed += 1
        r["matched_ids"] = new_ids
        r["matched_details"] = [m for m in new_matches if m["id"] != iid]
        if new_ids:
            nonzero += 1

    state["meta"]["reparsed_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    state["meta"]["matcher_version"] = "v2_phrase_score_lamalef"
    inp.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[ok] reparsed {len(results)} items")
    print(f"     changed_matches : {changed}")
    print(f"     non-zero matches: {nonzero}/{len(results)}")
    return 0


# ----------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="NotebookLM verifier for NORA-Audit")
    sp = p.add_subparsers(dest="cmd", required=True)

    sp_list = sp.add_parser("list", help="اسرد الدفاتر")
    sp_list.add_argument("-o", "--output", help="JSON ناتج (اختياري)")

    sp_ask = sp.add_parser("ask", help="أرسل سؤالا واحدا")
    sp_ask.add_argument("notebook_id")
    sp_ask.add_argument("question")
    sp_ask.add_argument("-o", "--output")

    sp_v = sp.add_parser("verify-docs", help="قارن فئة DOC بإجابة NotebookLM")
    sp_v.add_argument("notebook_id")
    sp_v.add_argument("-o", "--output")

    sp_d = sp.add_parser("verify-deps", help="طبقة (ج): اعتماديات كل مخرج (resumable)")
    sp_d.add_argument("notebook_id")
    sp_d.add_argument("-o", "--output")
    sp_d.add_argument("--mode", choices=list(DEPS_QUESTIONS.keys()), default="literal",
                      help="literal=ما ينص الدليل صراحة | inferential=ما يحتاج للمراجعة استدلاليا")
    sp_d.add_argument("--limit", type=int, default=None,
                      help="حد أقصى للعناصر المعالَجة (للاختبار)")

    sp_rp = sp.add_parser("reparse-deps",
                          help="إعادة تطبيق المطابق على raw_answers بدون استعلامات جديدة")
    sp_rp.add_argument("--input", default="knowledge/dep_suggestions_c.json")

    return p


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.cmd == "list":
            return asyncio.run(cmd_list(args))
        elif args.cmd == "ask":
            return asyncio.run(cmd_ask(args))
        elif args.cmd == "verify-docs":
            return asyncio.run(cmd_verify_docs(args))
        elif args.cmd == "verify-deps":
            return asyncio.run(cmd_verify_deps(args))
        elif args.cmd == "reparse-deps":
            return cmd_reparse_deps(args)
    except AuthError as e:
        print(f"[auth error] {e}\n\n{_auth_hint()}")
        return 10
    except KeyboardInterrupt:
        return 130
    return 1


if __name__ == "__main__":
    sys.exit(main())
