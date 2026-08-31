# SQLAlchemy declarative_base migration to DeclarativeBase class

Date: 2026-08-31
Phase: 1
Status: active

## Context
`lib/util/vars.py` uses `sqlalchemy.orm.declarative_base()` function which is
deprecated in SQLAlchemy 2.0. AGENTS.md Phase 1 requires using SQLAlchemy 2.0
declarative style (`Mapped[]` / `mapped_column()`), and the database reality
check item references this as well.

## Options considered
- Option A: Simple swap — replace `Base = declarative_base()` with a
  `DeclarativeBase` class. Pros: minimal change. Cons: doesn't address the
  import path change (`sqlalchemy.orm.declarative_base` vs `sqlalchemy.orm`).
- **Option B (chosen)**: Replace with `DeclarativeBase` class style, which
  future-proofs for `Mapped`/`mapped_column` usage and satisfies AGENTS.md's
  requirement for SQLAlchemy 2.0 declarative style.

## Decision
Replace `Base = declarative_base()` in `vars.py` with a `DeclarativeBase`
subclass. Update all imports of `Base` to use the new class. This is a
prerequisite for Phase 2's database work.

## Reasoning
The `declarative_base()` function emits deprecation warnings in SQLAlchemy 2.0+
and will be removed in a future version. The class-based approach is the
officially recommended pattern and enables better type checking.

## Files touched
- `minato_namikaze/lib/util/vars.py` — Base definition change
- Any files importing `Base` from vars (launcher.py, __init__.py, etc.)
