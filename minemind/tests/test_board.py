import io
import math
import unittest
from contextlib import redirect_stdout

from minemind.core.board import Board, Cell
from minemind.core.solver import MinemindSolver
from minemind.render import display_board


class TestCellRepr(unittest.TestCase):
    """Tests for the Cell dataclass rendering behavior."""

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
    """Core configuration and clamping behavior for Board._get_config."""

    def test_standard_beginner_config(self):
        b = Board(difficulty="beginner")
        self.assertEqual((b.rows, b.cols, b.mines), (9, 9, 10))

    def test_invalid_difficulty_without_custom_falls_back_to_beginner(self):
        b = Board(difficulty="nonsense")
        self.assertEqual((b.rows, b.cols, b.mines), (9, 9, 10))

    def test_custom_size_with_invalid_difficulty_uses_custom_dimensions(self):
        b = Board(rows=12, cols=7, mines=5, difficulty="nonsense")
        self.assertEqual((b.rows, b.cols, b.mines), (12, 7, 5))

    def test_non_positive_rows_cols_fall_back_to_defaults(self):
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
        b = Board(rows=2, cols=2, mines=50, difficulty="whatever")
        self.assertEqual(b.total_cells, 4)
        self.assertEqual(b.mines, 3)  # 4 - 1

    def test_negative_mine_count_becomes_zero(self):
        b = Board(rows=3, cols=3, mines=-10, difficulty="whatever")
        self.assertEqual(b.mines, 0)

    def test_default_density_for_custom_board(self):
        rows, cols = 4, 5
        total_cells = rows * cols
        expected = math.floor(total_cells * Board.DEFAULT_DENSITY)

        b = Board(rows=rows, cols=cols, mines=None, difficulty="whatever")
        self.assertEqual(b.mines, expected)


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


class TestBoardGridState(unittest.TestCase):
    """More detailed checks of the grid and board state."""

    def test_all_cells_initialized_consistently(self):
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
        rows, cols = 7, 11
        board = Board(rows=rows, cols=cols)
        self.assertEqual(board.total_cells, rows * cols)

    def test_initial_state_is_playing_for_custom_board(self):
        board = Board(rows=6, cols=9)
        self.assertEqual(board.state, "PLAYING")


class TestNeighbors(unittest.TestCase):
    """Edge and corner neighbor behavior."""

    def setUp(self):
        self.board_2x2 = Board(rows=2, cols=2, mines=0, difficulty="whatever")
        self.board_3x3 = Board(rows=3, cols=3, mines=0, difficulty="whatever")

    def test_neighbors_corner_cell_2x2(self):
        nbrs = self.board_2x2._get_neighbors_coords(0, 0)
        expected = {(0, 1), (1, 0), (1, 1)}
        self.assertEqual(set(nbrs), expected)

    def test_neighbors_center_cell_3x3(self):
        nbrs = self.board_3x3._get_neighbors_coords(1, 1)
        self.assertEqual(len(nbrs), 8)
        expected = {
            (0, 0), (0, 1), (0, 2),
            (1, 0),         (1, 2),
            (2, 0), (2, 1), (2, 2),
        }
        self.assertEqual(set(nbrs), expected)

    def test_neighbors_edge_cell_3x3(self):
        nbrs = self.board_3x3._get_neighbors_coords(0, 1)
        self.assertEqual(len(nbrs), 5)
        expected = {
            (0, 0), (0, 2),
            (1, 0), (1, 1), (1, 2),
        }
        self.assertEqual(set(nbrs), expected)


class TestNeighborCounts(unittest.TestCase):
    """Behavior of _calculate_neighbor_counts."""

    def test_calculate_neighbor_counts_simple_pattern(self):
        b = Board(rows=3, cols=3, mines=0, difficulty="whatever")

        # Reset cells
        for r in range(b.rows):
            for c in range(b.cols):
                b.cells[r][c] = Cell()

        # Mines at (0,0) and (2,1)
        b.cells[0][0].is_mine = True
        b.cells[2][1].is_mine = True

        b._calculate_neighbor_counts()

        self.assertEqual(b.cells[0][1].neighbor_mines, 1)
        self.assertEqual(b.cells[1][0].neighbor_mines, 2)
        self.assertEqual(b.cells[1][1].neighbor_mines, 2)
        self.assertEqual(b.cells[1][2].neighbor_mines, 1)
        self.assertEqual(b.cells[2][2].neighbor_mines, 1)

    def test_calculate_neighbor_counts_ignores_mine_cells(self):
        b = Board(rows=2, cols=2, mines=0, difficulty="whatever")
        b.cells[0][0].is_mine = True
        b.cells[0][0].neighbor_mines = 99  # sentinel

        b._calculate_neighbor_counts()

        self.assertEqual(b.cells[0][0].neighbor_mines, 99)
        self.assertEqual(b.cells[0][1].neighbor_mines, 1)
        self.assertEqual(b.cells[1][0].neighbor_mines, 1)
        self.assertEqual(b.cells[1][1].neighbor_mines, 1)


class TestRenderDisplay(unittest.TestCase):
    """Tests for the render/display_board behavior, including wrong flags."""

    def _get_row_tokens(self, board, row_index: int) -> list[str]:
        buf = io.StringIO()
        with redirect_stdout(buf):
            display_board(board)
        output = buf.getvalue().splitlines()

        row_line = output[2 + row_index]
        _, cells_part = row_line.split("|", 1)
        tokens = cells_part.strip().split()
        return tokens

    def test_flagged_non_mine_during_play_shows_F(self):
        b = Board(rows=1, cols=1, mines=0)
        cell = b.cells[0][0]
        cell.is_mine = False
        cell.is_flagged = True
        b.state = "PLAYING"

        tokens = self._get_row_tokens(b, 0)
        self.assertEqual(tokens, ["F"])

    def test_wrong_flag_after_loss_shows_X(self):
        b = Board(rows=1, cols=3, mines=0)

        # Cell 0: wrong flag (flagged, not a mine)
        b.cells[0][0].is_mine = False
        b.cells[0][0].is_flagged = True

        # Cell 1: correctly flagged mine
        b.cells[0][1].is_mine = True
        b.cells[0][1].is_flagged = True

        # Cell 2: unflagged mine
        b.cells[0][2].is_mine = True
        b.cells[0][2].is_flagged = False

        b.state = "LOST"

        tokens = self._get_row_tokens(b, 0)
        self.assertEqual(tokens, ["X", "F", "M"])


