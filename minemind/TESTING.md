# TESTING

## How to Run
From the repo root:
```bash
python -m pytest
```
(pytest will discover the `unittest`-style tests in `minemind/tests`.)

## Coverage by File
- `test_board_init.py`: Cell defaults, standard difficulty presets, custom size/density, and mine clamping.
- `test_board.py`: Neighbor math, flood-fill boundaries, win/loss transitions, public `reveal`/`flag` behavior, and render edge cases (wrong flags after loss).
- `test_generator.py`: Deferred mine placement respecting the first-click safe zone and clamping when the safe zone dominates the board.
- `test_frontier.py`: Identification of frontier cells (revealed numbers with hidden neighbors) and absence when all neighbors are revealed.
- `test_rules.py`: Solver trivial rules (flag vs reveal), subset deductions (safe vs mine difference), and move deduplication.
- `test_solver_small.py`: Sanity checks that solver returns well-formed move lists on tiny boards.
- `test_cli.py`: CLI command validation for `new`, `reveal`, and `flag`; ensures no crashes on bad input and zero-based coordinate handling.

## Notes
- Tests assume deterministic layouts when mines are manually arranged and `mines_placed` is set to True to bypass random placement.
- A skipped placeholder remains in `test_board.py` for future CLI-specific helpers.
