# Correction: old_outdated/ and slash_old/ Are Staging Folders, Not Legacy Code

Date: 2026-08-31
Phase: 3
Status: active — supersedes item 1 of `2026-08-31-phase-3-scope.md`

## Context
The original Phase 3 scope file treated `old_outdated/` and `slash_old/`
as legacy/abandoned code, to be audited file-by-file with each file
either ported (if still useful) or confirmed redundant and discarded.
That framing was wrong. The project owner clarified: these folders were
**deliberately created as a staging area** — cogs were moved there
specifically so they could be updated/rewritten separately from the live
`cogs/` tree, then moved back to their original location once brought up
to current standards. They are not dead code; they are a work-in-progress
holding pen.

## Options considered
- **Option A (original, superseded)**: audit each file, port what's
  useful, discard/confirm-redundant the rest, delete folders once nothing
  of value remains.
- **Option B**: every cog currently in `old_outdated/`/`slash_old/` is
  in scope for update, none are discarded as "not worth it" — the folders
  exist expressly to hold this in-progress work, so "nothing of value
  remains" isn't the exit condition. The exit condition is "everything
  has been moved back."

## Decision
**Option B.** For every file currently in `old_outdated/` and
`slash_old/`:
1. Rewrite/update it to current Phase 1/2 standards — async-native, no
   deprecated discord.py API usage, using the Config API
   (`lib/database/config.py`/`config_api.py`) for any persistence, and
   the permissions framework from `cogs/core.py` for access control,
   consistent with every other cog in the current tree.
2. Move it back to its correct location under `minato_namikaze/cogs/`
   (or `lib/` if it's genuinely shared logic, not a cog) — i.e. where it
   would live if it had been written fresh against the current
   architecture, not necessarily its old pre-staging path.
3. Confirm it's loaded correctly (via the existing cog auto-load
   mechanism in `discordbot.py`) and doesn't collide with a cog that may
   have been independently rebuilt in `cogs/` during Phases 1–2 — if a
   collision exists, that's a decision point (which version wins, or do
   they merge) and gets its own small decision note before resolving.
4. Only once a file has been fully moved back does it get deleted from
   the staging folder — deletion happens naturally as a result of the
   move (`mv`, not a separate cleanup step), not as a bulk purge at the
   end.

**Exit condition for item 1**: both `old_outdated/` and `slash_old/` are
empty and are removed entirely — because everything that was staged in
them has been updated and relocated, not because remaining contents were
judged unnecessary. If, while working through a specific file, it turns
out that file's functionality now genuinely duplicates something already
rebuilt elsewhere during Phase 2, that's still a real finding worth a
one-line note in the phase-3 log — but the default assumption going in
is "this gets updated and moved back," not "this gets triaged for
deletion."

## Reasoning
Treating the staging folders as legacy-code-to-triage risked exactly the
failure this correction exists to prevent: an agent silently deciding a
cog "isn't worth porting" and dropping it, when the actual intent was
that every cog in there is coming back, just modernized. The move-based
exit condition (folders empty because everything relocated, not because
things were pruned) makes the difference between the two framings
mechanically checkable rather than a matter of interpretation.

## Files touched
None yet — correction only. Implementation sessions log their own
per-file moves in `phase-logs/phase-3.md`, and use `mv`
(update-in-place then relocate) rather than copy+separately-delete, so
there's never a window where a cog exists in both the staging folder and
its final location.
