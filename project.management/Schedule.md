# Minesweeper Project Schedule (Nov 24 – Dec 7)

This is an **implementation timeline** assuming:

- Team meets **Monday night (Nov 24)** to align on requirements, design ideas, and edge cases.
- Most individual coding work begins on **Tuesday (Nov 25)**.
- Due date: **Sunday, Dec 7**.
- Rough capacity: ~1–2 hours on weekdays, ~3–4 hours on weekends.

Everyone writes **their own code**, but can share:
- Design ideas
- Edge cases
- Test scenarios

The schedule is written from the perspective of a single student developer.

---

## Monday, Nov 24 – Team Meeting & Planning (No Major Coding Required)

**Goal:** Get everyone aligned on requirements, architecture, and edge cases.

**Team Meeting Agenda (60–90 minutes):**
- Re-read and summarize the requirements together.
- Agree on **core architecture**:
  - `core/board.py` for game logic
  - `render.py` for board → text rendering
  - `cli.py` for REPL / command loop
- Brainstorm and write down **shared edge cases**:
  - Board sizes: 1×1, 1×N, N×1
  - 0 mines, 1 mine, all mines-but-one
  - Repeated reveals, flags, bad input, etc.
- Decide on **minimum interface** for:
  - `Board` (constructor, reveal, flag, game state)
  - `render_board(board)` or similar
  - CLI commands (e.g., `reveal r c`, `flag r c`, `quit`)
- Make sure each student understands:
  - No code sharing
  - But tests/ideas/edge cases can be shared

**Personal homework after meeting (optional, ~30 min):**
- Sketch your own `Board` class interface and data model.
- Note any questions you want to clarify later.

---

## Tuesday, Nov 25 – Board & Cell Model + Neighbors (1–2 hours)

**Goal:** Have a basic `Board` data structure and a working `neighbors(r, c)` helper.

**Tasks:**
- Implement your own `Cell`/`Tile` representation:
  - Track at least:
    - `is_mine`
    - `adjacent_mines`
    - `revealed`
    - `flagged`
- Implement `Board` with:
  - Stored rows/cols
  - Internal grid (2D list or equivalent)
- Implement `neighbors(r, c)`:
  - Return valid neighbor coordinates around a cell.

**Tests / checks:**
- For a 3×3 board:
  - Center has 8 neighbors.
  - Corners have 3 neighbors.
  - Edges have 5 neighbors.
- Confirm out-of-bounds neighbors are excluded.

---

## Wednesday, Nov 26 – Mine Placement & Adjacent Counts (1–2 hours)

**Goal:** Place mines and compute correct neighbor counts.

**Tasks:**
- Implement mine placement:
  - Use a method like `place_mines(num_mines, rng=None)` or similar.
  - Optionally support a seed for deterministic testing.
- Implement `compute_adjacent_counts()` using `neighbors`.

**Tests / checks:**
- Very small boards:
  - 1×1 with 0 mines.
  - 1×1 with 1 mine.
- A small 2×2 or 3×3 board where you **manually set mines**:
  - Confirm `adjacent_mines` counts are correct for each cell.
- Edge case: 0 mines and “many mines” (dense board).

---

## Thursday, Nov 27 – Basic Reveal Logic (1–2 hours)

**Goal:** Implement non-flood-fill `reveal_cell`.

**Tasks:**
- Implement `reveal_cell(r, c)` for basic cases:
  - If already revealed → no-op.
  - If mine → mark `game_over = True`, `won = False`.
  - If safe → mark cell revealed.
- Add fields on `Board` like:
  - `game_over`
  - `won`

**Tests / checks:**
- Reveal a mine:
  - `game_over` should be True.
- Reveal a non-mine:
  - Cell is marked revealed.
- Revealing same cell twice:
  - No crash, no state corruption.

---

## Friday, Nov 28 – Flood-Fill for Zero Cells (1–2 hours)

**Goal:** Implement recursive/iterative reveal of zero-adjacent cells.

**Tasks:**
- Extend `reveal_cell(r, c)`:
  - If `adjacent_mines == 0`, reveal all neighbors.
  - Use recursion or a queue/stack to avoid duplicates.
- Ensure you track visited cells to avoid infinite loops.

**Tests / checks:**
- Small board with one zero region:
  - Revealing a zero cell reveals its region and bordering number cells.
- Ensure:
  - No infinite recursion.
  - No repeated reveals.
  - Neighbor counts still correct.

---

## Saturday, Nov 29 – Flagging & Win Detection (3–4 hours)

**Goal:** Implement flagging and correct win condition logic.

**Tasks:**
- `toggle_flag(r, c)`:
  - Only allowed if cell is not revealed and game not over.
  - Alternate between flagged / unflagged.
- Win detection:
  - Win when **all non-mine cells** are revealed.
  - Typically checked after each successful reveal.

