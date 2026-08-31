# .github/ Maintenance — CI Workflows, Issue Templates, SECURITY.md

Date: 2026-08-31
Phase: post-Phase-3 maintenance (not part of the original three-phase plan
in AGENTS.md — repo/CI hygiene, tracked here as its own scoped task)
Status: active

## Context
All three phases in `AGENTS.md` are complete per `STATE.md`. This is a
new, separately-scoped task: `.github/` was never touched during Phases
1–3 (those focused on the bot's runtime code), and has drifted —
workflow files reference outdated action versions, some workflows don't
actually trigger/complete correctly, issue templates are stale, and
`SECURITY.md` no longer reflects the current state of the project
(supported versions, reporting process, or both).

Known `.github/` contents as of the last full repo audit (pre-Phase-1):
`workflows/lint.yml`, `workflows/python-app.yml`, `workflows/label.yml`,
`workflows/greetings.yml`, `workflows/dependency-review.yml`,
`workflows/summary.yml`, plus `.deepsource.toml` and a Dependabot config
at the repo root. Confirm this list against the actual current repo
before starting — Phase 1–3 work may have changed dependency management
or Python version in ways CI doesn't yet reflect (e.g. if `Pipfile` was
touched during the SQLAlchemy/Postgres work, `python-app.yml`'s install
step needs to match).

## Options considered
- **Option A**: Patch workflow files minimally — bump action version pins
  only, leave structure/triggers as-is.
- **Option B**: Full audit — for each workflow, confirm it still triggers
  on the right events, actually completes (not just "doesn't error on
  syntax"), uses current action versions, and still makes sense given
  what Phases 1–3 changed (e.g. a lint workflow should reflect whatever
  linter/formatter is actually in use now, not whatever was configured
  when the repo was in its pre-Phase-1 state).

## Decision
**Option B.** Version-pin bumps alone won't fix workflows that "don't
run" — that's very likely a trigger condition, a permissions block, or a
step referencing something Phases 1–3 removed/renamed (e.g. if `Pipfile`
dependency management changed, or file paths moved during the cog
migration work). This needs a real audit, not a mechanical bump.

### Checklist

**Workflows (`.github/workflows/*.yml`)**
- For each workflow: confirm the trigger (`on:`) still matches actual
  repo behavior (branch names, path filters — cog migrations may have
  moved paths that a `paths:` filter still references by old location).
- Bump every action reference to current major versions (e.g.
  `actions/checkout`, `actions/setup-python`, any Docker/build actions)
  — pin to a major version tag, don't pin to a commit SHA unless the
  project has a stated reason to (check if one already exists before
  changing that convention).
- `python-app.yml` (or equivalent): confirm the Python version matrix
  matches what the project actually requires now (3.13 per `Pipfile` as
  of the original audit — reconfirm, don't assume it hasn't changed) and
  that the dependency install step matches current dependency management
  (still `pipenv`? confirm nothing shifted during Phase 1's security
  pass).
- `lint.yml`: confirm it invokes whatever formatter/linter is actually
  configured in the repo now (originally `black` + `pre-commit`) — if
  Phase 1/2 introduced new tooling (e.g. `ruff`, `mypy` for the new typed
  Config API and SQLAlchemy 2.0 models), the lint workflow should reflect
  that, not just the pre-Phase-1 toolchain.
- `dependency-review.yml`: confirm it still functions given current
  `Pipfile`/`Pipfile.lock` — this one commonly breaks silently on
  permission scope issues (needs `contents: read` /
  `pull-requests: write` as appropriate) rather than syntax.
- `label.yml`, `greetings.yml`, `summary.yml`: lower priority but same
  treatment — confirm trigger validity and action versions; these are
  less likely to be "broken" in a way that matters functionally, more
  likely just stale.
- For every workflow that's confirmed "doesn't run" — identify the
  *actual* cause (bad trigger, missing permission, invalid syntax,
  removed dependency) and note it before fixing, so the fix is targeted
  rather than a rewrite-and-hope.

**Issue templates (`.github/ISSUE_TEMPLATE/`)**
- Confirm current format: if these are old-style Markdown templates,
  migrate to GitHub's YAML issue-forms format (`.yml` templates with
  structured fields) — the current GitHub standard, better structured
  data than freeform Markdown.
- Add/update `.github/ISSUE_TEMPLATE/config.yml` with accurate contact
  links (blank-issue disabling if desired, links to discussion/support
  channels — check `cogs/info/mysupport.py` and `example.ini` for the
  project's actual current support server/contact info rather than
  inventing new ones).
- Confirm templates reflect the *current* bot (e.g. if templates
  reference old command names or old architecture terms that Phase 2's
  refactor renamed).

**Pull request template**
- Check whether `.github/PULL_REQUEST_TEMPLATE.md` exists; if so, confirm
  it references current contribution standards (e.g. should now mention
  the `.agent-context/decisions/` convention if human contributors are
  expected to interact with agent-driven changes, and current lint/test
  requirements from the updated `lint.yml`).

**`SECURITY.md`**
- Update the supported-versions table to reflect actual current
  versioning (confirm whether the project uses version tags/releases at
  all post-refactor, or is rolling — adjust the table's shape
  accordingly rather than leaving stale version numbers).
- Update the vulnerability-reporting process/contact to whatever is
  actually current (check for a security contact email or private
  reporting channel — GitHub's private vulnerability reporting feature,
  if not already enabled, is worth turning on and referencing here
  instead of/alongside an email).
- Given Phase 1's security pass touched real vulnerability classes
  (eval/exec exposure, secrets handling, permission-hierarchy checks),
  it's worth `SECURITY.md` briefly reflecting that a security review
  happened, without turning it into a changelog — a security policy
  document, not a project history.

**`.deepsource.toml` / Dependabot config**
- Confirm `.deepsource.toml` analyzers still match the actual language/
  tooling mix post-refactor (e.g. if new tooling was added per the
  lint.yml item above, DeepSource config should know about it).
- Confirm Dependabot config's `package-ecosystem` and paths are still
  correct (still `pipenv`? still watching the right manifest paths?).

## Reasoning
This is scoped as a full audit rather than a quick version-bump because
"some [workflows] do not run" is a symptom, not a diagnosis — the actual
cause could be anywhere from a stale trigger condition to a path that
moved during the Phase 3 cog migration. Fixing the visible symptom
(bumping action versions) without finding the actual cause risks leaving
workflows that still silently fail to trigger. Grouping issue templates,
SECURITY.md, and CI config together in one task (rather than three
separate ones) is appropriate here since they're all "repo hygiene
catch-up after three phases of runtime-code-focused work" — same root
cause, same audit pass makes sense.

## Files touched
None yet — scope only. The implementing session should list every
`.github/` file it touches in `phase-logs/` (there's no dedicated
phase-4 log file yet; use `phase-logs/phase-3.md` with a clear
`## .github maintenance` heading, or create `phase-logs/maintenance.md`
if this kind of post-phase task recurs — worth a quick decision if it
comes up again).
