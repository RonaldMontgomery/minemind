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


class TestBoardConfig(unittest.TestCase):
    """Core configuration and clamping behavior."""

    def test_standard_beginner_config(self):
        """difficulty='beginner' with no custom rows/cols should use standard config."""
        b = Board(difficulty="beginner")
        self.assertEqual((b.rows, b.cols, b.mines), (9, 9, 10))

    def test_invalid_difficulty_without_custom_falls_back_to_beginner(self):
        """Invalid difficulty and no custom sizes should fall back to beginner defaults."""
        b = Board(difficulty="nonsense")
        self.assertEqual((b.rows, b.cols, b.mines), (9, 9, 10))

    def test_custom_size_with_invalid_difficulty_uses_custom_dimensions(self):
        """Custom rows/cols are respected even when difficulty is invalid."""
        b = Board(rows=12, cols=7, mines=5, difficulty="nonsense")
        self.assertEqual(b.rows, 12)
        self.assertEqual(b.cols, 7)
        self.assertEqual(b.mines, 5)

    def test_non_positive_rows_cols_fall_back_to_defaults(self):
        """Non-positive rows/cols fall back to beginner defaults where appropriate."""
        # rows <= 0 -> default; cols valid
        b1 = Board(rows=0, cols=5, mines=3, difficulty="whatever")
        self.assertEqual(b1.rows, Board.STANDARD_CONFIGS["beginner"][0])
        self.assertEqual(b1.cols, 5)

        # cols <= 0 -> default; rows valid
        b2 = Board(rows=10, cols=-1, mines=3, difficulty="whatever")
        self.assertEqual(b2.rows, 10)
        self.assertEqual(b2.cols, Board.STANDARD_CONFIGS["beginner"][1])

        # both invalid -> both default
        b3 = Board(rows=-5, cols="oops", mines=3, difficulty="whatever")
        default_rows, default_cols, _ = Board.STANDARD_CONFIGS["beginner"]
        self.assertEqual(b3.rows, default_rows)
        self.assertEqual(b3.cols, default_cols)

    def test_mines_clamped_to_total_cells_minus_one(self):
        """Mines should never exceed total_cells - 1."""
        b = Board(rows=2, cols=2, mines=50, difficulty="whatever")
        self.assertEqual(b.total_cells, 4)
        self.assertEqual(b.mines, 3)  # 4 - 1

    def test_negative_mine_count_becomes_zero(self):
        """Negative mine counts should be clamped up to 0."""
        b = Board(rows=3, cols=3, mines=-10, difficulty="whatever")
        self.assertEqual(b.mines, 0)

    def test_default_density_for_custom_board(self):
        """Mines=None → mines = floor(total_cells * DEFAULT_DENSITY)."""
        rows, cols = 4, 5
        total_cells = rows * cols
        expected = math.floor(total_cells * Board.DEFAULT_DENSITY)

        b = Board(rows=rows, cols=cols, mines=None, difficulty="whatever")
        self.assertEqual(b.mines, expected)


class TestBoardCustomConfigs(unittest.TestCase):
    """Tests for custom row/col/mines behavior and DEFAULT_DENSITY logic."""

    def test_custom_size_with_no_mines_uses_default_density(self):
        rows, cols = 10, 10
        expected_mines = math.floor(rows * cols * Board.DEFAULT_DENSITY)

        b = Board(rows=rows, cols=cols)
        self.assertEqual((b.rows, b.cols), (rows, cols))
        self.assertEqual(b.mines, expected_mines)

    def test_small_custom_board_density_example(self):
        rows, cols = 5, 5
        expected_mines = math.floor(rows * cols * Board.DEFAULT_DENSITY)
        b = Board(rows=rows, cols=cols)
        self.assertEqual((b.rows, b.cols), (rows, cols))
        self.assertEqual(b.mines, expected_mines)

    def test_invalid_rows_cols_fall_back_to_defaults(self):
        default_rows, default_cols, _ = Board.STANDARD_CONFIGS["beginner"]

        b1 = Board(rows=0, cols=10)
        self.assertEqual((b1.rows, b1.cols), (default_rows, 10))

        b2 = Board(rows=10, cols=0)
        self.assertEqual((b2.rows, b2.cols), (10, default_cols))

        b3 = Board(rows=-5, cols=7)
        self.assertEqual((b3.rows, b3.cols), (default_rows, 7))

    def test_invalid_difficulty_with_custom_size_uses_custom_rows_cols(self):
        rows, cols = 8, 12
        b = Board(rows=rows, cols=cols, difficulty="impossible-mode")
        self.assertEqual((b.rows, b.cols), (rows, cols))
        self.assertGreaterEqual(b.mines, 0)
        self.assertLess(b.mines, rows * cols)


