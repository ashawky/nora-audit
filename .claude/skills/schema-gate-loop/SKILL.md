---
name: schema-gate-loop
description: Container-by-container gate workflow for designing or extending a NORA-Audit deliverable schema (fields.json). Battle-tested across S2.2 (v0.2) and S2.3 (v0.3). Loads when the user starts a new deliverable schema sprint or a major schema iteration on an existing one.
---

# Schema Gate Loop — Sprint Workflow

## When to load this skill

- A sprint begins to design a fresh deliverable schema (e.g., `DEL-DOC-005`, `DEL-DOC-016`).
- A sprint extends an existing deliverable schema with a major iteration (e.g., adding sub-container weights, evidence_requirements).
- The user invokes a sprint name like `S2.X` and the focus is on `knowledge/deliverables/<NAME>/fields.json`.

If the work is a tiny localized fix or a one-off field rename, **do not** load this skill — direct edits are cheaper.

## What this skill encodes

The repeatable, gate-driven workflow that produced EA-Strategy v0.2 and v0.3. Each step has a user gate; never chain ahead silently.

---

## Step 0 — Sprint scoping (Gate 0: schema shape)

Before opening `fields.json`:

1. State the sprint goal in one sentence (e.g., "v0.3 = add field-level severity tags + container weights summing to 100").
2. Propose the **shape** of the change:
   - Which top-level containers are touched?
   - What new structures (e.g., `validation` block schema) are introduced?
   - Are any containers split, merged, removed?
3. List **out_of_scope_v0_X** explicitly — what is intentionally deferred (e.g., evidence_requirements, dependency edges, scorer impl).
4. Show this proposal as a brief markdown table or bullet list. **Wait for user approval (Gate 0)** before any per-container work.

> **Rule:** Gate 0 is non-skippable. Schema-shape errors caught at Gate 0 cost minutes; caught after 8 container gates they cost the whole sprint.

---

## Step 1 — Per-container gates

For each top-level container, in order:

1. Quote the relevant primary-spec / guide passages (verbatim Arabic, with `source_ref: {file, page, section}`).
2. Propose the container's contribution:
   - Field/sub-container additions or modifications (in JSON snippet form).
   - Severity tagging (`must` / `should` / `nice`) with `severity_source` (`primary_spec` / `guide` / `judgment`) and `rationale_ar`.
   - For v0.3+: container weight (integer; weights must sum to exactly 100 across the schema).
3. Pose 1–2 **decision questions** if the container has non-obvious choices (e.g., "this field could live in container X or Y — which?").
4. **Wait for user approval before moving to the next container.**
5. Capture the decision rationale as a `DD-N` entry — to be added to `design_decisions_v0_X` during Step 4.

> **Container ordering matters.** Use the same order as the existing schema or primary-spec when possible. Don't reorder containers mid-sprint without an explicit DD.

---

## Step 2 — Mid-sprint DD reversal (when it happens)

If the user revisits an earlier sprint's decision with fresh eyes (re-reads source text, refines understanding), **do not silently override**:

1. Identify the prior decision (e.g., DD-12 from v0.2).
2. Add a **new** DD in the current version block (e.g., DD-29 in v0.3) with:
   - `topic`: short description
   - `decision`: what changes now
   - `revises`: <prior DD id>
   - `user_quote_ar`: verbatim user reasoning if expressed
   - `migration_target`: where the removed/relocated item goes (if applicable)
3. Add `v0_X_revision_note` inline on the prior DD pointing forward to the new one.
4. **Never delete prior DDs.** They are audit-trail. Reversal is additive.

> Reference: DD-12 → DD-29 in EA-Strategy v0.3. Both visible in `fields.json`; status memory documents the journey.

---

## Step 3 — Foundational vs per-container DDs

- **Foundational DDs** (cross-cutting, project-wide convention) — declare during the **finalization** step, not per gate. Examples: DD-16 (severity semantics), DD-17 (weight scale), DD-18 (deprecate optional_per_guide).
- **Per-container DDs** — declare during the relevant gate. Examples: DD-19 (language=should), DD-20 (success_factors asymmetric severity).
- This separation keeps gate proposals focused on the container at hand instead of getting tangled in framework-level debates.