**Tests / checks:**
- Flag/unflag a cell:
  - State toggles correctly.
- Try flagging a revealed cell:
  - Should be disallowed or ignored per your design.
- Win condition:
  - On a tiny board, reveal all non-mine cells → `won == True`, `game_over == True`.
- Make sure you **don’t require all mines to be flagged** to win (unless the spec says so).

---

## Sunday, Nov 30 – Rendering Layer (3–4 hours)

**Goal:** Implement `render.py` to convert board state into text.

**Tasks:**
- Implement functions like:
  - `render_board(board) -> list[str]` or a single multi-line string.
- Decide how to show:
  - Hidden cells (e.g., `.`)
  - Flagged cells (e.g., `F`)
  - Revealed number cells (`1–8`)
  - Revealed zero cells (blank or `0`)
  - Mines (e.g., `*`) when game is over

**Tests / checks:**
- Snapshot-style expectations for simple boards:
  - A fresh board (no reveals).
  - Board after a few reveals and flags.
  - Board after game over.
- Confirm rendering code has **no game logic**, only formatting.

---

## Monday, Dec 1 – CLI/REPL Skeleton (1–2 hours)

**Goal:** Create the basic command loop in `cli.py`.

**Tasks:**
- Implement a simple loop that:
  - Prints a welcome message.
  - Reads commands like:
    - `reveal r c`
    - `flag r c`
    - `unflag r c` or equivalent
    - `show`
    - `quit`
  - Uses `render_board(board)` to display state.
- Wire CLI commands to `Board` methods.

**Tests / checks (manual):**
- Run a short test game manually via CLI.
- Confirm basic commands behave as expected.

---

## Tuesday, Dec 2 – CLI Robustness & Error Handling (1–2 hours)

**Goal:** Make the CLI resilient and friendly.

**Tasks:**
- Validate input:
  - Correct number of arguments.
  - Integers for row/col.
  - In-range coordinates.
- Handle invalid commands gracefully:
  - Print help or an error message instead of crashing.
- Decide how to handle actions when `game_over` is True.

**Tests / checks (manual + small helpers):**
- Try:
  - Invalid commands (`foo`, `reveal x y`, etc.).
  - Out-of-bounds coordinates.
  - Commands after win/loss.

---

## Wednesday, Dec 3 – Add More Tests & Regression Checks (1–2 hours)

**Goal:** Strengthen unit tests for core behavior.

**Tasks:**
- Add tests in `tests/` for:
  - Neighbor computation (corners, edges).
  - Flood-fill behavior.
  - Win & loss conditions.
  - Flagging rules.
- Capture any bugs found during manual testing and add regression tests.

**Checks:**
- Run `python -m unittest` (or your test runner).
- Fix failing tests or faulty assumptions.

---

## Thursday, Dec 4 – Refactor & Code Cleanup (1–2 hours)

**Goal:** Make the code clean, readable, and grader-friendly.

**Tasks:**
- Review each module:
  - Remove dead/unused code.
  - Improve names and docstrings for tricky methods.
- Ensure:
  - Game logic is in `core/board.py`.
  - `render.py` and `cli.py` don’t contain core rules.

**Checks:**
- Re-run tests after refactoring.
- Ensure package still runs as before.

---

## Friday, Dec 5 – Final Tests & README (2 hours)

**Goal:** Solidify tests and documentation.

**Tasks:**
- Double-check edge-case coverage:
  - Tiny boards (1×1, 1×N, N×1)
  - 0 mines, 1 mine, densely mined boards
  - Repeated reveals / flags
  - Bad CLI input
- Update or write `README.md`:
  - How to install/run.
  - Controls / commands.
  - Brief description of modules.

**Checks:**
- All tests passing.
- README instructions verified by actually running them.

---

## Saturday, Dec 6 – Full Run-Through & Fuzzing (2–3 hours)

**Goal:** Treat the project like an AI grader / picky professor would.

**Tasks:**
- Play several full games:
  - Try to break the game intentionally.
- For each edge case in your checklist:
  - Manually verify behavior is correct and stable.
- Add any last-minute **small** tests where appropriate.

**Checks:**
- No crashes.
- No obviously inconsistent behavior.
- Code still clear and commented.

---

## Sunday, Dec 7 – Submission (1–2 hours)

**Goal:** Package and submit calmly; no big changes.

**Tasks:**
- Final run:
  - `python -m minemind` (or whatever entry point is required).
  - All tests.
- Zip the folder as required, including:
  - Source
  - Tests
  - README
  - Any other required files (e.g., `pyproject.toml`)

**Rule for today:**
- No large refactors or risky changes.
- Only small fixes if something is clearly broken.

---

This schedule is deliberately conservative.  
If you finish early on some days, use that time to:
- Improve tests
- Think of new edge cases
- Improve clarity and comments
- Make the code something you’re proud to show a human *and* an AI grader.
