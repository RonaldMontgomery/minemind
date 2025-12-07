# minemind

Minesweeper-in-the-terminal with a small deterministic solver. The CLI starts an interactive shell so you can create boards, reveal/flag cells, and ask the solver to apply guaranteed moves.

## Installation
- Prereqs: Python 3.8+ and `pip`.
- Optional but recommended: `python -m venv .venv && .\.venv\Scripts\activate` (Windows PowerShell) or `source .venv/bin/activate` (Unix).
- Install in editable mode from the repo root:
  ```bash
  pip install -e .
  ```

## Run
- Start the shell (installs the `minemind` entry point via `pyproject.toml`):
  ```bash
  minemind
  ```
  or
  ```bash
  python -m minemind
  ```
- Coordinates are zero-based: `row col`.
- A fresh beginner board is created on launch; the first reveal is always safe and triggers mine placement.

## Command Cheatsheet (with examples)
- `help` / `?` — list commands.
- `new` — start a new game.
  - Preset difficulty: `new beginner` | `new intermediate` | `new expert`.
  - Custom: `new 12 16 30` (rows cols mines).
- `reveal <r> <c>` — reveal a cell, e.g., `reveal 3 4`.
- `flag <r> <c>` — toggle a flag, e.g., `flag 2 7`.
- `solve` — run one solver step; applies all certain flags/reveals it finds.
- `exit` / `quit` — leave the shell.

## Known Limitations
- Solver only applies deterministic trivial + subset rules; no guessing/probabilistic play.
- Subset logic is pairwise only; no full CSP/advanced pattern search.
- Some helper modules (`dsu.py`, `lru.py`, `rng.py`, `signatures.py`, `snapshot.py`) are stubs today.
- `board.py` contains duplicated legacy functions outside the class; they are unused but remain present.
- CLI is text-only (no colors), zero-based indexing, and has minimal validation beyond what tests cover.

## Tests
- Run with pytest from the repo root:
  ```bash
  python -m pytest
  ```
- The suite is built on `unittest`; pytest will discover and run it.