---

## Step 4 — Integration

After all container gates close:

1. Compile the final `fields.json` with:
   - All container changes integrated.
   - `out_of_scope_v0_X` array.
   - `design_decisions_v0_X` block with foundational DDs first, then per-container DDs.
   - Bumped `schema_version` and `scaffold_status` (e.g., `v0.3_pending_review`).
2. **Use `Write` for dense format expansions** (e.g., adding 100+ validation blocks across all leaves). `Edit` chains break on duplicate boilerplate (`old_string not unique`). For localized changes (single container, small delta), `Edit` is still preferred.
3. Record any `revises:` linkages and `v_X_revision_note` annotations on prior DDs.

---

## Step 5 — Verification

Run `python scripts/verify_schema.py <fields.json>`. Report PASS/FAIL explicitly. The script checks:

- Top-level required keys present
- Container weights sum to 100
- `governance` is a top-level container (DD-3)
- No deprecated `optional_per_guide` (DD-18)
- DD ids unique across versions, format `DD-N`
- Validation block severity/source distribution

If FAIL, fix root cause (don't suppress). Compare counts against status memory expectations.

---

## Step 6 — Close the sprint

Run `/end-sprint <S2.X>`. The slash command handles:

- DONE section in status memory
- Lessons (only non-obvious)
- Next sprint options (depth / breadth / parallel deliverable)
- §10 audit (Step 7 of /end-sprint — binding)
- Open follow-ups update

---

## Lessons baked in (carry forward)

1. **Subagent shallow-pass risk.** When delegating deep-read of guides to an Explore subagent, specify minimum candidate count, paste 2–3 examples of what to capture, and tag confidence levels per candidate. S2.2 first pass returned 4 candidates from 76 pages (~5%). Second pass with stricter prompt returned 14. Don't trust a single subagent pass.

2. **Process vs document content distinction.** Guides mix "how to create the document" with "what the document should contain." Reject anything that is a workflow step rather than a deliverable artifact (5 candidates rejected on this basis in v0.2).

3. **Primary-spec-only-must-floor heuristic.** Only fields the regulator can cite from primary-spec p.6 carry `severity=must`. Guide-only items max out at `should/nice`. This emerged organically across DD-20/22/24/26 in v0.3 — apply to any new deliverable schema.

4. **Conditional-must pattern (DD-21).** When a parent is optional but children are inseparable (e.g., SWOT 4 quadrants under `swot_analysis=nice`), leaves inherit the parent severity tag. Capture "if-conducted-then-required" semantics in a `conditional_note_ar` narrative; defer hard logic to the scorer (S4).

5. **Derivability principle (DD-27).** When a leaf is fully determined by another via deterministic mapping (e.g., `domain_name_ar` from `domain` enum + value_map), tag as `nice`. Recording is human-readability convenience, not information-bearing.

6. **Judgment-can-rise-to-must (DD-28).** Rare but valid: judgment-source can support `must` when absence makes the parent meaningless (precedent: `governance.approval_status`). Use sparingly; defaults remain primary_spec-anchored.

7. **JSON full-rewrite > Edit-chain when changes are dense.** When a single sprint adds 100+ validation blocks, a single `Write` call produces cleaner diffs than 100+ `Edit` calls and avoids the "old_string not unique" trap. CLAUDE.md §4 ("never rewrite a full file for a localized change") still applies to localized edits — this lesson covers non-localized format expansions only.

---

## Anti-patterns (do not do these)

- **Don't skip Gate 0.** Skipping schema-shape approval and going straight to container 1 has burned sprints when a structural assumption was wrong.
- **Don't delete prior DDs when reversing.** Revisions are additive (new DD with `revises:`). Audit trail must survive sprint changes.
- **Don't merge multiple containers into one mega-gate.** Per-container gates were 6 in S2.2 and 8 in S2.3 — the cadence is part of why focus stays sharp.
- **Don't promote a guide-only field to `must` to "be safe".** Over-claiming severity hurts more than under-claiming because it makes the audit fail noisily on optional content.
- **Don't run `/end-sprint` without first running `verify_schema.py`.** Sprint isn't done until the schema parses cleanly.
