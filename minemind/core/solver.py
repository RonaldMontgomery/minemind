# minemind/core/solver.py

from __future__ import annotations

from typing import List, Tuple, Dict, Set
from minemind.core.board import Board, Cell  # type: ignore[import]

# (row, col, action), where action is "REVEAL" or "FLAG"
SolverMove = Tuple[int, int, str]


class MinemindSolver:
    """
    Implements basic logical algorithms to solve a Minesweeper board.

    Rules implemented:

      1. Trivial Flag Rule
         For a revealed numbered cell C:

             neighbor_mines = C.neighbor_mines
             F  = number of flagged neighbors
             H  = set of hidden, unflagged neighbors

         If neighbor_mines - F == len(H) and > 0:
             All cells in H are mines → FLAG.

      2. Trivial Reveal Rule
         If F == neighbor_mines:
             All cells in H are safe → REVEAL.

      3. Subset Rules (using a frontier of numbered cells)
         For two frontier cells A and B with:

             H(A) = hidden neighbors of A
             H(B) = hidden neighbors of B
             mA   = mines still needed for A
             mB   = mines still needed for B

         We use:

           - Safe difference (subset reveal):
               If H(A) ⊂ H(B) and mA == mB:
                 All cells in H(B) - H(A) are safe → REVEAL.

           - Mine difference (subset flag):
               If H(A) ⊂ H(B) and mB - mA == |H(B) - H(A)| > 0:
                 All cells in H(B) - H(A) are mines → FLAG.

    All moves are deduplicated via a seen_moves set.
    """

    # ----- Frontier helpers -----

    def _get_frontier_cells(self, board: Board) -> List[Tuple[int, int]]:
        """
        Identifies revealed, numbered cells that have at least one hidden
        (unrevealed and unflagged) neighbor. Those are the only cells the
        solver needs to analyze.
        """
        frontier: List[Tuple[int, int]] = []

        for r in range(board.rows):
            for c in range(board.cols):
                cell = board.cells[r][c]

                # Only consider revealed numbered cells
                if not cell.is_revealed or cell.neighbor_mines <= 0:
                    continue

                # Check if it has any hidden, unflagged neighbor
                has_hidden = False
                for nr, nc in board._get_neighbors_coords(r, c):
                    n_cell = board.cells[nr][nc]
                    if not n_cell.is_revealed and not n_cell.is_flagged:
                        has_hidden = True
                        break

                if has_hidden:
                    frontier.append((r, c))

        return frontier

    # ------------------------------------------------------------------ #
    # Core solving step
    # ------------------------------------------------------------------ #

    def solve_step(self, board: Board) -> List[SolverMove]:
        """
        Finds all logically certain moves (REVEAL or FLAG) for one step.

        Returns a list of (row, col, action) tuples.
        """
        certain_moves: List[SolverMove] = []
        seen_moves: Set[SolverMove] = set()

        frontier = self._get_frontier_cells(board)

        # Collect per-frontier-cell data for subset logic
        frontier_data: List[Dict] = []

        for r, c in frontier:
            cell = board.cells[r][c]
            n = cell.neighbor_mines

            hidden_neighbors: List[Tuple[int, int]] = []
            flagged_neighbors = 0

            # Classify neighbors
            for nr, nc in board._get_neighbors_coords(r, c):
                neighbor = board.cells[nr][nc]
                if neighbor.is_flagged:
                    flagged_neighbors += 1
                elif not neighbor.is_revealed:
                    hidden_neighbors.append((nr, nc))

            if not hidden_neighbors:
                # Nothing interesting around this cell
                continue

            remaining_mines = n - flagged_neighbors

            # --- Trivial Flag Rule ---
            # If all remaining hidden neighbors must be mines.
            if remaining_mines == len(hidden_neighbors) and remaining_mines > 0:
                for nr, nc in hidden_neighbors:
                    move = (nr, nc, "FLAG")
                    if move not in seen_moves:
                        seen_moves.add(move)
                        certain_moves.append(move)

            # --- Trivial Reveal Rule ---
            # If all mines are already flagged, remaining hidden are safe.
            if flagged_neighbors == n:
                for nr, nc in hidden_neighbors:
                    move = (nr, nc, "REVEAL")
                    if move not in seen_moves:
                        seen_moves.add(move)
                        certain_moves.append(move)

            # Store data for subset logic if there are still unknowns around
            if hidden_neighbors:
                frontier_data.append(
                    {
                        "r": r,
                        "c": c,
                        "hidden_coords": set(hidden_neighbors),
                        "remaining_mines": remaining_mines,
                    }
                )

        # Apply subset-based deductions (T5–T7)
        self._apply_subset_logic(frontier_data, certain_moves, seen_moves)

        return certain_moves

    # ----- Subset logic -----

    def _apply_subset_logic(
        self,
        frontier_data: List[Dict],
        certain_moves: List[SolverMove],
        seen_moves: Set[SolverMove],
    ) -> None:
        """
        Inspect pairs of frontier cells to find subset relationships
        between their hidden neighbor sets and deduce additional flags
        or reveals.
        """
        n = len(frontier_data)
        if n < 2:
            return

        for i in range(n):
            A = frontier_data[i]
            H_a: Set[Tuple[int, int]] = A["hidden_coords"]
            m_a: int = A["remaining_mines"]

            # If A's constraints are already impossible or trivial, skip it
            if m_a < 0 or not H_a:
                continue

            for j in range(n):
                if i == j:
                    continue

                B = frontier_data[j]
                H_b: Set[Tuple[int, int]] = B["hidden_coords"]
                m_b: int = B["remaining_mines"]

                if m_b < 0 or not H_b:
                    continue

                if not H_a < H_b:
                    continue

                diff = H_b - H_a
                if not diff:
                    continue

                extra_mines = m_b - m_a

                # Case 1: Same remaining mines but a larger hidden set => diff is safe
                #   H(A) ⊂ H(B) and mA == mB → cells in diff are safe (REVEAL).
                if extra_mines == 0:
                    for r, c in diff:
                        move = (r, c, "REVEAL")
                        if move not in seen_moves:
                            seen_moves.add(move)
                            certain_moves.append(move)

                # Case 2: Extra mines exactly fill the difference set => diff all mines
                #   H(A) ⊂ H(B) and mB - mA == |diff| > 0 → cells in diff are mines (FLAG).
                elif extra_mines == len(diff) and extra_mines > 0:
                    for r, c in diff:
                        move = (r, c, "FLAG")
                        if move not in seen_moves:
                            seen_moves.add(move)
                            certain_moves.append(move)