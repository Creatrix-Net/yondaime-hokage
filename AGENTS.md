# AGENTS.md — Instructions for any AI coding agent working on this repo

This file is the entry point. Any agent (Claude Code, another Claude session,
a different model entirely) starting work on `yondaime-hokage` reads this
FIRST, before touching any code.

This file defines **what to do**. The `.agent-context/` directory (see
below) is where an agent records **what it did, why, and what the next
agent needs to know**. Read both before writing a single line of code.

---

## 0. Read this before anything else

1. Read this file in full.
2. Read `.agent-context/STATE.md` — the current status of the project
   (which phase, what's done, what's in progress, what's blocked).
3. Read the most recent 2–3 files in `.agent-context/decisions/` to pick up
   recent reasoning that isn't yet folded into `STATE.md`.
4. Only then start work.

If `.agent-context/STATE.md` doesn't exist yet, this is the first agent
session — create it using the template in section 3 below, and note that
this is session 1.

---

## 1. The three phases

Work proceeds in three phases, **in order**. Do not start Phase 2 work
until Phase 1 is marked complete in `STATE.md`, and do not start Phase 3
until Phase 2 is complete. Partial/parallel work across phases is what
causes untracked regressions — don't do it, even if it looks efficient in
the moment.

An agent picking up mid-project should assume the phase recorded in
`STATE.md` is authoritative, not whatever phase this file's ordering
implies.

### Phase 1 — Stabilize: security, performance, current standards

Goal: the _existing_ feature set, unchanged in behavior, running on
current, secure, non-deprecated foundations. No new features. No
architectural redesign yet — that's Phase 2. This is a hardening and
modernization pass, not a rewrite.

Checklist (work through systematically, one cog/module at a time, commit
per logical unit):

- **discord.py currency audit**

  - Diff current code against the latest stable discord.py changelog and
    migration notes. Flag and fix deprecated API usage (e.g. legacy
    `Bot.__init__` kwargs, old intents patterns, anything using
    `discord.ext.commands` idioms that have a documented modern
    replacement).
  - Confirm privileged intents actually declared are actually required —
    don't request `members`/`message_content`/etc. unless a loaded cog
    uses them. Over-broad intents are both a security and a verification
    problem for bots at scale.
  - Fix known dead code / duplicate definitions found during audit (e.g.
    the duplicate `get_random_image_from_tag` sync+async definitions in
    `discordbot.py` — verify which is live, delete the other).

- **Security pass**

  - Every `eval`/`exec`-capable command (`dev eval`, Jishaku's `py`,
    `shell`, `sh` etc.) must be confirmed owner-only at the permission
    check level, not just hidden from help. Audit the actual check
    decorators, don't assume.
  - Confirm `JISHAKU_HIDE` / debug-tool exposure is correct for a
    production deploy profile vs a local/dev profile — these should not
    share a default.
  - Audit all `except:` / bare `except Exception:` blocks that swallow
    errors silently (several exist, e.g. around Tenor/Giphy calls) —
    replace with narrow exception handling and logging. Silent broad
    excepts hide both bugs and abuse attempts.
  - Config/secrets: replace the `configparser` + raw
    `os.environ.get(..., "False")` string-typed pattern in
    `lib/util/vars.py` with a typed settings approach (e.g.
    `pydantic-settings` or equivalent) — no more implicit string "False"
    stand-ins for missing booleans.
  - Confirm no tokens/secrets can leak into logs, Sentry breadcrumbs, or
    error embeds sent to Discord channels.
  - Review `remove`/purge and moderation commands for missing
    permission-hierarchy checks (e.g. can a mod ban someone with a higher
    role than themselves via a raw ID path).

- **Performance pass**

  - Any synchronous/blocking call inside an async context (file I/O,
    `requests`-style calls, CPU-bound image manipulation in `img.py`)
    should be moved to a thread executor or an async-native library.
  - Review `on_message`'s unconditional `process_commands` +
    unconditional message deletion in `finally` — confirm this doesn't
    cause redundant API calls or rate-limit pressure at scale; document
    the actual intended behavior in a code comment if it's staying.
  - Confirm the async SQLAlchemy engine/session (`lib/database/session.py`)
    is actually reused correctly (pooling) rather than creating a new
    engine per call anywhere in the codebase.

- **Database reality check** (prerequisite for Phase 2, do it here)
  - `lib/database/badges.py` and `backup.py` currently use Discord channel
    history as a datastore instead of the SQLAlchemy session that already
    exists. Decide, case by case, whether each should move to real
    Postgres-backed models now (Phase 1) or is explicitly deferred to
    Phase 2's modularity work — record the decision in
    `.agent-context/decisions/`, don't just silently pick one.
  - Where models are added, use SQLAlchemy 2.0 declarative style
    (`Mapped[]` / `mapped_column()`), not the legacy `Column()` style.
  - Every new model ships with a reviewed (not blindly accepted)
    `alembic revision --autogenerate` migration.

Exit criteria for Phase 1: no known deprecated discord.py API usage, no
silent broad excepts on security-relevant paths, no plaintext-string
config booleans, `dev`/Jishaku eval paths confirmed locked to owner,
database access is either real (SQLAlchemy+Postgres) or explicitly
documented as deferred with a reason.

### Phase 2 — Refactor: Red-DiscordBot-style modularity

Goal: restructure the _proven-working_ Phase-1 code into a modular
architecture inspired by Red-DiscordBot, without changing user-facing
command behavior unless explicitly agreed and logged as a decision.

Reference points from Red worth deliberately adapting (not copying
verbatim — Red is GPLv3, so treat it as a design reference, reimplement in
your own words/code, and check `LICENSE`/`SECURITY.md` in this repo before
lifting any actual code):

- **A generalized Config abstraction** — replace the mix of hardcoded
  enums (`ChannelAndMessageId`, `Tokens`, `Webhooks` in `vars.py`) and
  per-cog ad hoc storage with one consistent, driver-backed
  (Postgres via the Phase-1 SQLAlchemy layer) config API scoped by
  guild/user/channel/role/global, the way Red's `Config` object works.
- **Per-guild cog/feature toggling** — not necessarily full dynamic
  cog install/uninstall like Red's downloader (that's a large surface
  area, decide explicitly whether it's in scope), but at minimum
  per-guild enable/disable of feature categories, backed by the new
  Config layer.
- **A real permissions framework** — beyond owner-ID + blacklist,
  a config-driven per-guild command permission override system.
- **Cog boundary cleanup** — `lib/classes/`, `lib/functions/`,
  `lib/util/` currently mix genuinely shared utilities with
  single-cog-specific logic. Each cog should own its
  cog-specific code; only truly cross-cutting code stays in `lib/`.

Every structural decision here (what moves where, what gets merged, what
gets deprecated) goes in `.agent-context/decisions/` before the change is
made, not after — see section 3.

Exit criteria for Phase 2: Config abstraction in place and at least the
highest-value cogs (moderation, setup, antiraid) migrated onto it; clear
`lib/` vs `cogs/` boundary documented in `.agent-context/STATE.md`;
existing commands still function equivalently (regression-checked, not
assumed).

### Phase 3 — Build: new, hand-picked features

Goal: implement new functionality by hand (agent-assisted, not
auto-generated wholesale) on top of the Phase-2 architecture. Candidate
features and any feature explicitly greenlit for this phase get their own
file under `.agent-context/decisions/` describing scope _before_
implementation starts, so a future agent knows what "done" means for that
feature without re-deriving it from the diff.

Do not begin Phase 3 scoping until Phase 2's exit criteria are marked met
in `STATE.md`.

---

## 2. Ground rules that apply across all phases

- **One logical change per commit**, with a commit message that references
  the relevant `.agent-context/decisions/` file when the change came from
  a recorded decision.
- **No behavior change without a recorded reason.** If a fix incidentally
  changes user-visible behavior, say so explicitly in both the commit and
  `STATE.md` — don't let it hide inside a "cleanup" commit.
- **Never re-derive a decision that's already recorded.** If
  `.agent-context/decisions/` already answered a question (e.g. "why
  Postgres over SQLite", "why Alembic"), don't re-litigate it — link to it.
- **When in doubt about scope, write the doubt down** in
  `.agent-context/decisions/` as an open question rather than silently
  picking an interpretation.
- Match the project's existing license/attribution obligations — check
  `LICENSE`, `SECURITY.md`, `CODE_OF_CONDUCT.md` before adding new
  dependencies or lifting patterns from GPL'd projects like Red.

---

## 3. The `.agent-context/` directory

This directory is **not tracked by git** (see `.gitignore` — the entry is
already added; confirm it's still there before writing anything here). It
exists purely so that context transfers cleanly between agent sessions —
including sessions run by a different model or a different tool — without
re-deriving history from the diff or from this file's static instructions.

### Why it's gitignored

The point is a scratch/working-memory layer that doesn't pollute the
repo's actual history, doesn't need to survive a squash-merge, and can be
freely rewritten/pruned without affecting collaborators who only care
about the code. It is a _local reasoning trail_, not documentation for
end users — that's what `docs/` and `README.md` are for.

### Structure

```
.agent-context/
├── STATE.md              # single current-status file — always up to date
├── decisions/             # one file per decision, append-only, never edited after the fact
│   └── YYYY-MM-DD-short-slug.md
├── phase-logs/             # one running log per phase, session-by-session notes
│   ├── phase-1.md
│   ├── phase-2.md
│   └── phase-3.md
└── archive/                # superseded decisions/logs moved here, never deleted
```

### `STATE.md` — required sections, kept current, overwritten in place

```markdown
# Project State

Last updated: <date> by <agent/session identifier>

## Current phase

Phase <1|2|3> — <one line on where exactly within the phase>

## Phase 1 status

- [ ] discord.py currency audit
- [ ] Security pass
- [ ] Performance pass
- [ ] Database reality check
      (check off as completed, add sub-items as discovered)

## Phase 2 status

(same pattern, only relevant once Phase 1 is checked off)

## Phase 3 status

(same pattern)

## In progress right now

<what the last session was mid-way through, specific enough that a new
agent can resume without guessing>

## Known open questions

<anything flagged as undecided — link to the decisions/ file if one exists>

## Do not touch / explicitly deferred

<anything intentionally left alone, and why — prevents a future agent
"fixing" something that was deliberately left as-is>
```

### `decisions/YYYY-MM-DD-short-slug.md` — one per decision

Append-only. Once written, a decision file is never edited to change its
conclusion — if a later session reverses a decision, write a **new** file
that references and supersedes the old one, and move the old one's status
line to "superseded by <new file>". This preserves the actual reasoning
history instead of erasing it.

```markdown
# <Decision title>

Date: <date>
Phase: <1|2|3>
Status: active | superseded by <file>

## Context

What prompted this decision — what was ambiguous, what tradeoff existed.

## Options considered

- Option A — pros/cons
- Option B — pros/cons

## Decision

What was chosen.

## Reasoning

Why — this is the part future agents actually need; the "what" is visible
in the diff, the "why" is not.

## Files touched

List of files created/modified/deleted as a direct result of this
decision, so a future agent can trace decision → code without re-reading
the whole diff history.
```

### `phase-logs/phase-N.md` — running session log

Append a dated entry per work session, most recent at the bottom. Short —
this is a log, not a report. Points to `decisions/` files rather than
repeating their content.

```markdown
## <date> — session <n>

- Worked on: <what>
- Decisions made: <link to decisions/ files, if any>
- Files created: <list>
- Files deleted: <list, with reason if not obvious>
- Handed off with: <what the next session should pick up>
```

### Rules for writing to `.agent-context/`

- Write to `STATE.md` **every session**, even a short one — it's the
  single source of truth for "where are we."
- Write a `decisions/` file **before** making a non-obvious change, not
  after — the point is to capture reasoning while it's live, not to
  reconstruct it from memory afterward.
- Never delete a file in `.agent-context/` — move superseded material to
  `archive/` instead. Context loss is the exact failure mode this
  directory exists to prevent.
- Keep entries factual and specific (file paths, exact reasoning,
  concrete tradeoffs) — vague notes ("cleaned things up") are worse than
  no note, because they create false confidence that context was
  preserved.

---

## 4. First actions for a new agent session

1. Confirm `.agent-context/` exists and `.gitignore` excludes it. If not,
   create/fix both before anything else.
2. Read `.agent-context/STATE.md`. If it doesn't exist, this is session 1
   — create it, set Current phase to `1`, and note that in
   `phase-logs/phase-1.md`.
3. Pick up exactly where "In progress right now" left off, or if empty,
   take the next unchecked item in the current phase's checklist.
4. Before ending the session, update `STATE.md` and append to the
   relevant `phase-logs/phase-N.md` — this is not optional cleanup, it's
   the deliverable that makes the next session possible.
