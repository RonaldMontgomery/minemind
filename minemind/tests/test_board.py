import math
import unittest

from minemind.core.board import Board, Cell


class TestCellRepr(unittest.TestCase):
    """Tests for the Cell dataclass behavior."""

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


class TestBoardConfig(unittest.TestCase):
    """Core configuration and clamping behavior."""

    def test_standard_beginner_config(self):
        """difficulty='beginner' with no custom rows/cols should use standard config."""
        b = Board(difficulty="beginner")
        self.assertEqual((b.rows, b.cols, b.mines), (9, 9, 10))

    def test_invalid_difficulty_without_custom_falls_back_to_beginner(self):
        """
        Invalid difficulty and no custom sizes should fall back
        to beginner defaults (9x9, 10 mines).
        """
        b = Board(difficulty="nonsense")
        self.assertEqual((b.rows, b.cols, b.mines), (9, 9, 10))

    def test_custom_size_with_invalid_difficulty_uses_custom_dimensions(self):
        """
        If custom rows/cols are provided, we should use them even when
        difficulty string is invalid.
        """
        b = Board(rows=12, cols=7, mines=5, difficulty="nonsense")
        self.assertEqual(b.rows, 12)
        self.assertEqual(b.cols, 7)
        self.assertEqual(b.mines, 5)

    def test_non_positive_rows_cols_fall_back_to_defaults(self):
        """
        Non-positive or non-int rows/cols should fall back to default beginner size.
        """
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
        """
        When mines=None, mine count should be floor(total_cells * DEFAULT_DENSITY),
        then clamped between 0 and total_cells - 1.
        """
        rows, cols = 4, 5
        total_cells = rows * cols
        expected = math.floor(total_cells * Board.DEFAULT_DENSITY)

        b = Board(rows=rows, cols=cols, mines=None, difficulty="whatever")
        self.assertEqual(b.mines, expected)


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


class TestNeighbors(unittest.TestCase):
    """Edge and corner neighbor behavior."""

    def setUp(self):
        self.board_2x2 = Board(rows=2, cols=2, mines=0, difficulty="whatever")
        self.board_3x3 = Board(rows=3, cols=3, mines=0, difficulty="whatever")

    def test_neighbors_corner_cell_2x2(self):
        """
        Corner cell (0,0) on 2x2 should have exactly three neighbors: (0,1), (1,0), (1,1).
        """
        nbrs = self.board_2x2._get_neighbors_coords(0, 0)
        expected = {(0, 1), (1, 0), (1, 1)}
        self.assertEqual(set(nbrs), expected)

    def test_neighbors_center_cell_3x3(self):
        """
        Center cell (1,1) on 3x3 should have 8 neighbors.
        """
        nbrs = self.board_3x3._get_neighbors_coords(1, 1)
        self.assertEqual(len(nbrs), 8)
        expected = {
            (0, 0), (0, 1), (0, 2),
            (1, 0),         (1, 2),
            (2, 0), (2, 1), (2, 2),
        }
        self.assertEqual(set(nbrs), expected)

    def test_neighbors_edge_cell_3x3(self):
        """
        Edge cell (0,1) (top middle) on 3x3 should have 5 neighbors.
        """
        nbrs = self.board_3x3._get_neighbors_coords(0, 1)
        self.assertEqual(len(nbrs), 5)
        expected = {
            (0, 0), (0, 2),
            (1, 0), (1, 1), (1, 2),
        }
        self.assertEqual(set(nbrs), expected)


