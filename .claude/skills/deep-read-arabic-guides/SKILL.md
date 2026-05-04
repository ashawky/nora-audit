---
name: deep-read-arabic-guides
description: Two-pass deep-read pattern for harvesting candidate fields from Arabic regulatory guides (DGA practice-establishment + national-methodology) into a deliverable-schema candidates file. Battle-tested in S2.2 (EA-Strategy v0.2; pass-1 yielded 4 candidates, pass-2 yielded 14 after stricter prompt) and S2.4 (v0.4 sub-weights, structure-map sibling). Loads when a sprint extracts content from `extracted/guides/*.json` to seed or extend a `knowledge/deliverables/<NAME>/fields.json`.
---

# Deep-Read Arabic Guides — Two-Pass Subagent Workflow

## When to load this skill

- A sprint begins or extends a deliverable schema and the **depth source is one or more Arabic guides** under `extracted/guides/*.json` (e.g., `practice-establishment`, `national-methodology-v1`).
- The sprint will produce a `knowledge/deliverables/<NAME>/v<X>_candidates.json` audit artifact + later promote some candidates into `fields.json` via the `schema-gate-loop` skill.
- Typical sprint codes: **S2.2** (EA-Strategy v0.2 — original); **M3.1 onward** (DOC-15/16/17 schemas); future depth iterations on existing schemas where guide content is the source.

If the sprint operates only on primary-spec content (no guide depth) → **do not** load this skill; direct primary-spec parsing is cheaper. If the sprint is a tiny field rename or DD-only edit → **do not** load; `schema-gate-loop` alone suffices.

## What this skill encodes

The repeatable two-pass workflow that produced EA-Strategy v0.2's 14 candidates **after** a failed first pass that returned only 4 (the canonical "shallow-pass" failure mode). It captures the prompt elements, output structure, and gate language that survived sprint S2.3's audit — including the DD-29 reversal, where a first-pass high-confidence candidate (`governance_focus_axes`) was overturned at v0.3 reread.

**The lesson is not "trust the deep-read"; the lesson is "structure the deep-read so reread is cheap and reversal is non-catastrophic."**

Battle-tested precedent:
- `414aac4` — S2.2 v0.2 (original two-pass deep-read; pass-1 = 4, pass-2 = 14)
- `153c602` — S2.3 v0.3 (DD-29 reversal of `governance_focus_axes`; primary-spec floor formalized as DD-16)
- `014ee65` — S2.4 v0.4 (schema-gate-loop Step 0a structure-map = sibling pattern: same subagent-as-compressor philosophy applied to existing fields.json instead of guides)

---

## Step 0 — Sprint prep: pre-deep-read scoping

Before launching any subagent:

1. **Anchor to primary spec first.** Open `extracted/primary-spec/primary-spec.extracted.json` and locate the deliverable's row in the `.02 الوثائق` table (or the appropriate category section). Extract: page number, content mandate (the bullet list defining what the document must contain), approval authority. **This is the must-floor.** Only fields traceable to these bullets will carry `severity=must` in the eventual `fields.json`. State this rule in the deep-read subagent prompt.
2. **Identify guide chapter range.** From the relevant `extracted/guides/<guide>.extracted.json` (or `extracted/guides/<deliverable>-chapter-map.json` if one was prepared via S2.1-style mechanical extraction), determine which page ranges discuss the deliverable. Chapter-map artifact is preferred when available; cold guide scan is acceptable for greenfield deliverables.
3. **Container hypothesis.** Based on primary-spec mandate + chapter-range scan, hypothesize **6–10 candidate top-level containers** for the eventual `fields.json`. This is a scoping seed for Pass 1's container assignment, not a final commitment.
4. **State the deep-read scope explicitly.** Examples — from S2.2 EA-Strategy: "P1+P2 read, ~76 pages of practice-establishment + national-methodology, target candidates for the 7 v0.1 containers." For greenfield: "all guide pages X–Y discussing DEL-DOC-NNN, harvest into hypothesized containers from step 3."