class TestBoardCustomConfigEdges(unittest.TestCase):
    """Extra tests exercising _get_config edge cases and clamping logic."""

    def test_invalid_difficulty_with_custom_size_uses_custom_and_density(self):
        rows, cols = 8, 12
        board = Board(rows=rows, cols=cols, difficulty="impossible-mode")

        self.assertEqual(board.rows, rows)
        self.assertEqual(board.cols, cols)

        expected_mines = math.floor(rows * cols * Board.DEFAULT_DENSITY)
        self.assertEqual(board.mines, expected_mines)

    def test_valid_difficulty_with_custom_size_prefers_custom_size(self):
        beginner_rows, beginner_cols, _ = Board.STANDARD_CONFIGS["beginner"]
        rows, cols = beginner_rows + 3, beginner_cols + 1

        board = Board(rows=rows, cols=cols, difficulty="beginner")

        self.assertEqual(board.rows, rows)
        self.assertEqual(board.cols, cols)

        expected_mines = math.floor(rows * cols * Board.DEFAULT_DENSITY)
        self.assertEqual(board.mines, expected_mines)

    def test_zero_rows_fall_back_to_default_rows(self):
        default_rows, default_cols, _ = Board.STANDARD_CONFIGS["beginner"]

        board = Board(rows=0, cols=10)
        self.assertEqual(board.rows, default_rows)
        self.assertEqual(board.cols, 10)

        expected_mines = math.floor(default_rows * 10 * Board.DEFAULT_DENSITY)
        self.assertEqual(board.mines, expected_mines)

        board2 = Board(rows=10, cols=-1)
        self.assertEqual(board2.rows, 10)
        self.assertEqual(board2.cols, default_cols)

    def test_only_rows_provided_uses_default_cols(self):
        default_rows, default_cols, _ = Board.STANDARD_CONFIGS["beginner"]

        custom_rows = default_rows + 5
        board = Board(rows=custom_rows)

        self.assertEqual(board.rows, custom_rows)
        self.assertEqual(board.cols, default_cols)

        expected_mines = math.floor(custom_rows * default_cols * Board.DEFAULT_DENSITY)
        self.assertEqual(board.mines, expected_mines)

    def test_negative_mines_clamped_to_zero(self):
        board = Board(rows=6, cols=6, mines=-10)
        self.assertEqual(board.rows, 6)
        self.assertEqual(board.cols, 6)
        self.assertEqual(board.mines, 0)

    def test_zero_mines_allowed(self):
        board = Board(rows=4, cols=4, mines=0)
        self.assertEqual(board.mines, 0)
        self.assertEqual(board.total_cells, 16)


class TestBoardMineClamping(unittest.TestCase):
    """Tests around mine count clamping: [0, total_cells - 1]."""

    def test_mines_clamped_to_max_total_cells_minus_one(self):
        rows, cols = 2, 2
        total_cells = rows * cols

        b = Board(rows=rows, cols=cols, mines=999)
        self.assertEqual(b.mines, total_cells - 1)

    def test_mines_clamped_to_min_zero_when_negative(self):
        rows, cols = 10, 10
        b = Board(rows=rows, cols=cols, mines=-5)
        self.assertEqual(b.mines, 0)

    def test_explicit_zero_mines_is_allowed(self):
        rows, cols = 5, 5
        b = Board(rows=rows, cols=cols, mines=0)
        self.assertEqual(b.mines, 0)
        self.assertEqual((b.rows, b.cols), (rows, cols))


class TestBoardGridInitialization(unittest.TestCase):
    """Tests for the creation of the 2D grid of Cell objects and basic state."""

    def test_grid_dimensions_match_rows_and_cols(self):
        b = Board(difficulty="beginner")
        self.assertEqual(len(b.cells), b.rows)
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
        b = Board(difficulty="beginner")
        for r in range(b.rows):
            for c in range(b.cols):
                cell = b.cells[r][c]
                self.assertFalse(cell.is_mine)
                self.assertFalse(cell.is_revealed)
                self.assertFalse(cell.is_flagged)
                self.assertIsInstance(cell.neighbor_mines, int)
