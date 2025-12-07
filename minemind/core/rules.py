# minemind/core/rules.py
"""
Logical rules for Minesweeper solving.

The project handout describes several families of rules:

* Trivial Flag rule:
    If all remaining hidden neighbors of a numbered cell must be mines,
    then those neighbors can be safely flagged.

* Trivial Reveal rule:
    If all mines around a numbered cell have already been flagged, then all
    remaining hidden neighbors of that cell are safe and can be revealed.

* Subset rules:
    When two frontier cells share a related hidden region, the smaller
    (subset) constraint can sometimes be used to deduce information about
    the extra cells in the larger set.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Set, Tuple

from .board import Board
from .frontier import FrontierCellView, Coord

# A solver move is always (row, col, action) where action is "REVEAL" or "FLAG".
SolverMove = Tuple[int, int, str]


@dataclass(frozen=True)
class RuleContext:
    """
    Small container bundling a board together with the frontier views that a
    rule function is allowed to inspect.
    """

    board: Board
    frontier: Iterable[FrontierCellView]


def apply_trivial_rules(ctx: RuleContext) -> List[SolverMove]:
    """
    Apply the two basic Minesweeper rules to all frontier cells in ``ctx`` and
    return a list of logically certain moves.
    """
    moves: List[SolverMove] = []
    seen: Set[SolverMove] = set()

    for fv in ctx.frontier:
        hidden = fv.hidden_neighbors
        if not hidden:
            continue

        # Rule 1: all remaining hidden neighbors are mines.
        if fv.remaining_mines == len(hidden) and fv.remaining_mines > 0:
            for (r, c) in hidden:
                move = (r, c, "FLAG")
                if move not in seen:
                    seen.add(move)
                    moves.append(move)

        # Rule 2: no remaining mines; all hidden neighbors are safe.
        if fv.remaining_mines == 0:
            for (r, c) in hidden:
                move = (r, c, "REVEAL")
                if move not in seen:
                    seen.add(move)
                    moves.append(move)

    return moves


def apply_subset_rules(ctx: RuleContext) -> List[SolverMove]:
    """
    Apply simple subset-based deductions across pairs of frontier cells.
    """
    frontier_list = list(ctx.frontier)
    moves: List[SolverMove] = []
    seen: Set[SolverMove] = set()

    n = len(frontier_list)
    for i in range(n):
        A = frontier_list[i]
        HA = A.hidden_neighbors
        mA = A.remaining_mines

        if not HA:
            continue

        for j in range(i + 1, n):
            B = frontier_list[j]
            HB = B.hidden_neighbors
            mB = B.remaining_mines

            if not HB:
                continue

            # Check both directions: HA ⊂ HB and HB ⊂ HA.
            for smaller, larger, m_small, m_large in (
                (HA, HB, mA, mB),
                (HB, HA, mB, mA),
            ):
                if not smaller or smaller == larger:
                    continue

                if not smaller.issubset(larger):
                    continue

                diff = larger - smaller
                if not diff:
                    continue

                extra_mines = m_large - m_small

                # Case 1: same number of remaining mines → extras are safe.
                if m_small == m_large:
                    for (r, c) in diff:
                        move = (r, c, "REVEAL")
                        if move not in seen:
                            seen.add(move)
                            moves.append(move)

                # Case 2: all extra cells must be mines.
                if extra_mines == len(diff) and extra_mines > 0:
                    for (r, c) in diff:
                        move = (r, c, "FLAG")
                        if move not in seen:
                            seen.add(move)
                            moves.append(move)

    return moves