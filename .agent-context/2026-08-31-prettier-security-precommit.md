# Prettier Formatting CI, PR Security Scanning, and Pre-commit Hooks

Date: 2026-08-31
Phase: post-Phase-3 maintenance (extends
`decisions/2026-08-31-github-maintenance.md` — same task family, split
into its own file since it's additive scope, not a correction)
Status: active

## Context
On top of the `.github/` audit already scoped, three concrete additions
were requested: a formatting check using Prettier, a pull-request
security scan, and pre-commit hooks covering both.

Important scoping note before implementation starts: **Prettier does not
format Python.** This is a Python discord.py bot — Python files are
already covered by `black` (confirmed present in the original pre-commit
setup). Prettier's actual scope here is non-Python text formats already
in the repo: YAML (`.github/workflows/*.yml`, any `.yml` issue templates
from the `.github` maintenance task), JSON (`lib/data/commands.json`,
`lib/data/listing.json`), Markdown (`README.md`, `docs/`, `SECURITY.md`,
issue/PR templates), and TOML if the project wants it included (check
Prettier's TOML support/plugin situation — it's not built-in, may need a
plugin or may be better left to a Python-specific TOML formatter). Don't
let "format with Prettier" quietly turn into "reformat all the Python" —
that's `black`'s job and already exists.

## Options considered
For the security scan specifically:
- **Option A**: Rely solely on the already-present `dependency-review.yml`
  (dependency vulnerability checks) and call that sufficient.
  - Insufficient by itself — code CODE security (as opposed to dependency
    security) — Phase 1's security pass already found real issues in
    application code (eval/exec exposure, secrets handling) manually.
    A recurring automated check on every PR should cover code, not just
    dependencies.
- **Option B**: Add both a static-analysis security scan for Python code
  (Bandit, or CodeQL's Python support) and keep the existing dependency
  review — plus a secrets-leak check on the diff.

## Decision
**Option B.** Concretely:

### 1. Prettier formatting check (CI)
- New workflow, e.g. `.github/workflows/prettier.yml`.
- Scope: `**/*.{yml,yaml,json,md}` at minimum — exclude anything
  auto-generated (e.g. `Pipfile.lock` is JSON but shouldn't be
  Prettier-reformatted; `docs/` build output if any is committed,
  which it shouldn't be).
- Mode: **check-only in CI** (`prettier --check`), not auto-fix-and-push
  — CI should fail and tell a contributor to run Prettier locally
  (via the pre-commit hook, see below) rather than the workflow silently
  rewriting their PR. If auto-fix-on-PR is actually wanted instead,
  that's a real tradeoff (convenience vs. surprising diffs on someone
  else's PR) — flag it as an explicit choice rather than defaulting to
  it.
- Add a `.prettierrc` (or `.prettierrc.json`) at repo root so local
  pre-commit runs and CI use identical config — don't let them drift.
- Add a `.prettierignore` mirroring the scope exclusions above.

### 2. PR security scanning (CI)
- **Bandit** (Python-specific static security analysis) as a new
  workflow or a job added to an existing one — flags exactly the class
  of issue Phase 1's manual security pass was hunting for (bare excepts
  hiding failures, exec/eval usage, hardcoded secrets, insecure
  deserialization, etc.), but automated and recurring on every PR
  instead of one-time.
- Keep/confirm `dependency-review.yml` (already exists per the
  `.github` maintenance audit) for dependency-side vulnerabilities —
  don't duplicate this with a second dependency scanner unless Bandit's
  scope genuinely doesn't overlap (it doesn't — Bandit is code, not
  dependencies).
- Add a secrets-in-diff check (e.g. `gitleaks` action, or confirm
  GitHub's native secret scanning + push protection is enabled at the
  repo settings level — the latter doesn't need a workflow file at all,
  just a settings toggle, worth checking before adding a redundant
  Action for it).
- All security-scan jobs should be **required status checks** on the
  default branch's protection rules if branch protection is in use —
  note this as a repo-settings step, not just a workflow file, since a
  workflow that runs but isn't required doesn't actually block anything.

### 3. Pre-commit hooks (`.pre-commit-config.yaml`)
- Confirm the existing `black` hook is still current (correct rev
  pinned, not stale).
- Add a Prettier pre-commit hook (`mirrors-prettier` or equivalent)
  scoped identically to the CI workflow's file patterns, so local
  pre-commit and CI never disagree about what should be reformatted.
- Add a Bandit pre-commit hook for the same fast local feedback loop as
  item 2's CI job — catching an issue locally before a PR is faster than
  waiting for CI.
- Add a secrets-detection pre-commit hook (`detect-secrets` or
  `gitleaks` pre-commit mirror) matching whatever tool item 2 settles on
  for CI, so the same thing is checked in both places.
- Confirm hook versions are pinned (not `main`/`latest`) for
  reproducibility, consistent with how `black`'s existing pin presumably
  already works.

## Reasoning
Splitting Prettier/security/pre-commit into its own decision file rather
than folding it into the existing `.github` maintenance checklist keeps
the two tasks independently trackable — the maintenance audit is about
fixing what's broken/stale, this is about adding new recurring checks
that didn't exist before. Calling out Prettier's actual language scope
up front prevents a plausible but wrong interpretation (reformatting
Python) that would conflict with the existing `black` setup. Keeping CI
and pre-commit configs pointed at identical scope/config (same
`.prettierrc`, same hook versions) is the concrete mechanism that
prevents the common failure mode where local pre-commit and CI quietly
disagree and contributors get surprised by CI failures pre-commit didn't
catch.

## Files touched
None yet — scope only. Implementing session logs actual files
created/modified in `phase-logs/` per the file this decision extends.
