---
name: tenant-learning-capture
description: Structured capture of insights from tenant (agency) work into a one-way candidate file for review-then-promote to core. Loads when working under agencies/<name>/ paths or when a pattern from tenant work looks like it could generalize back to core (knowledge/, scripts/, schemas).
---

# Tenant Learning Capture — One-way Knowledge Boundary

## When to load this skill

Load when **all** of:
- Current branch starts with `client/` (you're on a tenant branch).
- An insight, pattern, correction, or convention has emerged in the tenant work that **could generalize** beyond this tenant — e.g., a schema gap surfaced by real-world artifacts, a heuristic that worked, a convention worth standardizing.
- The user signals "this might be useful for core" / "we should add this back" / "interesting pattern."

**Do NOT load** when:
- On `main` — direct edits to core are the right path.
- The pattern is purely tenant-specific (engagement-internal, no core impact).
- The change is already covered by an existing DD or memory entry — point the user at it instead.

## What this skill encodes

The **one-way knowledge boundary** between tenant work and core. Per master plan §3.4 + §3.5:

- `client/<name>` branches **never merge back to main**.
- Tenant insights flow to `learnings-from-agencies/<agency>-<YYYY-MM-DD>/candidates.md`.
- A reviewer (Zidan) triggers `/promote-learning <id>` from `main` to apply the change after review.

This skill's job: convert a transient tenant observation into a **reviewable candidate** with enough structure for the reviewer to make a confident go/no-go decision.

---

## Step 1 — Allocate a candidate ID

Format: `<AGENCY-UPPER>-<YYYY-MM-DD>-<NN>` where NN is a 2-digit per-day sequence (01-padded).

To allocate NN:
1. Read `learnings-from-agencies/<agency>-<YYYY-MM-DD>/candidates.md` if it exists.
2. If absent → `NN=01`.
3. If present → scan for `id: ` lines, find the highest existing NN, set new NN = highest+1.

Example: `ETEC-2026-05-12-03` (third candidate captured on that date).

## Step 2 — Capture the 5 fields

Interview the user (or synthesize from immediate context) for these five fields. **Do not skip any.**

### 2.1 `context` — what happened
1–3 sentences. Concrete: cite the file path or task that surfaced this, plus the surprise/gap/insight.

> Bad: "noticed something useful"
> Good: "While drafting `agencies/etec/workspace/DOC-15-cycle-charter-general/v1/sec3.md`, the EA-Strategy v0.4 schema's `governance` container had no field for `committee_quorum_threshold` — but DGA's primary spec p.6 mentions a quorum requirement we had marked as out-of-scope."

### 2.2 `proposed_change` — what core should change
File paths + specific edits + DD-family if schema-related.

> Format: "Add field `<key>` to `<container>` in `knowledge/deliverables/<DEL>/fields.json`. Severity: <must/should/nice>. Source: <primary_spec p.X / guide / judgment>. Likely DD: extends DD-XX (or new DD-YY)."

### 2.3 `likely_impact` — blast radius
- Which existing schemas/scripts touched? (cite paths)
- Backwards-compat concerns? (existing meta blocks, downstream deps)
- Effort: **S** (<30 min) / **M** (30 min–2 h) / **L** (>2 h)

### 2.4 `confidence` — strength of signal
- **low** — speculative; observed once; may not generalize
- **medium** — observed twice OR once with strong rationale; likely useful
- **high** — strong signal across multiple touchpoints; consider promoting fast

### 2.5 `evidence_pointer` — where in tenant work
Path inside `agencies/<name>/` that triggered this. Read-only reference for the reviewer to verify context if needed. Do **not** quote tenant content here — just the path.

## Step 3 — Append to candidates.md

Output target: `learnings-from-agencies/<agency>-<YYYY-MM-DD>/candidates.md`

If the file or directory doesn't exist, create them. The file structure is markdown with one H2 header + one YAML code block per candidate, in capture order.

### Template (per candidate)

````markdown
## <CANDIDATE-ID>

```yaml
id: <CANDIDATE-ID>
captured_at: <ISO datetime>
agency: <agency-id>
branch: <current branch>
context: |
  <1–3 sentences>
proposed_change: |
  <file paths + specific edits + DD impact>
likely_impact: |
  <schemas/scripts + back-compat + effort S/M/L>
confidence: <low|medium|high>
evidence_pointer: agencies/<name>/<path>
promoted_at: null
promoted_commit: null
```
````

> **Why YAML-in-markdown?** Markdown headers make the file skimmable for the reviewer. The fenced YAML block is machine-parseable for `/promote-learning` to extract structured fields. The `null` sentinels on `promoted_at` / `promoted_commit` give `/promote-learning` clean placeholders to fill.

## Step 4 — Tell the user

After the YAML block is appended, tell the user **exactly**:

> "Captured as `<CANDIDATE-ID>`. Run `/promote-learning <CANDIDATE-ID>` from `main` when ready to review and apply. The candidate file is at `learnings-from-agencies/<agency>-<YYYY-MM-DD>/candidates.md`."

Do not switch branches or promote on the user's behalf — the boundary is one-way and reviewer-gated.

---

## Edge cases

- **Candidate already exists with same essence.** Search existing `candidates.md` for similar `proposed_change` text. If found → tell the user, point them at the existing ID instead of creating a duplicate.
- **Tenant data leak risk in `proposed_change`.** Never paste tenant-specific text (names, internal numbers) into `proposed_change` — abstract to the pattern. Real tenant data stays in `agencies/<name>/`.
- **High-confidence + small effort.** If confidence=high AND effort=S, suggest the user run `/promote-learning` immediately after returning to main. Otherwise treat candidates as queued.
- **Multi-file proposed_change.** Itemize per file; the `/promote-learning` command will gate per-file in Step 4.

## Anti-patterns (do not do these)

- ❌ Editing `knowledge/`, `scripts/`, `extracted/`, or `DGA-Resources/` directly from a `client/*` branch — the PreToolUse boundary hook will block it.
- ❌ Switching to `main` from within a `client/*` session to "just apply the fix." The reviewer gate exists for a reason — even small changes deserve a moment of fresh-eyes review.
- ❌ Bundling 5+ candidates in one capture. One candidate = one focused change. Batch promotions happen at the reviewer's discretion, not at capture time.
- ❌ Putting tenant-internal identifiers in `context` or `proposed_change`. If the reviewer needs to verify, they read `evidence_pointer`.
