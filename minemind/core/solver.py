# minemind/core/solver.py

from typing import List, Tuple, Dict, Set
from minemind.core.board import Board  # Used for type hinting and access

# Define a move type for clear communication between solver and CLI
SolverMove = Tuple[int, int, str]  # (row, col, 'REVEAL' or 'FLAG')


class MinemindSolver:
    """Implements logical algorithms to solve a Minesweeper board."""

    def __init__(self) -> None:
        # Placeholder for later caching / parameters
        pass

    # ------------------------------------------------------------------
    # Frontier discovery
    # ------------------------------------------------------------------
    def _get_frontier_cells(self, board: Board) -> List[Tuple[int, int]]:
        """
        Identifies all revealed, numbered cells that are adjacent to hidden cells.
        These are the only cells the solver needs to analyze.
        """
        frontier_coords: List[Tuple[int, int]] = []

        for r in range(board.rows):
            for c in range(board.cols):
                cell = board.cells[r][c]

                # Only revealed, numbered cells are interesting
                if cell.is_revealed and cell.neighbor_mines > 0:
                    # Check if any neighbor is hidden & not flagged
                    for nr, nc in board._get_neighbors_coords(r, c):
                        neighbor = board.cells[nr][nc]
                        if not neighbor.is_revealed and not neighbor.is_flagged:
                            frontier_coords.append((r, c))
                            break  # one hidden neighbor is enough to mark as frontier

        return frontier_coords

    # ------------------------------------------------------------------
    # Subset logic (T5–T6)
    # ------------------------------------------------------------------
    def _apply_subset_logic(
        self,
        frontier_data: List[Dict],
        certain_moves: List[SolverMove],
        seen_moves: Set[SolverMove],
    ) -> None:
        """
        Applies subset-based deductions:

          Let A and B be two frontier cells with:
            Hidden(A), Hidden(B) = sets of hidden neighbors
            mA, mB = remaining mines around each

          1. If Hidden(A) ⊂ Hidden(B) and mA == mB:
               Hidden(B) \ Hidden(A) must be safe → REVEAL.

          2. If Hidden(A) ⊂ Hidden(B) and mB - mA == |Hidden(B) \ Hidden(A)| > 0:
               All cells in Hidden(B) \ Hidden(A) are mines → FLAG.
        """
        n = len(frontier_data)
        for i in range(n):
            A = frontier_data[i]
            hiddenA: Set[Tuple[int, int]] = A["hidden_coords"]
            mA: int = A["mines_needed"]

            if not hiddenA:
                continue

            for j in range(n):
                if i == j:
                    continue

                B = frontier_data[j]
                hiddenB: Set[Tuple[int, int]] = B["hidden_coords"]
                mB: int = B["mines_needed"]

                if not hiddenB:
                    continue

                # We only care about proper subsets
                if not hiddenA < hiddenB:
                    continue

                diff = hiddenB - hiddenA
                if not diff:
                    continue

                # Case 1: same remaining mines -> diff must be safe
                if mA == mB:
                    for (r, c) in diff:
                        move: SolverMove = (r, c, "REVEAL")
                        if move not in seen_moves:
                            seen_moves.add(move)
                            certain_moves.append(move)

                # Case 2: extra mines exactly fill the difference set
                else:
                    extra = mB - mA
                    if extra > 0 and extra == len(diff):
                        for (r, c) in diff:
                            move = (r, c, "FLAG")
                            if move not in seen_moves:
                                seen_moves.add(move)
                                certain_moves.append(move)

    # ------------------------------------------------------------------
    # Main solving step
    # ------------------------------------------------------------------
    def solve_step(self, board: Board) -> List[SolverMove]:
        """
        Finds all logically certain moves (reveals or flags) for one step.

        Implements:
          - Trivial Flag Rule:
              If neighbor_mines - flagged_neighbors == hidden_unflagged_neighbors > 0,
              then all hidden neighbors must be mines → FLAG them.
          - Trivial Reveal Rule:
              If flagged_neighbors == neighbor_mines,
              then all remaining hidden neighbors are safe → REVEAL them.
          - Subset Rule (via _apply_subset_logic).
        """
        certain_moves: List[SolverMove] = []
        seen_moves: Set[SolverMove] = set()

        # Collect per-frontier data for possible subset deductions
        frontier_data: List[Dict] = []

        for r, c in self._get_frontier_cells(board):
            cell = board.cells[r][c]
            n_mines = cell.neighbor_mines

            hidden_coords: Set[Tuple[int, int]] = set()
            flagged_count = 0

            # Collect neighbors
            for nr, nc in board._get_neighbors_coords(r, c):
                neighbor = board.cells[nr][nc]
                if neighbor.is_flagged:
                    flagged_count += 1
                elif not neighbor.is_revealed:
                    # hidden & not flagged
                    hidden_coords.add((nr, nc))

            if not hidden_coords:
                continue

            remaining_mines = n_mines - flagged_count

            # --- Trivial Flag Rule ---
            # All remaining hidden neighbors are mines.
            if remaining_mines == len(hidden_coords) and remaining_mines > 0:
                for (nr, nc) in hidden_coords:
                    move: SolverMove = (nr, nc, "FLAG")
                    if move not in seen_moves:
                        seen_moves.add(move)
                        certain_moves.append(move)

            # --- Trivial Reveal Rule ---
            # All hidden neighbors are safe.
            if flagged_count == n_mines and hidden_coords:
                for (nr, nc) in hidden_coords:
                    move = (nr, nc, "REVEAL")
                    if move not in seen_moves:
                        seen_moves.add(move)
                        certain_moves.append(move)

            # Save data for subset logic (even if trivial rules produced moves)
            if remaining_mines >= 0:
                frontier_data.append(
                    {
                        "r": r,
                        "c": c,
                        "hidden_coords": hidden_coords,
                        "mines_needed": remaining_mines,
                    }
                )

        # Apply subset-based deductions (T5–T6)
        if frontier_data:
            self._apply_subset_logic(frontier_data, certain_moves, seen_moves)

        return certain_moves