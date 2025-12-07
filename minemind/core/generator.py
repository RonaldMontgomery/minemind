# minemind/core/generator.py
"""
Board generation helpers for MineMind.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .board import Board


@dataclass(frozen=True)
class BoardConfig:
    """
    Immutable configuration object describing how a new Board should be created.
    """

    difficulty: Optional[str] = None
    rows: Optional[int] = None
    cols: Optional[int] = None
    mines: Optional[int] = None


def new_board(
    *,
    difficulty: str | None = None,
    rows: int | None = None,
    cols: int | None = None,
    mines: int | None = None,
) -> Board:
    """
    Create and return a new Board instance.

    Parameters
    ----------
    difficulty:
        Optional difficulty string such as "beginner", "intermediate", or
        "expert".  If omitted, the Board class will fall back to its default.
    rows, cols:
        Optional explicit dimensions.  When provided, these take precedence
        over the difficulty preset for size (see Board._get_config).
    mines:
        Optional explicit mine count.  When omitted, the Board will compute
        a value based on its DEFAULT_DENSITY.

    Returns
    -------
    Board
        A fully initialized Board in the PLAYING state with no mines placed
        until the first reveal.
    """
    kwargs: dict[str, object] = {}
    if difficulty is not None:
        kwargs["difficulty"] = difficulty
    if rows is not None:
        kwargs["rows"] = rows
    if cols is not None:
        kwargs["cols"] = cols
    if mines is not None:
        kwargs["mines"] = mines

    return Board(**kwargs)


def from_config(config: BoardConfig) -> Board:
    """
    Helper that mirrors :func:`new_board` but accepts a BoardConfig
    instance instead of individual arguments.
    """
    return new_board(
        difficulty=config.difficulty,
        rows=config.rows,
        cols=config.cols,
        mines=config.mines,
    )