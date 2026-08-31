# Prettier and Security Pre-commit Hooks

Date: 2026-08-31
Phase: 3
Status: active

## Context
Local pre-commit hooks need to align with the new CI pipelines. Currently, the repository uses `black` for Python formatting. We must introduce `prettier` for other filetypes, `bandit` for security linting, and a secrets detection hook (`gitleaks`).

## Decision
- **Black**: Pinned to a stable version (e.g. `24.8.0`).
- **Prettier**: Pinned to specific version via `pre-commit/mirrors-prettier`, scoped identically to the CI check (`types_or: [yaml, json, markdown]`).
- **Bandit**: Added via `PyCQA/bandit` and pinned.
- **Gitleaks**: Added via `gitleaks/gitleaks` to mirror the CI secrets check.

## Files touched
- `.pre-commit-config.yaml`