class TestMinePlacement(unittest.TestCase):
    """Deferred mine placement and safe-zone behavior."""

    def test_place_mines_respects_safe_zone(self):
        """
        _place_mines must never put a mine in the safe cell or its neighbors.
        """
        rows, cols = 10, 10
        mines = 20
        b = Board(rows=rows, cols=cols, mines=mines, difficulty="whatever")

        safe_r, safe_c = 5, 5
        safe_coords = set(b._get_neighbors_coords(safe_r, safe_c))
        safe_coords.add((safe_r, safe_c))

        b._place_mines(safe_r, safe_c)

        for (r, c) in safe_coords:
            with self.subTest(r=r, c=c):
                self.assertFalse(b.cells[r][c].is_mine)

        # ensure the number of mines equals the board's mine count
        mine_count = sum(
            1 for r in range(rows) for c in range(cols) if b.cells[r][c].is_mine
        )
        self.assertEqual(mine_count, b.mines)

    def test_place_mines_reduces_mines_when_safe_zone_too_large(self):
        """
        If safe zone covers the whole board (1x1), mines
        should be reduced so we don't try to sample more than candidates.
        """
        b = Board(rows=1, cols=1, mines=5, difficulty="whatever")
        # From _get_config clamp: total_cells=1, mines -> 0
        self.assertEqual(b.mines, 0)

        # Explicitly set mines > 0 to test _place_mines logic too
        b.mines = 5
        b._place_mines(0, 0)

        # After _place_mines, mines should be reduced to 0 (no candidates)
        self.assertEqual(b.mines, 0)
        self.assertFalse(b.cells[0][0].is_mine)

    def test_place_mines_when_safe_zone_covers_most_of_board(self):
        """
        3x3 board, safe cell in center makes entire board 'safe'.
        _place_mines should not crash and should set mines to 0.
        """
        b = Board(rows=3, cols=3, mines=8, difficulty="whatever")
        b._place_mines(1, 1)

        all_mines = [
            (r, c)
            for r in range(b.rows)
            for c in range(b.cols)
            if b.cells[r][c].is_mine
        ]
        self.assertEqual(len(all_mines), 0)
        self.assertEqual(b.mines, 0)


class TestNeighborCounts(unittest.TestCase):
    """Behavior of _calculate_neighbor_counts."""

    def test_calculate_neighbor_counts_simple_pattern(self):
        """
        Manually place a few mines and verify neighbor counts on a small board.
        Layout (M = mine, . = empty):

        M . .
        . . .
        . M .

        Mines at (0,0) and (2,1).
        """
        # Ensure we don't accidentally run the random mine placement from __init__
        b = Board(rows=3, cols=3, mines=0, difficulty="whatever") 

        # Reset cells (Good practice for deterministic tests)
        for r in range(b.rows):
            for c in range(b.cols):
                b.cells[r][c] = Cell()

        # Place deterministic mines
        b.cells[0][0].is_mine = True
        b.cells[2][1].is_mine = True

        b._calculate_neighbor_counts()

        self.assertEqual(b.cells[0][1].neighbor_mines, 1)  # near (0,0)
        self.assertEqual(b.cells[1][0].neighbor_mines, 2)  # FIX: near (0,0) and (2,1)
        self.assertEqual(b.cells[1][1].neighbor_mines, 2)  # adjacent to both mines
        self.assertEqual(b.cells[1][2].neighbor_mines, 1)  # near (2,1)
        self.assertEqual(b.cells[2][2].neighbor_mines, 1)  # near (2,1)

    def test_calculate_neighbor_counts_ignores_mine_cells(self):
        """
        neighbor_mines for cells that *are* mines should remain whatever they were
        (we don't overwrite them in _calculate_neighbor_counts).
        """
        b = Board(rows=2, cols=2, mines=0, difficulty="whatever")
        b.cells[0][0].is_mine = True
        b.cells[0][0].neighbor_mines = 99  # sentinel

        b._calculate_neighbor_counts()

        # ensure we did not overwrite the mine's neighbor_mines field
        self.assertEqual(b.cells[0][0].neighbor_mines, 99)
        # but neighbors should be updated appropriately
        self.assertEqual(b.cells[0][1].neighbor_mines, 1)
        self.assertEqual(b.cells[1][0].neighbor_mines, 1)
        self.assertEqual(b.cells[1][1].neighbor_mines, 1)

    import math
