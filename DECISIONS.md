# Architecture and Design Decisions (Milestone M0)

## 1. Schema Validation
- Used `pydantic` heavily in `schemas.py`. It guarantees data matches exactly what's detailed in `AGENT_SPEC.md` without requiring manual validation layers.

## 2. LLM Cache Reset
- `LLMCache` was implemented using `sqlite3` for persistent on-disk storage with a `SHA256` hash of parameters as a unique key.
- When an `LLMResponse` is retrieved from the cache, `tokens_in`, `tokens_out`, and `estimated_cost` are deliberately overwritten to `0.0`. This ensures that cached hits strictly avoid draining the budget within the `BudgetTracker`.

## 3. CLI framework
- Using `typer` instead of `argparse`. Since it integrates well with standard types, handles help documentation elegantly, and is highly readable as the CLI scope expands in subsequent milestones.

## 4. Build System
- Swapped to `hatchling` within `pyproject.toml` targeting `src/dseek`. This provides a modern, fast, PEP-621 compliant backend out of the box and seamlessly enables editable installs (`pip install -e .`).
