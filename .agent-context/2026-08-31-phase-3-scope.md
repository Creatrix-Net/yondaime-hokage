# Phase 3 Scope — Legacy Migration, Interaction UI, Economy, New Games

Date: 2026-08-31
Phase: 3
Status: active

## Context
Phase 2 closed with `old_outdated/` and `slash_old/` explicitly deferred
(see `STATE.md` "Do not touch"). Phase 3 begins by closing that
deferral, then builds hand-picked new features on top of the now-complete
Config abstraction (`lib/database/config.py` + `config_api.py`) and
permissions framework from `cogs/core.py`. This file scopes that work so
implementation has a fixed definition of "done" instead of growing
unbounded mid-session.

This is a scope-setting document, not an implementation log. Each work
item below gets its own follow-up decision file when a session starts
implementing it, if choices come up that aren't already settled here.

## Options considered
For the legacy folders specifically:
- **Option A**: Delete `old_outdated/` and `slash_old/` outright, treat
  any needed functionality as a fresh Phase 3 build.
- **Option B**: Audit each file for logic not yet reimplemented anywhere
  in current `cogs/`, port anything still relevant onto the Phase 2
  architecture (Config API, permissions framework), then delete the
  folders once nothing of value remains unmigrated.

## Decision
**Option B** for the legacy folders. Blind deletion risks silently
losing a feature that was working and just never got carried through
Phases 1–2 because it lived in a folder explicitly marked "outdated" by
name rather than by actual review.

Full Phase 3 work items, in the order they should be tackled:

### 1. Legacy folder migration and removal
- Go file by file through `old_outdated/` and `slash_old/`.
- For each file: determine whether its functionality already exists in
  current `cogs/` (in which case just confirm and delete), or whether it
  represents something not yet ported.
- Anything worth keeping gets rewritten against current standards — not
  copy-pasted — using the Config API for any persistence and the
  permissions framework from `cogs/core.py` for access control, matching
  Phase 1/2 conventions (async-native, typed, no bare excepts).
- Record what was ported vs. discarded and why, per file or logical
  group, in a dedicated decision file
  (`decisions/YYYY-MM-DD-legacy-migration.md`) — this is the audit trail
  that justifies the deletion.
- Only delete a legacy file once its disposition (ported / confirmed
  redundant / confirmed obsolete) is recorded. Do not delete first and
  document later.
- `slash_old/` in particular predates the current app-command
  implementation — confirm nothing there represents app-command coverage
  that current `cogs/` is missing before removing it.

### 2. Reaction roles → button-based
- Replace the emoji-reaction interaction model with persistent
  `discord.ui.View`/`Button` components (`custom_id`-based, registered
  via `bot.add_view()` on startup so buttons survive bot restarts).
- Note: `lib/classes/reaction_roles.py` was already deleted in Phase 2's
  cog-boundary cleanup — confirm where its logic landed (likely inlined
  into a cog) before starting, so this isn't rebuilt from scratch
  unnecessarily.
- Store role/button mappings via the Config API (guild-scoped), not a
  bespoke table — this is exactly the kind of per-guild structured data
  the Config abstraction was built for.
- Preserve existing functionality (multiple role groups per message,
  add/remove-on-click toggle behavior) as a baseline; buttons are a UI
  migration, not a feature cut, unless a limitation of buttons (e.g. the
  25-component-per-message cap) forces a documented behavior change.

### 3. Giveaways → database-backed, Red-style advanced features
- Move off any ad hoc/in-memory giveaway state onto real persistence —
  either dedicated SQLAlchemy models or the Config API, whichever fits
  the data shape better (decide explicitly in the implementation
  session's decision file: giveaways have relational shape — entries,
  a giveaway, winners — which may argue for real models over Config's
  key/value shape).
- Feature set to reach parity/exceed Red-style giveaway cogs:
  - Persistent entries (survives restart, no reliance on reaction cache).
  - Entry requirements (role requirement, account-age minimum, message-
    count minimum if tied into the new economy/activity tracking).
  - Weighted winner selection (e.g. bonus entries for boosters or a
    role) as an optional mode, simple uniform-random as default.
  - Multi-winner support with a real reroll that respects who already
    won and excludes them.
  - Scheduled end time with automatic winner announcement (needs a
    reliable scheduler — check what `reminder.py`'s dispatch mechanism
    already provides before building a second scheduling system).

### 4. Economy / currency system (new)
- Red-style bank abstraction: per-user balance, guild-scoped or global
  currency (decide per Red's own `bank.is_global()` pattern — expose as
  a Config-backed toggle, not a hardcoded choice).
- Core commands: balance check, leaderboard, transfer between users,
  admin set/add/remove balance.
- At least one faucet (a way to earn currency — e.g. a claim/daily
  command with a cooldown) and one sink (a way to spend it — even a
  simple one, like an entry cost for a game or giveaway bonus entries)
  so the economy isn't a dead-end number.
- Currency name/symbol configurable per guild via the Config API, not
  hardcoded — this is a direct, concrete use of the Phase 2 Config
  abstraction and a good first real consumer of it in Phase 3.
- Bank balances persist via real SQLAlchemy models (this is exactly the
  relational, frequently-updated, transactionally-sensitive data the
  Phase 1 database work was for) — not the Config API's JSON-blob shape.

### 5. New game cogs (Red-inspired, hand-picked)
Candidates, each independently scoped/greenlit rather than built as one
undifferentiated batch:
- **Trivia** — question-bank driven, per-guild leaderboard, integrates
  with the new economy as an optional reward hook.
- **Higher-or-lower** — simple betting minigame, natural economy sink.
- **Counting** — dedicated counting-channel game (config-driven channel
  assignment via the Config API).
- **Did-you-mean command suggestions** — not a "game" but was flagged
  earlier as high-value/low-cost (Levenshtein-distance suggestion on
  mistyped commands) — worth slotting in here since it touches the same
  UX-polish spirit as the games work.
Each of these should get exactly the same treatment as item 3/4: a scope
note if anything is non-obvious, real persistence via Config API or
models as appropriate, and a check against `lib/classes/games/` (which
already holds Akinator/Connect Four/Hangman/TicTacToe/Typeracer engines)
so new games follow that existing pattern rather than inventing a
parallel one.

## Reasoning
Sequencing legacy migration first prevents Phase 3 building new features
on top of an architecture that still has an unaudited, undocumented
"do not touch" folder sitting next to it — anything genuinely useful in
`old_outdated/`/`slash_old/` should either be alive in current `cogs/`
or explicitly declared dead before new work piles on top. Buttons before
giveaways/economy because the button-based interaction pattern
(persistent views, custom_id handling) is reusable infrastructure the
later items can lean on. Economy is scoped before games because several
of the game candidates (trivia rewards, higher-or-lower bets) depend on
it existing first.

## Files touched
None yet — this is the scope decision only. Implementation sessions will
each log their own files touched in the relevant `decisions/` entry and
in `phase-logs/phase-3.md`.