import unittest

from minemind.core.board import Board, Cell


class TestCellRepr(unittest.TestCase):
    """Tests for the Cell dataclass behavior."""

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


class TestBoardConfig(unittest.TestCase):
    """Core configuration and clamping behavior."""

    def test_standard_beginner_config(self):
        """difficulty='beginner' with no custom rows/cols should use standard config."""
        b = Board(difficulty="beginner")
        self.assertEqual((b.rows, b.cols, b.mines), (9, 9, 10))

    def test_invalid_difficulty_without_custom_falls_back_to_beginner(self):
        """
        Invalid difficulty and no custom sizes should fall back
        to beginner defaults (9x9, 10 mines).
        """
        b = Board(difficulty="nonsense")
        self.assertEqual((b.rows, b.cols, b.mines), (9, 9, 10))

    def test_custom_size_with_invalid_difficulty_uses_custom_dimensions(self):
        """
        If custom rows/cols are provided, we should use them even when
        difficulty string is invalid.
        """
        b = Board(rows=12, cols=7, mines=5, difficulty="nonsense")
        self.assertEqual(b.rows, 12)
        self.assertEqual(b.cols, 7)
        self.assertEqual(b.mines, 5)

    def test_non_positive_rows_cols_fall_back_to_defaults(self):
        """
        Non-positive or non-int rows/cols should fall back to default beginner size.
        """
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
        """
        When mines=None, mine count should be floor(total_cells * DEFAULT_DENSITY),
        then clamped between 0 and total_cells - 1.
        """
        rows, cols = 4, 5
        total_cells = rows * cols
        expected = math.floor(total_cells * Board.DEFAULT_DENSITY)

        b = Board(rows=rows, cols=cols, mines=None, difficulty="whatever")
        self.assertEqual(b.mines, expected)


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


class TestNeighbors(unittest.TestCase):
    """Edge and corner neighbor behavior."""

    def setUp(self):
        self.board_2x2 = Board(rows=2, cols=2, mines=0, difficulty="whatever")
        self.board_3x3 = Board(rows=3, cols=3, mines=0, difficulty="whatever")

    def test_neighbors_corner_cell_2x2(self):
        """
        Corner cell (0,0) on 2x2 should have exactly three neighbors: (0,1), (1,0), (1,1).
        """
        nbrs = self.board_2x2._get_neighbors_coords(0, 0)
        expected = {(0, 1), (1, 0), (1, 1)}
        self.assertEqual(set(nbrs), expected)

    def test_neighbors_center_cell_3x3(self):
        """
        Center cell (1,1) on 3x3 should have 8 neighbors.
        """
        nbrs = self.board_3x3._get_neighbors_coords(1, 1)
        self.assertEqual(len(nbrs), 8)
        expected = {
            (0, 0), (0, 1), (0, 2),
            (1, 0),         (1, 2),
            (2, 0), (2, 1), (2, 2),
        }
        self.assertEqual(set(nbrs), expected)

    def test_neighbors_edge_cell_3x3(self):
        """
        Edge cell (0,1) (top middle) on 3x3 should have 5 neighbors.
        """
        nbrs = self.board_3x3._get_neighbors_coords(0, 1)
        self.assertEqual(len(nbrs), 5)
        expected = {
            (0, 0), (0, 2),
            (1, 0), (1, 1), (1, 2),
        }
        self.assertEqual(set(nbrs), expected)


