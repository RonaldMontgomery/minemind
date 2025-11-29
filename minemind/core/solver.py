# minemind/core/solver.py

from typing import List, Tuple
from minemind.core.board import Board

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

        Additionally prepares data for more advanced subset logic by
        collecting (hidden set, mines_needed) for each frontier cell,
        and then running _find_subset_deductions.
        """
        certain_moves: List[SolverMove] = []
        seen_moves = set()  # to avoid duplicates across overlapping frontiers

        # New structure to hold all relevant data for each frontier cell
        # Format (per entry):
        # {
        #   'r': int,
        #   'c': int,
        #   'mines_needed': int,
        #   'hidden_coords': set[(row, col)]
        # }
        frontier_data = []

        for r, c in self._get_frontier_cells(board):
            cell = board.cells[r][c]

            # --- Collection of State ---
            hidden_coords = set()
            flagged_count = 0

            for nr, nc in board._get_neighbors_coords(r, c):
                neighbor = board.cells[nr][nc]
                if neighbor.is_flagged:
                    flagged_count += 1
                elif not neighbor.is_revealed:
                    hidden_coords.add((nr, nc))

            if not hidden_coords:
                continue

            remaining_mines = cell.neighbor_mines - flagged_count

            # --- Trivial Rules Check (using the new variables) ---
            cell_generated_move = False

            # Trivial Flag Rule: all remaining hidden neighbors are mines
            if remaining_mines == len(hidden_coords) and remaining_mines > 0:
                for nr, nc in hidden_coords:
                    move = (nr, nc, "FLAG")
                    if move not in seen_moves:
                        seen_moves.add(move)
                        certain_moves.append(move)
                        cell_generated_move = True

            # Trivial Reveal Rule: all hidden neighbors are safe
            if flagged_count == cell.neighbor_mines:
                for nr, nc in hidden_coords:
                    move = (nr, nc, "REVEAL")
                    if move not in seen_moves:
                        seen_moves.add(move)
                        certain_moves.append(move)
                        cell_generated_move = True

            # Store data for advanced comparison (subset rule, etc.)
            # We *always* collect it; seen_moves prevents duplicates later.
            frontier_data.append({
                "r": r,
                "c": c,
                "mines_needed": remaining_mines,
                "hidden_coords": hidden_coords,
            })

        # --- Subsets and Advanced Logic (T5 and beyond) ---
        self._find_subset_deductions(board, frontier_data, certain_moves, seen_moves)

        return certain_moves

    def _find_subset_deductions(
        self,
        board: Board,
        frontier_data: List[dict],
        certain_moves: List[SolverMove],
        seen_moves: set,
    ) -> None:
        """
        Applies the classic subset rule between frontier cells:

        For two frontier cells A and B with:
          - hidden sets HA and HB
          - mines needed a and b (mines_needed)

        If HA ⊆ HB, then:
          - Let D = HB \ HA and extra_mines = b - a.

          Case 1: extra_mines == 0:
              All cells in D are safe -> REVEAL them.

          Case 2: extra_mines == |D|:
              All cells in D are mines -> FLAG them.

        This can deduce new information that the trivial per-cell rules cannot.
        """
        n = len(frontier_data)
        if n < 2:
            return

        for i in range(n):
            A = frontier_data[i]
            hiddenA = A["hidden_coords"]
            minesA = A["mines_needed"]

            if not hiddenA:
                continue

            for j in range(n):
                if i == j:
                    continue

                B = frontier_data[j]
                hiddenB = B["hidden_coords"]
                minesB = B["mines_needed"]

                if not hiddenB:
                    continue

                # We only care about true subset/superset relationships
                if not hiddenA.issubset(hiddenB):
                    continue

                diff = hiddenB - hiddenA
                if not diff:
                    # No extra cells to deduce anything about
                    continue

                extra_mines = minesB - minesA
                if extra_mines < 0:
                    # Inconsistent info, ignore this pair
                    continue

                # Case 1: extra_mines == 0 -> all cells in diff are safe
                if extra_mines == 0:
                    for (r, c) in diff:
                        cell = board.cells[r][c]
                        if cell.is_revealed or cell.is_flagged:
                            continue
                        move = (r, c, "REVEAL")
                        if move not in seen_moves:
                            seen_moves.add(move)
                            certain_moves.append(move)

                # Case 2: extra_mines == |diff| -> all cells in diff are mines
                elif extra_mines == len(diff):
                    for (r, c) in diff:
                        cell = board.cells[r][c]
                        if cell.is_revealed or cell.is_flagged:
                            continue
                        move = (r, c, "FLAG")
                        if move not in seen_moves:
                            seen_moves.add(move)
                            certain_moves.append(move)