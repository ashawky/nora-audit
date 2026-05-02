---
description: Review a tenant-derived learning candidate and promote it to core (one-way: client → main, reviewer-gated)
argument-hint: <candidate-id>  e.g. ETEC-2026-05-01-01
---

# Promote Tenant Learning to Core

User wants to review and apply candidate **$ARGUMENTS** from `learnings-from-agencies/`.

This command formalizes the one-way knowledge boundary defined in master plan §3.4–§3.5: tenant insights flow to core only via reviewed promotion, never silent merge.

## Step 1 — Verify on `main`

Run `git rev-parse --abbrev-ref HEAD`.

- If output is `main` → proceed.
- If output starts with `client/` → **abort**. Tell the user:
  > "Promotion runs from `main` only. Currently on `<branch>`. Switch to main first (`git checkout main`), pull latest, then re-run `/promote-learning $ARGUMENTS`."
- If detached HEAD or other → ask the user how to proceed; don't guess.

If working tree is dirty, **stop** and ask whether to stash or commit first. Promotion produces a clean single-purpose commit; mixed state pollutes the audit trail.

## Step 2 — Locate the candidate

Search across `learnings-from-agencies/*/candidates.md` for `id: $ARGUMENTS` (use Grep). Three outcomes:

- **Single match** → proceed to Step 3 with that file path.
- **No match** → ask the user to verify the ID. Do not proceed.
- **Multiple matches** (rare — same ID in different agency-date dirs) → list them with their file paths and ask the user to disambiguate.

## Step 3 — Present candidate + get approval

Read the candidate's YAML block. Show the user:

```
Candidate $ARGUMENTS  (from <agency-id>, <YYYY-MM-DD>)

Context:          <wrapped>
Proposed change:  <wrapped>
Likely impact:    <wrapped>
Confidence:       <low|medium|high>
Evidence pointer: <agencies/<name>/<path>>  (read-only ref; not opened automatically)

Status: <not-yet-promoted | already-promoted-at-YYYY-MM-DD>
```

If `promoted_at` is non-null → **abort**. Tell the user:
> "Candidate $ARGUMENTS was already promoted on `<promoted_at>` in commit `<promoted_commit>`. Re-promotion not supported. If you intend to extend the change, capture a new candidate."

Otherwise, ask exactly:
> "Apply this change to core? (yes / no / modify)"

- `no` → exit without changes.
- `modify` → ask what to adjust; revise the proposed change in conversation; re-show; re-ask.
- `yes` → proceed to Step 4.

## Step 4 — Apply the change to core

Implement `proposed_change` via **surgical edits** (CLAUDE.md §4 — no full-file rewrites). For each file mentioned:

1. Read the file to confirm the target location exists.
2. If the file does not exist → stop and ask the user. The candidate may be stale; do not create new files unprompted.
3. Apply the edit using `Edit` (preferred) or `Write` (only for new files explicitly requested in the candidate).
4. If the candidate touches a `fields.json` → after the edit, run `python scripts/verify_schema.py <path>` and report PASS/FAIL. On FAIL, stop and ask the user.

If multiple files → confirm each before editing.

## Step 5 — Mark candidate as promoted (placeholder hash)

Edit the candidate's YAML block in `candidates.md`:

```yaml
promoted_at: <today ISO date YYYY-MM-DD>
promoted_commit: <pending>
```

Use `Edit`, not `Write` — preserve all other candidates in the file. Match exactly on the `promoted_at: null` and `promoted_commit: null` lines (each block has its own pair, so include the surrounding `id: $ARGUMENTS` context to keep the match unique).

## Step 6 — Commit on `main`

Stage the touched core file(s) **and** the modified `candidates.md`. Commit message format:

```
feat(core): promote $ARGUMENTS from <agency-id> learnings

<one-paragraph summary of the change — what was added/modified/removed>

Source: agencies/<name>/<path> (evidence pointer)
Confidence: <level>
```

Per repo convention, end the commit body with:
`Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>`

Use a HEREDOC for the commit message to preserve formatting.

## Step 7 — Backfill commit hash

After the commit lands:

1. Get the new commit hash: `git rev-parse --short HEAD`.
2. Edit the `candidates.md`: `promoted_commit: <pending>` → `promoted_commit: <hash>`.
3. Commit again with message: `chore(learnings): backfill promoted_commit for $ARGUMENTS`.

This produces a clean two-commit sequence: the substantive change first, then the audit-trail backfill. **Do not** use `--amend` — per CLAUDE.md "create new commits rather than amending."

## Step 8 — Final report

Show the user:
- Files changed (list with line counts)
- Two commit hashes (substantive + backfill)
- Any verification output (e.g., `verify_schema.py` PASS)
- Suggested next step (e.g., update `status_phase_progress.md` if this is a sprint-level promotion, or just ack)

---

## Edge cases

- **Candidate references a file or container that no longer exists on main.** Stop. The candidate may be stale, or the proposed change may need re-scoping. Ask the user.
- **`proposed_change` is too vague to act on.** Stop and ask the user for specifics. Do not invent edits.
- **Candidate confidence is `low`.** Warn the user: "Confidence is low — proceed only if you've validated this independently. Continue?" Do not auto-proceed.
- **Sensitive file (e.g., `knowledge/deliverables/<DEL>/fields.json`).** Run `verify_schema.py` after edit (Step 4). If verify fails, ROLLBACK the edit before committing — do not commit a broken schema.
- **Hook blocks the edit.** Should not happen on `main`, but if it does, stop and ask the user — likely a misconfigured hook.

## Format conventions (binding)

- snake_case English keys + `name_ar` siblings — preserve when editing schemas
- Conventional commits: `feat(core):`, `chore(learnings):`, etc.
- Convert relative dates to absolute ISO (YYYY-MM-DD)
- Reference the candidate ID consistently (`$ARGUMENTS`) in commit messages and reports