> **Rule:** If primary spec is silent on the deliverable (rare), every candidate caps at `severity=should` or `nice`. Document this constraint in `design_decisions_v0_X` as a foundational decision.

---

## Step 1 — Pass 1 (Explore subagent, baseline harvest)

Launch **one Explore subagent** (read-only, faster than the general Agent for content extraction). Its prompt **must include all six** of the following elements — omitting any one risks the shallow-pass failure mode:

| Element | Why it matters |
|---|---|
| Target candidate count (e.g., "≥10 candidates") | Without a count, the subagent under-harvests. S2.2 pass-1 had no count → returned 4. |
| 2–3 worked examples with full output structure (Arabic quote + section + container + confidence) | Models the output format. Free-form descriptions get free-form returns. |
| Container-hypothesis list from Step 0 | Forces scoping per candidate. Orphan candidates are useless at gate time. |
| Confidence requirement: every candidate tagged `high\|medium\|low` | No untagged candidates. Untagged = unreviewable at user gate. |
| Primary-spec floor rule stated upfront | Subagent learns the must-vs-should boundary. Prevents inflated `must` claims. |
| Output schema for each candidate (see Step 4) | Pass 1's output format must match the final `v<X>_candidates.json` format exactly. |

**Subagent type:** `Explore`. **Depth:** `very thorough` for greenfield new-deliverable reads; `medium` for extension sprints with a chapter-map already prepared.

---

## Step 2 — User-gate review (count + quality check)

After Pass 1 returns:

1. **Count candidates.** If `<70%` of the target count, plan a Pass 2 with stricter prompt (Step 3 binding). If `≥70%`, sample 3 candidates for quality (verbatim quote present? section ref accurate? container assignment plausible?). If quality fails, also Pass 2.
2. **Surface to user.** Present the candidate list as a compact table — one row per candidate: `id | container | confidence | one-line rationale`. **Wait for user feedback** on:
   - Specific candidates the user thinks are wrong (rejected at gate-time)
   - Specific patterns the user thinks are missed (e.g., "the guide section on RACI matrices wasn't harvested" → feeds Pass 2 concrete-miss examples)
3. **User Gate 2:** decide Pass 2 (yes/no) + scope of Pass 2 prompt refinements.

> **Rule:** Never skip Step 2. The subagent does not know the user's mental model of "what should be there"; only the user does. S2.2's pass-1 → pass-2 jump (4 → 14) came **entirely** from user-supplied miss examples added to the pass-2 prompt.

---

## Step 3 — Pass 2 (Explore subagent, refined prompt)

If Step 2 triggered Pass 2, launch a new Explore subagent with the Pass 1 prompt **plus**:

- **Concrete miss examples from user feedback** — 3+ specific patterns the previous pass missed, verbatim phrasing where possible.
- **Tightened candidate count** — set the target at 90%+ of expected total. S2.2: pass-2 target was 14, achieved 14 + 5 out-of-scope flags.
- **Out-of-scope flagging requirement:** if a candidate clearly belongs to another deliverable, return it tagged `out_of_scope_target: DEL-XXX-NNN` instead of dropping it silently.
- **Quote-only-from-source rule:** "if you cannot quote it verbatim from the guide page, do not include it as a candidate."

Pass 2 is not optional retroactively. Once user gate 2 calls for it, run it. Do not paper over Pass 1 gaps with manual additions in Step 4 — that destroys the audit trail.

---

## Step 4 — Candidate audit artifact

Write `knowledge/deliverables/<NAME>/v<X>_candidates.json` with one entry per candidate. **Format is binding:**

```json
{
  "candidate_id": "<container_key>-<seq>",
  "field_name_ar": "<Arabic name as proposed>",
  "field_key": "<snake_case English key>",
  "evidence_quote_ar": "<verbatim Arabic passage from guide>",
  "source": {
    "file": "extracted/guides/<guide>.extracted.json",
    "page": 47,
    "section": "5.1.2.3"
  },
  "container_key": "<target container in fields.json>",
  "confidence": "high|medium|low",
  "type_hints": "object | leaf | list_of_objects | nested_items",
  "notes": "<free-form: why this, what it fixes, ambiguities, out_of_scope_target if relevant>"
}
```

