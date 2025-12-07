# minemind/core/solver.py

"""
Solver logic for Minemind.

This module exposes a single public entry point:

    MinemindSolver.solve_step(board) -> list[(row, col, action)]

where action is either "FLAG" or "REVEAL".

Implemented reasoning:

- T1: Trivial Flag Rule (all remaining hidden neighbors are mines).
- T2: Trivial Reveal Rule (all remaining hidden neighbors are safe).
- T3: No-certainty case (returns []).
- T4: Seen-moves de-duplication across overlapping frontiers.
- T5/T6: Simple 2-cell subset logic:

    Let H(A), H(B) be sets of hidden neighbors of frontier cells A, B.
    Let mA, mB be remaining mines around A, B after accounting for flags.

    1. If H(A) ⊂ H(B) and mA == mB:
           All cells in H(B) \ H(A) are safe → REVEAL.

    2. If H(A) ⊂ H(B) and mB - mA == |H(B) \ H(A)| > 0:
           All cells in H(B) \ H(A) are mines → FLAG.
"""

from __future__ import annotations

from typing import Iterable, List, Tuple, Dict, Set

from .board import Board, Cell

# A single solver move: (row, col, action) where action in {"FLAG", "REVEAL"}.
SolverMove = Tuple[int, int, str]


class MinemindSolver:
    """Stateless one-step Minesweeper solver."""

    @staticmethod
    def _get_frontier_cells(board: Board) -> Iterable[Tuple[int, int]]:
        """
        Yield coordinates of all 'frontier' numbered cells.

        A frontier cell is:
          - revealed
          - not a mine
          - neighbor_mines > 0
          - and has at least one hidden neighbor
        """
        for r in range(board.rows):
            for c in range(board.cols):
                cell: Cell = board.cells[r][c]

                if not cell.is_revealed:
                    continue
                if cell.is_mine:
                    continue
                if cell.neighbor_mines <= 0:
                    continue

                neighbors = board._get_neighbors_coords(r, c)
                if any(not board.cells[nr][nc].is_revealed for (nr, nc) in neighbors):
                    yield (r, c)

    def _apply_subset_logic(
        self,
        frontier_data: List[Dict[str, object]],
        certain_moves: List[SolverMove],
        seen_moves: Set[SolverMove],
    ) -> None:
        """
        Apply a simple 2-cell subset rule over the frontier.

        For any pair of frontier cells A and B with hidden neighbor sets H(A),
        H(B) and remaining mines mA, mB we use two cases:

          1. If H(A) ⊂ H(B) and mB == mA:
                 All cells in H(B) \\ H(A) are safe → REVEAL.

          2. If H(A) ⊂ H(B) and mB - mA == |H(B) \\ H(A)| > 0:
                 All cells in H(B) \\ H(A) are mines → FLAG.
        """
        n = len(frontier_data)
        for i in range(n):
            A = frontier_data[i]
            hiddenA: Set[Tuple[int, int]] = A["hidden_coords"]  # type: ignore[index]
            mA: int = A["mines_needed"]  # type: ignore[index]

            if not hiddenA:
                continue

            for j in range(n):
                if i == j:
                    continue

                B = frontier_data[j]
                hiddenB: Set[Tuple[int, int]] = B["hidden_coords"]  # type: ignore[index]
                mB: int = B["mines_needed"]  # type: ignore[index]

                if not hiddenB:
                    continue

                # We only care about *strict* subset relations.
                if not (hiddenA < hiddenB):
                    continue

                diff = hiddenB - hiddenA
                if not diff:
                    continue

                extra_mines = mB - mA

                # Case 1: same remaining mine count → diff must be all safe.
                if extra_mines == 0:
                    for (r, c) in diff:
                        move: SolverMove = (r, c, "REVEAL")
                        if move not in seen_moves:
                            certain_moves.append(move)
                            seen_moves.add(move)
                    continue

                # Case 2: all extra mines must live in the diff set.
                if extra_mines == len(diff) and extra_mines > 0:
                    for (r, c) in diff:
                        move = (r, c, "FLAG")
                        if move not in seen_moves:
                            certain_moves.append(move)
                            seen_moves.add(move)

    # ----- Public API --------

    def solve_step(self, board: Board) -> List[SolverMove]:
        """
        Compute a single batch of logically forced moves on the given board.

        Returns:
            A list of (row, col, action) tuples, where action is "FLAG" or
            "REVEAL". If no certain deduction is possible, returns [].
        """
        certain_moves: List[SolverMove] = []
        seen_moves: Set[SolverMove] = set()

        frontier_data: List[Dict[str, object]] = []

        # First pass: trivial rules and frontier summary.
        for (r, c) in self._get_frontier_cells(board):
            cell = board.cells[r][c]
            n_mines = cell.neighbor_mines

            hidden_coords: Set[Tuple[int, int]] = set()
            flagged_count = 0

            # Classify neighbors of this frontier cell.
            for (nr, nc) in board._get_neighbors_coords(r, c):
                neighbor = board.cells[nr][nc]
                if neighbor.is_flagged:
                    flagged_count += 1
                elif not neighbor.is_revealed:
                    # hidden & unflagged
                    hidden_coords.add((nr, nc))

            if not hidden_coords:
                # Nothing unknown around this frontier cell.
                continue

            remaining_mines = n_mines - flagged_count

            # All remaining hidden neighbors must be mines.
            if remaining_mines == len(hidden_coords) and remaining_mines > 0:
                for (nr, nc) in hidden_coords:
                    move: SolverMove = (nr, nc, "FLAG")
                    if move not in seen_moves:
                        certain_moves.append(move)
                        seen_moves.add(move)

            # All remaining hidden neighbors must be safe.
            if remaining_mines == 0:
                for (nr, nc) in hidden_coords:
                    move = (nr, nc, "REVEAL")
                    if move not in seen_moves:
                        certain_moves.append(move)
                        seen_moves.add(move)

            # Record summary for possible subset checks later.
            frontier_data.append(
                {
                    "coord": (r, c),
                    "hidden_coords": hidden_coords,
                    "mines_needed": remaining_mines,
                }
            )

        # If we got any trivial moves, return them immediately
        if certain_moves:
            return certain_moves

        # Otherwise, attempt a single round of subset reasoning
        self._apply_subset_logic(frontier_data, certain_moves, seen_moves)

        # Either we found subset moves, or still nothing -> [].
        return certain_moves