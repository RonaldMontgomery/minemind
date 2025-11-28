import math
import unittest

from minemind.core.board import Board, Cell


class TestCellRepr(unittest.TestCase):
    """Additional tests for the Cell dataclass behavior."""

    def test_repr_hidden_unflagged_non_mine(self):
        """A fresh hidden, unflagged non-mine cell should render as '#'."""
        cell = Cell(is_mine=False, is_revealed=False, is_flagged=False, neighbor_mines=0)
        self.assertEqual(repr(cell), "#")

    def test_repr_flagged(self):
        """A flagged cell should render as 'F' when not revealed."""
        cell = Cell(is_mine=False, is_revealed=False, is_flagged=True, neighbor_mines=0)
        self.assertEqual(repr(cell), "F")

    def test_repr_revealed_non_mine(self):
        """A revealed non-mine cell should render its neighbor mine count."""
        cell = Cell(is_mine=False, is_revealed=True, is_flagged=False, neighbor_mines=3)
        self.assertEqual(repr(cell), "3")

    def test_repr_revealed_mine(self):
        """A revealed mine cell should render as 'M'."""
        cell = Cell(is_mine=True, is_revealed=True, is_flagged=False, neighbor_mines=0)
        self.assertEqual(repr(cell), "M")


class TestBoardCustomConfigEdges(unittest.TestCase):
    """Extra tests exercising _get_config edge cases and clamping logic."""

    def test_invalid_difficulty_with_custom_size_uses_custom_and_density(self):
        """
        If difficulty is invalid but rows/cols are provided, the board should
        keep the custom size and compute mines from DEFAULT_DENSITY.
        """
        rows, cols = 8, 12
        board = Board(rows=rows, cols=cols, difficulty="impossible-mode")

        self.assertEqual(board.rows, rows)
        self.assertEqual(board.cols, cols)

        expected_mines = math.floor(rows * cols * Board.DEFAULT_DENSITY)
        # For this size/density we expect no clamping to total_cells - 1.
        self.assertEqual(board.mines, expected_mines)

    def test_valid_difficulty_with_custom_size_prefers_custom_size(self):
        """
        If rows/cols are provided along with a valid difficulty, the custom
        size should win over the standard preset; mines still use density.
        """
        beginner_rows, beginner_cols, _ = Board.STANDARD_CONFIGS["beginner"]
        rows, cols = beginner_rows + 3, beginner_cols + 1

        board = Board(rows=rows, cols=cols, difficulty="beginner")

        self.assertEqual(board.rows, rows)
        self.assertEqual(board.cols, cols)

        expected_mines = math.floor(rows * cols * Board.DEFAULT_DENSITY)
        self.assertEqual(board.mines, expected_mines)

    def test_zero_rows_fall_back_to_default_rows(self):
        """
        rows <= 0 should fall back to the default beginner rows; cols should
        honor the custom value when valid.
        """
        default_rows, default_cols, _ = Board.STANDARD_CONFIGS["beginner"]

        board = Board(rows=0, cols=10)

        self.assertEqual(board.rows, default_rows)
        self.assertEqual(board.cols, 10)

        expected_mines = math.floor(default_rows * 10 * Board.DEFAULT_DENSITY)
        self.assertEqual(board.mines, expected_mines)

        # Also verify columns fallback when invalid but rows are valid.
        board2 = Board(rows=10, cols=-1)
        self.assertEqual(board2.rows, 10)
        self.assertEqual(board2.cols, default_cols)

    def test_only_rows_provided_uses_default_cols(self):
        """
        When only rows is provided, columns should come from the default
        beginner config, and mines come from density.
        """
        default_rows, default_cols, _ = Board.STANDARD_CONFIGS["beginner"]

        custom_rows = default_rows + 5
        board = Board(rows=custom_rows)

        self.assertEqual(board.rows, custom_rows)
        self.assertEqual(board.cols, default_cols)

        expected_mines = math.floor(custom_rows * default_cols * Board.DEFAULT_DENSITY)
        self.assertEqual(board.mines, expected_mines)

    def test_negative_mines_clamped_to_zero(self):
        """Explicit negative mine counts should clamp up to 0."""
        board = Board(rows=6, cols=6, mines=-10)
        self.assertEqual(board.rows, 6)
        self.assertEqual(board.cols, 6)
        self.assertEqual(board.mines, 0)

    def test_zero_mines_allowed(self):
        """Explicitly passing mines=0 should be respected."""
        board = Board(rows=4, cols=4, mines=0)
        self.assertEqual(board.mines, 0)
        self.assertEqual(board.total_cells, 16)

    def test_mines_clamped_to_total_cells_minus_one_for_small_board(self):
        """
        For very small boards, confirm that mines are capped at total_cells - 1
        to avoid an all-mine grid.
        """
        rows, cols = 2, 2
        board = Board(rows=rows, cols=cols, mines=10)
        self.assertEqual(board.total_cells, rows * cols)
        self.assertEqual(board.mines, board.total_cells - 1)


class TestBoardGridState(unittest.TestCase):
    """More detailed checks of the grid and board state."""

    def test_all_cells_initialized_consistently(self):
        """
        On a new board, all cells should be Cell instances with consistent
        default user-facing state (no mines placed yet, unrevealed, unflagged).
        """
        rows, cols = 4, 5
        board = Board(rows=rows, cols=cols)

        self.assertEqual(len(board.cells), rows)
        self.assertEqual(len(board.cells[0]), cols)

        for r in range(rows):
            for c in range(cols):
                cell = board.cells[r][c]
                self.assertIsInstance(cell, Cell)
                self.assertFalse(cell.is_mine)
                self.assertFalse(cell.is_revealed)
                self.assertFalse(cell.is_flagged)
                self.assertIsInstance(cell.neighbor_mines, int)

    def test_total_cells_matches_rows_times_cols_for_custom_board(self):
        """total_cells should equal rows * cols for any custom configuration."""
        rows, cols = 7, 11
        board = Board(rows=rows, cols=cols)
        self.assertEqual(board.total_cells, rows * cols)

    def test_initial_state_is_playing_for_custom_board(self):
        """Custom boards should also start in PLAYING state."""
        board = Board(rows=6, cols=9)
        self.assertEqual(board.state, "PLAYING")


if __name__ == "__main__":
    unittest.main()