Rejected candidates from gate-time review **stay in the file** with `"status": "rejected"` + `"rejection_rationale"`. Do not delete rejections — they are the audit trail (mirrors S2.2's 5 rejections preserved as DD-12 and later cited in the DD-29 reversal narrative).

This file ships with the sprint commit alongside the updated `fields.json`.

---

## Step 5 — Promotion to fields.json (handoff to schema-gate-loop)

Once `v<X>_candidates.json` is approved:

1. Hand off to the `schema-gate-loop` skill (load it now if not already loaded).
2. At each per-container gate, design new fields **only** from accepted candidates for that container. Do not introduce fields without a candidate row backing them.
3. Each promoted field gets a `validation` block (per v0.3 conventions) where `source_quote_ar` and `source_ref` come **directly** from the candidate row.
4. Track the candidate-to-field mapping in `design_decisions_v0_X` (e.g., `DD-N: "promoted candidates identity-001..003 to fields identity.{a,b,c}; rejected identity-004 — see candidates.json rejection_rationale"`).

Step 5 is the bridge — it moves rigor from "we found these candidates" to "we committed to these fields with full provenance."

---

## Lessons baked in (carry forward)

1. **Two-pass mandatory.** Single-pass subagent output is never trusted for a complete deep-read. S2.2 pass-1 = 4 candidates (5% yield); pass-2 = 14. The first pass is a calibration probe, not a deliverable.
2. **Pass-2 prompt is engineered, not freeform.** Min count + concrete miss examples + container scoping + confidence tagging + primary-spec floor rule + out-of-scope flagging — all six. Drop one and yield drops.
3. **Candidate output structure is binding.** The format in Step 4 is not a suggestion — it's the contract that lets gate-time review be cheap. Free-form candidate text destroys reviewability.
4. **Primary-spec floor rule.** `severity=must` only for primary-spec-traceable fields (DD-16, DD-17, DD-28). Guide-only candidates cap at `should/nice`. State this in the deep-read prompt upfront — emerged organically in S2.3 and is mandatory from M3 onward.
5. **Reread before promoting first-pass high-confidence.** S2.2 promoted `governance_focus_axes` from a guide p.33 first-pass high-confidence; S2.3 reread the same passage and reversed it (DD-29). High confidence ≠ verified; gate-time reread is a non-skippable safety net.
6. **Subagent over direct Read.** Guides are 100–313 pages of Arabic text. Loading them into main context bloats the rest of the sprint. The Explore subagent returns a structured candidate list; main context stays clean for gate decisions. (Same philosophy as `schema-gate-loop` Step 0a's structure-map sibling — `014ee65`.)
7. **Out-of-scope flagging, not silent rejection.** When a candidate clearly belongs to another deliverable (e.g., DOC-15's deep-read finds DOC-16 content), tag `out_of_scope_target: DEL-XXX-NNN` and preserve. Silent drop loses the audit trail; explicit flag feeds the next sprint's input.

---

## Anti-patterns (do not do these)

1. **Inferring fields beyond verbatim guide content.** If the guide does not state it, do not harvest it. Fields with no `evidence_quote_ar` have no provenance and cannot be defended at audit.
2. **Harvesting process/workflow steps as deliverable fields.** Guides mix "how to create the document" (process) with "what the document contains" (artifact). Reject step-like candidates (e.g., "conduct a SWOT analysis" is a process, not a content field). S2.2 rejected 5 candidates on this basis.
3. **Conflating governance content with the host deliverable's scope.** S2.2 → S2.3 governance reversal (DD-29) was the lesson; do not repeat it. If a candidate sounds governance-flavored and the host deliverable is a content document (e.g., DOC-15 charter ≠ DOC-08 governance committee charter), suspect it and force a reread before promoting.
4. **Skipping the primary-spec anchor.** The must-floor is set there. A deep-read without primary-spec context cannot assign severity correctly and produces unanchored fields.
5. **Single-pass subagent trust.** Two passes always — or one pass + explicit user acceptance of pass-1 sufficiency, but never silent acceptance.
