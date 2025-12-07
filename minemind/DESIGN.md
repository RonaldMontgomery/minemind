# DESIGN

## Architecture
```
+-----------+       +-----------------+       +-----------------+
|  Board    | ----> | Frontier Builder| ----> |  Rule Engines   |
| grid+state|       | (iter/collect)  |       | trivial+subset  |
+-----------+       +-----------------+       +-----------------+
      ^                       |                           |
      |                       v                           v
      |                +--------------+           +---------------+
      |                |  Solver step |           |  CLI (Shell)  |
      |                | aggregates   | <---------+ applies moves |
      |                +--------------+           +---------------+
```
- `Board`: owns cells, mines, revealed/flagged state, win/loss detection.
- `frontier.py`: derives read-only `FrontierCellView` for every revealed numbered cell touching a hidden neighbor.
- `rules.py`: pure logic over frontier views (trivial and subset rules) producing certain moves.
- `solver.py`: orchestrates frontier collection + rule passes, dedupes moves, returns guaranteed actions.
- `cli.py` + `render.py`: user interface and text rendering; shell dispatches to board/solver.

## Invariants
- **DSU (future use)**: parent pointers form forests; `find(x)` returns canonical root; rank/size non-negative; unions only merge distinct sets.
- **Board**:
  - `rows, cols > 0`; `mines` clamped to `[0, rows*cols-1]`.
  - `state` ? {`PLAYING`, `WON`, `LOST`}; monotonic transitions (never revert to PLAYING after win/loss).
  - Mines are placed exactly once on the first reveal; the first clicked cell and its neighbors are mine-free.
  - After `_calculate_neighbor_counts`, each non-mine cell has an accurate `neighbor_mines` equal to adjacent mines.
  - `flag` toggles only on unrevealed cells; reveal never flips a flag.
  - Flood-fill only propagates through zero-count cells; numbered boundaries stop expansion.
- **Solver/frontier**:
  - Frontier cells are revealed, numbered (`neighbor_mines > 0`), and have =1 hidden, unflagged neighbor.
  - For each frontier cell: `remaining_mines = neighbor_mines - flagged_neighbors` (may be negative in test harness setups; rules must tolerate).
  - Returned moves are deterministic, side-effect-free, and deduplicated.

## Data Flow (hint / step / auto)
1. **Snapshot board**: CLI requests a solver step; board remains authoritative state.
2. **Build frontier**: `iter_frontier_cells(board)` yields each frontier cell with hidden/flagged neighbor info.
3. **Rule passes**: trivial rules run per frontier cell; subset rules inspect pairs of frontier views for set relationships.
4. **Produce moves**: moves are collected and deduped as `(row, col, action)`.
5. **Apply**:
   - *hint*: display the move list without mutating the board (not yet implemented, but would reuse the same pipeline).
   - *step*: current `solve` command applies all certain moves once, in order, until the list is exhausted or the game ends.
   - *auto*: would iterate steps until no certain moves remain or game over; could stop early on non-determinism.

## Components / Frontier Diagram
```
Board cells
   +-> FrontierCellView (row, col, hidden_neighbors, flagged_neighbors, remaining_mines)
          +-> Trivial rules (all hidden are mines; all hidden are safe)
          +-> Subset rules (subset diff => safe/mine conclusions)
                  +-> Solver move list (FLAG / REVEAL)
```

## Notes / Gaps
- Probability/guessing, CSP search, and multi-cell pattern libraries are intentionally omitted for determinism and speed.
- Helper modules (`dsu.py`, `lru.py`, `rng.py`, `signatures.py`, `snapshot.py`) are placeholders; no runtime dependency today.
