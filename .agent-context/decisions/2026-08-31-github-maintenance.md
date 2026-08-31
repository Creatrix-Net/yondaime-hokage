# GitHub Actions Maintenance

Date: 2026-08-31
Phase: 3
Status: active

## Context
The repository needs a comprehensive static analysis and security pass enforced via CI to complement local development hooks. We need to introduce Prettier (for non-Python formatting) and Bandit/Gitleaks for security, without stepping on Python's Black formatting.

## Decision
- **Prettier**: Enforced strictly via a new `prettier.yml` action in check-only mode (`--check`), limited to `.yml`, `.yaml`, `.json`, and `.md` files. Excludes Python files and `Pipfile.lock`.
- **Bandit**: Added as a static security check for Python code.
- **Gitleaks**: Added to detect secrets in PR diffs, as native GitHub secret scanning status couldn't be confirmed.
- **Required Status Checks**: These new CI jobs (Prettier, Bandit, Gitleaks) should be manually configured as "Required Status Checks" in the GitHub Branch Protection settings for the `master` branch. 

## Files touched
- `.prettierrc`, `.prettierignore`
- `.github/workflows/prettier.yml`
- `.github/workflows/security.yml`
