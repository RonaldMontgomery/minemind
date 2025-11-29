# minemind/core/solver.py

from typing import List, Tuple
from minemind.core.board import Board  # Used for type hinting and access

# Define a move type for clear communication between solver and CLI
SolverMove = Tuple[int, int, str]  # (row, col, 'REVEAL' or 'FLAG')


class MinemindSolver:
    """Implements logical algorithms to solve a Minesweeper board."""

    def __init__(self):
        # Solver initialization (may need to cache patterns later)
        pass

    def _get_frontier_cells(self, board: Board) -> List[Tuple[int, int]]:
        """
        Identifies all revealed, numbered cells that are adjacent to hidden cells.
        These are the only cells the solver needs to analyze.
        """
        frontier_coords: List[Tuple[int, int]] = []

        for r in range(board.rows):
            for c in range(board.cols):
                cell = board.cells[r][c]

                # We are only interested in revealed cells that have a visible count
                if cell.is_revealed and cell.neighbor_mines > 0:
                    # Check if any of its neighbors are hidden (unrevealed AND not flagged)
                    for nr, nc in board._get_neighbors_coords(r, c):
                        neighbor_cell = board.cells[nr][nc]
                        if not neighbor_cell.is_revealed and not neighbor_cell.is_flagged:
                            frontier_coords.append((r, c))
                            # Break out of the inner loop once one hidden neighbor is found
                            break

        return frontier_coords

    def solve_step(self, board: Board) -> List[SolverMove]:
        """
        Finds all logically certain moves (reveals or flags) for one step.

        Implements:
          - Trivial Flag Rule:
              If neighbor_mines - flagged_neighbors == hidden_unflagged_neighbors,
              then all hidden neighbors must be mines -> FLAG them.
          - Trivial Reveal Rule:
              If flagged_neighbors == neighbor_mines,
              then all remaining hidden neighbors are safe -> REVEAL them.
        """
        certain_moves: List[SolverMove] = []
        seen_moves = set()  # to avoid duplicates across overlapping frontiers

        frontier = self._get_frontier_cells(board)

        for r, c in frontier:
            cell = board.cells[r][c]
            n = cell.neighbor_mines

            hidden_neighbors: List[Tuple[int, int]] = []
            flagged_neighbors = 0

            for nr, nc in board._get_neighbors_coords(r, c):
                neighbor = board.cells[nr][nc]
                if neighbor.is_flagged:
                    flagged_neighbors += 1
                elif not neighbor.is_revealed:
                    hidden_neighbors.append((nr, nc))

            if not hidden_neighbors:
                continue

            remaining_mines = n - flagged_neighbors

            # --- Trivial Flag Rule ---
            # All remaining hidden neighbors are mines.
            if remaining_mines == len(hidden_neighbors) and remaining_mines > 0:
                for nr, nc in hidden_neighbors:
                    move = (nr, nc, "FLAG")
                    if move not in seen_moves:
                        seen_moves.add(move)
                        certain_moves.append(move)

            # --- Trivial Reveal Rule ---
            # All hidden neighbors are safe.
            if flagged_neighbors == n:
                for nr, nc in hidden_neighbors:
                    move = (nr, nc, "REVEAL")
                    if move not in seen_moves:
                        seen_moves.add(move)
                        certain_moves.append(move)

        return certain_moves