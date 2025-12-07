# minemind/core/frontier.py
"""
Frontier utilities for MineMind.

A frontier is the set of revealed numbered cells that are adjacent to at
least one hidden (unrevealed and unflagged) cell.  These cells are the only
places where the solver can extract new information about the unknown region.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Iterator, List, Set, Tuple

from .board import Board, Cell

Coord = Tuple[int, int]


@dataclass(frozen=True)
class FrontierCellView:
    """
    Read-only view of a single frontier cell.

    Attributes
    ----------
    row, col:
        Coordinates of the numbered cell on the board.
    hidden_neighbors:
        Set of coordinates of neighboring cells that are currently hidden
        (unrevealed and not flagged).
    flagged_neighbors:
        Number of neighboring cells that are currently flagged.
    remaining_mines:
        How many mines must still be present in ``hidden_neighbors`` in order
        for the numbered cell's constraint to be satisfied.  This is defined as

            remaining_mines = cell.neighbor_mines - flagged_neighbors

        and can be negative in deliberately broken test setups; callers are
        expected to handle that gracefully.
    """

    row: int
    col: int
    hidden_neighbors: Set[Coord]
    flagged_neighbors: int
    remaining_mines: int


def iter_frontier_cells(board: Board) -> Iterator[FrontierCellView]:
    """
    Yield a :class:`FrontierCellView` for every revealed numbered cell that has
    at least one hidden neighbor.

    Notes
    -----
    * A cell is considered a frontier cell if:
        - it is revealed,
        - it has ``neighbor_mines > 0``, and
        - at least one neighbor is hidden (unrevealed and not flagged).
    * This function does not mutate the board.
    """
    rows, cols = board.rows, board.cols

    for r in range(rows):
        for c in range(cols):
            cell: Cell = board.cells[r][c]

            if not cell.is_revealed or cell.neighbor_mines <= 0:
                continue

            hidden: Set[Coord] = set()
            flagged_count = 0

            for nr, nc in board._get_neighbors_coords(r, c):
                neighbor = board.cells[nr][nc]
                if neighbor.is_flagged:
                    flagged_count += 1
                elif not neighbor.is_revealed:
                    hidden.add((nr, nc))

            # Only yield cells that actually border at least one hidden cell.
            if not hidden:
                continue

            remaining = cell.neighbor_mines - flagged_count

            yield FrontierCellView(
                row=r,
                col=c,
                hidden_neighbors=hidden,
                flagged_neighbors=flagged_count,
                remaining_mines=remaining,
            )


def collect_frontier(board: Board) -> List[FrontierCellView]:
    """
    Return the entire frontier in a list.
    """
    return list(iter_frontier_cells(board))