class TestBoardGameFlowPublicAPI(unittest.TestCase):
    """
    Tests that use the public reveal(r, c) and flag(r, c) methods
    to drive game flow.
    """

    def _make_simple_mine_layout(self) -> Board:
        b = Board(rows=2, cols=2, mines=0, difficulty="whatever")

        for r in range(b.rows):
            for c in range(b.cols):
                b.cells[r][c] = Cell()

        b.cells[0][0].is_mine = True
        b.mines = 1
        b._calculate_neighbor_counts()
        b.state = "PLAYING"
        return b

    def test_flag_toggles_is_flagged_without_reveal(self):
        b = self._make_simple_mine_layout()
        self.assertFalse(b.cells[0][0].is_flagged)

        b.flag(0, 0)
        self.assertTrue(b.cells[0][0].is_flagged)
        self.assertFalse(b.cells[0][0].is_revealed)

        # Unflag
        b.flag(0, 0)
        self.assertFalse(b.cells[0][0].is_flagged)

    def test_reveal_mine_sets_state_lost(self):
        b = self._make_simple_mine_layout()
        self.assertEqual(b.state, "PLAYING")

        b.reveal(0, 0)
        self.assertEqual(b.state, "LOST")
        self.assertTrue(b.cells[0][0].is_revealed)

    def test_reveal_safe_does_not_change_flagged_cells(self):
        b = self._make_simple_mine_layout()

        b.flag(0, 0)
        b.reveal(1, 1)

        self.assertTrue(b.cells[0][0].is_flagged)
        self.assertFalse(b.cells[0][0].is_revealed)
        self.assertTrue(b.cells[1][1].is_revealed)


class TestBoardFloodFillBehavior(unittest.TestCase):
    """
    Tests that the flood-fill style expansion when revealing zero-cells
    behaves correctly and stops at numbered cells.
    """

    def test_flood_fill_stops_at_numbered_cells(self):
        """
        Construct a board with a region of zero cells separated from other cells
        by a column of numbered cells (neighbor_mines > 0). Revealing inside
        the zero region should reveal the zeros and the boundary numbers, but
        should not 'leak' beyond the numbered boundary.
        """
        b = Board(rows=3, cols=4, mines=0, difficulty="whatever")

        # Manually set up a clean boundary structure:
        for r in range(b.rows):
            for c in range(b.cols):
                b.cells[r][c] = Cell()
                b.cells[r][c].neighbor_mines = 0 # Default all to 0
            
            # Column 2 (index 2) is the boundary (count = 1)
            b.cells[r][2].neighbor_mines = 1 

        # CRITICAL: Bypass the deferred setup that would wipe out your manual counts.
        b.mines_placed = True 
        
        # Reveal from inside the zero region.
        b.reveal(1, 0)

        # Zeros and numbered boundary (Col 0, 1, 2) should be revealed.
        for r in range(b.rows):
            for c in range(3):  # columns 0, 1, 2
                self.assertTrue(
                    b.cells[r][c].is_revealed,
                    f"Expected flood-fill to reveal zero region and boundary at ({r},{c}).",
                )

        # Rightmost column (3) should remain hidden (no propagation beyond numbers).
        for r in range(b.rows):
            self.assertFalse(
                b.cells[r][3].is_revealed,
                f"Flood-fill should not reveal beyond numbered boundary at row {r}.",
            )

class TestBoardWinConditionLogic(unittest.TestCase):
    """
    Tests that the board's win logic transitions state to WON
    only when all non-mine cells are revealed.
    """

    def test_win_condition_triggers_after_last_safe_cell_revealed(self):
        b = Board(rows=2, cols=2, mines=0, difficulty="whatever")

        for r in range(2):
            for c in range(2):
                b.cells[r][c] = Cell()

        b.cells[0][0].is_mine = True
        b.mines = 1
        b._calculate_neighbor_counts()
        b.state = "PLAYING"

        self.assertEqual(b.state, "PLAYING")

        b.reveal(0, 1)
        self.assertEqual(b.state, "PLAYING")

        b.reveal(1, 0)
        self.assertEqual(b.state, "PLAYING")

        b.reveal(1, 1)
        self.assertEqual(b.state, "WON")

    def test_not_won_if_safe_cells_remaining(self):
        b = Board(rows=2, cols=2, mines=0, difficulty="whatever")

        for r in range(2):
            for c in range(2):
                b.cells[r][c] = Cell()

        b.cells[0][0].is_mine = True
        b.mines = 1
        b._calculate_neighbor_counts()
        b.state = "PLAYING"

        b.reveal(1, 1)
        self.assertEqual(b.state, "PLAYING")


@unittest.skip("CLI validation tests depend on concrete helpers in cli.py; add when helpers are stable.")
class TestCLIValidation(unittest.TestCase):
    """
    Placeholder suite for CLI / input validation tests.

    Once cli.py exposes testable helpers (e.g., parse_move or validate_move),
    you can import them here and replace these skipped tests.
    """

    def test_example_placeholder(self):
        self.fail("Replace with real CLI tests once helpers are available.")