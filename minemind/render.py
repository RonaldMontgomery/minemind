# minemind/render.py
# Renderer logic for MineMind CLI.
#
# This module is read-only with respect to the game state: it only inspects
# the Board and Cell data and prints a textual representation.

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # for type checkers only; avoids runtime import cycles
    from minemind.core.board import Board, Cell


def _get_cell_char(cell, board_state: str, show_mines: bool) -> str:
    """
    Returns the single character symbol for a cell.

    Conventions:
      - Revealed non-mine: '.' for 0, or '1'..'8' for neighbor counts
      - Revealed mine: 'M'
      - Hidden, flagged (during play): 'F'
      - Hidden, unflagged: '#'
      - After game over (show_mines=True):
          * All mines visible as 'M'
          * Incorrect flags (flagged but not mine) shown as 'X'
    """
    # Revealed cells
    if cell.is_revealed:
        if cell.is_mine:
            return "M"
        return str(cell.neighbor_mines) if cell.neighbor_mines > 0 else "."

    # Hidden cells during play / after game
    if cell.is_flagged:
        # If the game is over, distinguish incorrect flags for clarity
        if show_mines and not cell.is_mine:
            return "X"  # wrong flag
        return "F"      # correct flag or still playing

    # If game is over and we need to show unflagged mines
    if show_mines and cell.is_mine:
        return "M"  # show all mines when game is over

    return "#"  # Default hidden state


def display_board(board):
    """Prints the current state of the board to the console."""
    show_all_mines = board.state != "PLAYING"
    rows, cols = board.rows, board.cols

    output = []

    # 1. Print Column Indices (Header)
    col_header = "    " + " ".join(str(c).ljust(2) for c in range(cols))
    output.append(col_header)
    output.append("   " + "---" * cols)

    # 2. Print Rows and Cells
    for r in range(rows):
        row_str = f"{str(r).ljust(2)}| "

        for c in range(cols):
            cell = board.cells[r][c]
            char = _get_cell_char(cell, board.state, show_all_mines)
            row_str += char.ljust(2) + " " 

        output.append(row_str.rstrip())

    print("\n".join(output))