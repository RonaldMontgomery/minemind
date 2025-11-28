import math
import unittest

from minemind.core.board import Board, Cell


class TestCellDefaults(unittest.TestCase):
    """Tests for the Cell dataclass default state."""

    def test_cell_initial_state(self):
        """A new Cell should have the documented default properties."""
        cell = Cell()
        self.assertFalse(cell.is_mine)
        self.assertFalse(cell.is_revealed)
        self.assertFalse(cell.is_flagged)
        self.assertEqual(cell.neighbor_mines, 0)

    def test_cell_repr_is_safe_and_string(self):
        """__repr__ should return a string (used in board display)."""
        cell = Cell()
        rep = repr(cell)
        self.assertIsInstance(rep, str)
        # For now we only assert it's non-empty; format can change later
        self.assertNotEqual(rep, "")


class TestBoardStandardConfigs(unittest.TestCase):
    """Tests that standard difficulty presets map correctly to rows/cols/mines."""

    def test_beginner_defaults(self):
        """Board() and Board(difficulty='beginner') should match STANDARD_CONFIGS."""
        rows, cols, mines = Board.STANDARD_CONFIGS["beginner"]

        b_default = Board()
        self.assertEqual((b_default.rows, b_default.cols, b_default.mines),
                         (rows, cols, mines))

        b_beginner = Board(difficulty="beginner")
        self.assertEqual((b_beginner.rows, b_beginner.cols, b_beginner.mines),
                         (rows, cols, mines))

    def test_intermediate_defaults(self):
        rows, cols, mines = Board.STANDARD_CONFIGS["intermediate"]
        b = Board(difficulty="intermediate")
        self.assertEqual((b.rows, b.cols, b.mines), (rows, cols, mines))

    def test_expert_defaults(self):
        rows, cols, mines = Board.STANDARD_CONFIGS["expert"]
        b = Board(difficulty="expert")
        self.assertEqual((b.rows, b.cols, b.mines), (rows, cols, mines))

    def test_invalid_difficulty_falls_back_to_beginner_when_no_custom_size(self):
        """Invalid difficulty with no rows/cols should fall back to beginner config."""
        default_rows, default_cols, default_mines = Board.STANDARD_CONFIGS["beginner"]
        b = Board(difficulty="not-a-real-diff")
        self.assertEqual((b.rows, b.cols, b.mines),
                         (default_rows, default_cols, default_mines))


class TestBoardCustomConfigs(unittest.TestCase):
    """Tests for custom row/col/mines behavior and DEFAULT_DENSITY logic."""

    def test_custom_size_with_no_mines_uses_default_density(self):
        """rows/cols specified, mines=None → mines = floor(rows*cols*DEFAULT_DENSITY)."""
        rows, cols = 10, 10
        expected_mines = math.floor(rows * cols * Board.DEFAULT_DENSITY)

        b = Board(rows=rows, cols=cols)
        self.assertEqual((b.rows, b.cols), (rows, cols))
        self.assertEqual(b.mines, expected_mines)

    def test_small_custom_board_density_example(self):
        """Sanity check for a small board (5x5)."""
        rows, cols = 5, 5
        expected_mines = math.floor(rows * cols * Board.DEFAULT_DENSITY)
        b = Board(rows=rows, cols=cols)
        self.assertEqual((b.rows, b.cols), (rows, cols))
        self.assertEqual(b.mines, expected_mines)

    def test_invalid_rows_cols_fall_back_to_defaults(self):
        """
        rows/cols that are not positive integers should fall back to the default
        beginner dimensions (per _get_config logic).
        """
        default_rows, default_cols, default_mines = Board.STANDARD_CONFIGS["beginner"]

        # rows <= 0
        b1 = Board(rows=0, cols=10)
        self.assertEqual((b1.rows, b1.cols), (default_rows, 10))

        # cols <= 0
        b2 = Board(rows=10, cols=0)
        self.assertEqual((b2.rows, b2.cols), (10, default_cols))

        # negative rows
        b3 = Board(rows=-5, cols=7)
        self.assertEqual((b3.rows, b3.cols), (default_rows, 7))

    def test_invalid_difficulty_with_custom_size_uses_custom_rows_cols(self):
        """
        If difficulty is invalid but rows/cols are provided, we should still
        respect the custom size and compute/clamp mines.
        """
        rows, cols = 8, 12
        b = Board(rows=rows, cols=cols, difficulty="impossible-mode")
        self.assertEqual((b.rows, b.cols), (rows, cols))
        # Mines should be computed from density and clamped; just assert it is in valid range
        self.assertGreaterEqual(b.mines, 0)
        self.assertLess(b.mines, rows * cols)


class TestBoardMineClamping(unittest.TestCase):
    """Tests around mine count clamping: [0, total_cells - 1]."""

    def test_mines_clamped_to_max_total_cells_minus_one(self):
        """Mines cannot exceed total_cells - 1."""
        rows, cols = 2, 2
        total_cells = rows * cols

        # Request a ridiculous number of mines
        b = Board(rows=rows, cols=cols, mines=999)
        self.assertEqual(b.mines, total_cells - 1)

    def test_mines_clamped_to_min_zero_when_negative(self):
        """Negative mine counts should clamp to 0."""
        rows, cols = 10, 10
        b = Board(rows=rows, cols=cols, mines=-5)
        self.assertEqual(b.mines, 0)

    def test_explicit_zero_mines_is_allowed(self):
        """Explicitly passing mines=0 should result in a valid zero-mine board."""
        rows, cols = 5, 5
        b = Board(rows=rows, cols=cols, mines=0)
        self.assertEqual(b.mines, 0)
        self.assertEqual((b.rows, b.cols), (rows, cols))


class TestBoardGridInitialization(unittest.TestCase):
    """Tests for the creation of the 2D grid of Cell objects and basic state."""

    def test_grid_dimensions_match_rows_and_cols(self):
        b = Board(difficulty="beginner")
        self.assertEqual(len(b.cells), b.rows)
        # Assume at least one row exists for a valid board
        self.assertGreater(b.rows, 0)
        self.assertEqual(len(b.cells[0]), b.cols)

    def test_every_grid_element_is_a_cell(self):
        b = Board(difficulty="beginner")
        for r in range(b.rows):
            for c in range(b.cols):
                self.assertIsInstance(b.cells[r][c], Cell)

    def test_initial_game_state_and_total_cells(self):
        b = Board(difficulty="beginner")
        self.assertEqual(b.state, "PLAYING")
        self.assertEqual(b.total_cells, b.rows * b.cols)

    def test_cells_start_unrevealed_and_not_mines_by_default(self):
        """At initialization, cells exist but mines have not yet been placed."""
        b = Board(difficulty="beginner")
        for r in range(b.rows):
            for c in range(b.cols):
                cell = b.cells[r][c]
                # Current design: all cells start as non-mine, unrevealed, unflagged.
                self.assertFalse(cell.is_mine)
                self.assertFalse(cell.is_revealed)
                self.assertFalse(cell.is_flagged)
                self.assertIsInstance(cell.neighbor_mines, int)


if __name__ == "__main__":
    unittest.main()