class TestMinePlacement(unittest.TestCase):
    """Deferred mine placement and safe-zone behavior."""

    def test_place_mines_respects_safe_zone(self):
        """
        _place_mines must never put a mine in the safe cell or its neighbors.
        """
        rows, cols = 10, 10
        mines = 20
        b = Board(rows=rows, cols=cols, mines=mines, difficulty="whatever")

        safe_r, safe_c = 5, 5
        safe_coords = set(b._get_neighbors_coords(safe_r, safe_c))
        safe_coords.add((safe_r, safe_c))

        b._place_mines(safe_r, safe_c)

        for (r, c) in safe_coords:
            with self.subTest(r=r, c=c):
                self.assertFalse(b.cells[r][c].is_mine)

        # ensure the number of mines equals the board's mine count
        mine_count = sum(
            1 for r in range(rows) for c in range(cols) if b.cells[r][c].is_mine
        )
        self.assertEqual(mine_count, b.mines)

    def test_place_mines_reduces_mines_when_safe_zone_too_large(self):
        """
        If safe zone covers the whole board (1x1), mines
        should be reduced so we don't try to sample more than candidates.
        """
        b = Board(rows=1, cols=1, mines=5, difficulty="whatever")
        # From _get_config clamp: total_cells=1, mines -> 0
        self.assertEqual(b.mines, 0)

        # Explicitly set mines > 0 to test _place_mines logic too
        b.mines = 5
        b._place_mines(0, 0)

        # After _place_mines, mines should be reduced to 0 (no candidates)
        self.assertEqual(b.mines, 0)
        self.assertFalse(b.cells[0][0].is_mine)

    def test_place_mines_when_safe_zone_covers_most_of_board(self):
        """
        3x3 board, safe cell in center makes entire board 'safe'.
        _place_mines should not crash and should set mines to 0.
        """
        b = Board(rows=3, cols=3, mines=8, difficulty="whatever")
        b._place_mines(1, 1)

        all_mines = [
            (r, c)
            for r in range(b.rows)
            for c in range(b.cols)
            if b.cells[r][c].is_mine
        ]
        self.assertEqual(len(all_mines), 0)
        self.assertEqual(b.mines, 0)


class TestNeighborCounts(unittest.TestCase):
    """Behavior of _calculate_neighbor_counts."""

    def test_calculate_neighbor_counts_simple_pattern(self):
        """
        Manually place a few mines and verify neighbor counts on a small board.
        Layout (M = mine, . = empty):

        M . .
        . . .
        . M .

        Mines at (0,0) and (2,1).
        """
        # Ensure we don't accidentally run the random mine placement from __init__
        b = Board(rows=3, cols=3, mines=0, difficulty="whatever") 

        # Reset cells (Good practice for deterministic tests)
        for r in range(b.rows):
            for c in range(b.cols):
                b.cells[r][c] = Cell()

        # Place deterministic mines
        b.cells[0][0].is_mine = True
        b.cells[2][1].is_mine = True

        b._calculate_neighbor_counts()

        self.assertEqual(b.cells[0][1].neighbor_mines, 1)  # near (0,0)
        self.assertEqual(b.cells[1][0].neighbor_mines, 2)  # FIX: near (0,0) and (2,1)
        self.assertEqual(b.cells[1][1].neighbor_mines, 2)  # adjacent to both mines
        self.assertEqual(b.cells[1][2].neighbor_mines, 1)  # near (2,1)
        self.assertEqual(b.cells[2][2].neighbor_mines, 1)  # near (2,1)

    def test_calculate_neighbor_counts_ignores_mine_cells(self):
        """
        neighbor_mines for cells that *are* mines should remain whatever they were
        (we don't overwrite them in _calculate_neighbor_counts).
        """
        b = Board(rows=2, cols=2, mines=0, difficulty="whatever")
        b.cells[0][0].is_mine = True
        b.cells[0][0].neighbor_mines = 99  # sentinel

        b._calculate_neighbor_counts()

        # ensure we did not overwrite the mine's neighbor_mines field
        self.assertEqual(b.cells[0][0].neighbor_mines, 99)
        # but neighbors should be updated appropriately
        self.assertEqual(b.cells[0][1].neighbor_mines, 1)
        self.assertEqual(b.cells[1][0].neighbor_mines, 1)
        self.assertEqual(b.cells[1][1].neighbor_mines, 1)


if __name__ == "__main__":
    unittest.main()