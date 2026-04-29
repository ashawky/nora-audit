---
description: End-of-sprint memory update — adds DONE section, updates next sprint, audits §10 promotions
argument-hint: <sprint-name>  e.g. S2.4
---

# End-of-Sprint Memory Update

User has completed sprint **$ARGUMENTS** and wants the auto-memory `status_phase_progress.md` updated.

## Step 1 — Read the memory file

Path pattern (auto-memory):
`~/.claude/projects/<sanitized-CWD>/memory/status_phase_progress.md`

For NORA-Audit specifically:
`C:\Users\USER\.claude\projects\C--Users-USER-Documents-Claude-Projects-NORA-Audit\memory\status_phase_progress.md`

If the file doesn't exist or is empty, ask the user before proceeding (likely a path mismatch or wrong project).

## Step 2 — Audit what changed in this sprint

Run in parallel:
- `git log --oneline -10` — filter for `($ARGUMENTS)` suffix in commit messages
- `git diff --stat HEAD~5..HEAD` — file-level changes
- `git status` — uncommitted state

If working tree is dirty, **stop** and ask if the sprint is actually done.

## Step 3 — Compose the new section

Format every `## Phase 1 / $ARGUMENTS — DONE ✅ (YYYY-MM-DD)` section MUST follow:

```
## Phase 1 / <sprint> — DONE ✅ (YYYY-MM-DD)

**Process used:** <brief narrative — gates, scope, mid-sprint revisions>

**Artifacts:**
- `<path>` — <bumped version, line counts, key metrics>

**Locked-in conventions** (project-wide):
- <bullet> (omit if none emerged)

**Commits on origin/main:**
- `<hash>` <commit subject>
```

## Step 4 — Update date header

The first content line is `**As of YYYY-MM-DD (end of <sprint> session):**`. Update both date and sprint label.

## Step 5 — Lessons (only if non-obvious)

Under `## Lessons from $ARGUMENTS`, list only insights that:
- Aren't derivable from code/git history
- Generalize beyond this sprint
- Either failure-recovery insights OR validated approaches

Format: numbered list, lead with the rule, then *why* and *when* to apply.

## Step 6 — Update "Next sprint" section

Propose 2-3 options (depth / breadth / parallel-deliverable). For each: one-sentence scope + effort estimate (small/medium/large) + why-now. Mark a recommendation; user may override.

## Step 7 — CLAUDE.md §10 audit (BLOCKING — do not skip)

For every recurring activity in this sprint, ask: **"Did I do something I might do again?"** If yes, classify:

| Pattern type | Promote to |
|---|---|
| Recurring CLI sequence | `scripts/<name>.{sh,py}` |
| Recurring reasoning workflow | `.claude/skills/<name>/SKILL.md` |
| Recurring prompt | `.claude/commands/<name>.md` |
| Recurring isolated investigation | `.claude/agents/<name>.md` |
| Recurring deterministic action | Hook in `.claude/settings.json` |
| Recurring external action | n8n workflow |

For each candidate: estimate effort. If effort < 15min, **scaffold immediately** (per §10's "ship the file"). If effort > 15min, add to follow-ups with effort + ROI note.

## Step 8 — Update "Open follow-ups"

Three actions:
1. Add follow-ups discovered this sprint
2. Mark resolved follow-ups (if any) — move to "Primitives promoted" log if they led to a primitive
3. Add §10 audit findings from Step 7

## Step 9 — Show diff preview, save on approval

Show the user what will change (new section + updated next-sprint + new follow-ups). On approval, use Edit (targeted) — never Write blindly. The file is precious audit trail.

## Step 10 — Commit hash placeholder

If sprint commit not yet made, use `<<sprint> commit hash>` placeholder. Add a follow-up: "Update commit hash in status memory after commit lands."

## Format Conventions (binding)

- snake_case English keys + `name_ar` siblings — preserve when quoting from schemas
- Versioned blocks (`design_decisions_v<X>`, `out_of_scope_v<X>`) accumulate; never delete prior
- Convert relative dates to absolute ISO (YYYY-MM-DD)
- Reference design decisions by ID (DD-X) when invoking
- Bilingual: structural language English, Arabic content verbatim

## Edge Cases

- **No commits this sprint:** ask if sprint is complete or commits are pending
- **Mid-sprint DD reversal:** call out with `revises: DD-<N>` linkage
- **Lessons warrant promotion (§10):** flag in follow-ups; scaffold inline if effort < 15min
- **Sprint name unclear:** ask the user — don't guess
