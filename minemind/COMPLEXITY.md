# COMPLEXITY

Let R = rows, C = cols, N = R*C cells, F = frontier cells, k = hidden neighbors per frontier cell (= 8 in standard grids).

## Core Operations
- **Open / reveal**: O(1) to validate + mark; triggers flood-fill when neighbor count is 0.
- **Flood-fill**: O(H) where H is the number of cells revealed in the zero-region (bounded by N); neighbor lookups are O(1) each.
- **Build frontier** (`iter_frontier_cells`): O(N * deg) ˜ O(N) with constant-degree (=8) neighbor scans.
- **Rule pass (trivial rules)**: O(F * k) to inspect each frontier cell and its hidden set.
- **Subset pass**: O(F^2 * k) pairwise subset checks; hidden sets are small so k is a tight constant (=8).
- **Enumeration (if extended)**: worst-case O(S 2^{k_i}) over frontier cells; capped by `k_max` to avoid explosion.

## k_max Choice
If full combinational enumeration is added, cap unknowns per constraint with `k_max = 20`. Rationale:
- 2^20 ˜ 1,048,576 cases is a practical upper bound for occasional heavy cells on modern machines.
- Typical frontier sets in Minesweeper are much smaller (=8), so the cap rarely binds; when it does, it prevents solver stalls.
- Keeps memory and CPU bounded for automated runs while still covering realistic puzzles.
