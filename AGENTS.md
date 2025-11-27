# Repository Guidelines

## Project Structure & Module Organization
- Core CLI lives in `src/agentkit_cli/`: `__main__.py` wires argparse, `init.py` scaffolds projects and templates, `check.py` validates local tools, and `config.py` centralizes defaults.
- Root docs (`README.md`, `INSTALL*.md`, `QUICKSTART.md`, `START-HERE.md`) explain install, workflow, and generated assets; keep them in sync with code changes.
- `test-project/` is a generated sample for manual smoke tests; avoid editing it unless intentionally updating fixtures.

## Build, Test, and Development Commands
- Use Python 3.11+. Install in editable mode with dev tools: `pip install -e .[dev]` (or `uv pip install -e .[dev]`).
- Quick smoke: `agentkit --version`, `agentkit check`, then `agentkit init demo --ai claude --here` to verify scaffolding.
- Run lint/format locally: `ruff check .` and `black src tests`.
- Execute tests: `pytest` (or `uv run pytest`). Add `-k <pattern>` when iterating on a specific area.

## Coding Style & Naming Conventions
- Format with Black (88-char lines) and lint with Ruff (E,F,I,N,W rules; E501 ignored because Black handles wrapping).
- Use 4-space indents, `snake_case` modules/functions, `PascalCase` classes, and `UPPER_SNAKE` constants. Keep CLI command names short lowercase verbs (`init`, `check`).
- Prefer typed function signatures, concise docstrings, and rich console output that is friendly but brief.

## Testing Guidelines
- Tests belong under `tests/` following `test_*.py`, `Test*` classes, and `test_*` functions (see `pyproject.toml`).
- Favor fast unit tests; when touching filesystem code (e.g., `init_project`), use `tmp_path` fixtures and avoid mutating real directories.
- Cover edge cases such as non-empty dirs with `--force` and missing tool checks. Add regression tests when fixing bugs.

## Commit & Pull Request Guidelines
- Commit messages: imperative mood, clear scope (e.g., `add init force prompt guard`), body optional but useful for rationale.
- PRs should include a short summary, steps to validate (commands run like `pytest`, `ruff check .`, `agentkit check`), and linked issues. Update docs when user-facing behavior shifts.
- Exclude generated deliverables (`deliverables/`, `.agentkit/` outputs) unless explicitly refreshing templates.

## Security & Configuration Tips
- Never hardcode API keys or personal paths; keep defaults in `config.py` and read from env when needed.
- `agentkit check` shells out to tool binaries—ensure any new checks handle timeouts and failures gracefully. Guard new scripts/templates against accidental secret leakage. 
