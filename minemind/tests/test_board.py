import io
import math
import unittest
from contextlib import redirect_stdout

from minemind.core.board import Board, Cell
from minemind.render import display_board


class TestCellRepr(unittest.TestCase):
    """Tests for the Cell dataclass behavior."""

    def test_repr_hidden_unflagged_non_mine(self):
        cell = Cell(is_mine=False, is_revealed=False, is_flagged=False, neighbor_mines=0)
        self.assertEqual(repr(cell), "#")

    def test_repr_flagged(self):
        cell = Cell(is_mine=False, is_revealed=False, is_flagged=True, neighbor_mines=0)
        self.assertEqual(repr(cell), "F")

    def test_repr_revealed_non_mine(self):
        cell = Cell(is_mine=False, is_revealed=True, is_flagged=False, neighbor_mines=3)
        self.assertEqual(repr(cell), "3")

    def test_repr_revealed_mine(self):
        cell = Cell(is_mine=True, is_revealed=True, is_flagged=False, neighbor_mines=0)
        self.assertEqual(repr(cell), "M")


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


class TestMinePlacement(unittest.TestCase):
    """Deferred mine placement and safe-zone behavior."""

    def test_place_mines_respects_safe_zone(self):
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

        mine_count = sum(
            1 for r in range(rows) for c in range(cols) if b.cells[r][c].is_mine
        )
        self.assertEqual(mine_count, b.mines)

    def test_place_mines_reduces_mines_when_safe_zone_too_large(self):
        b = Board(rows=1, cols=1, mines=5, difficulty="whatever")
        self.assertEqual(b.mines, 0)

        b.mines = 5
        b._place_mines(0, 0)

        self.assertEqual(b.mines, 0)
        self.assertFalse(b.cells[0][0].is_mine)

    def test_place_mines_when_safe_zone_covers_most_of_board(self):
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
        b = Board(rows=3, cols=3, mines=0, difficulty="whatever") 

        for r in range(b.rows):
            for c in range(b.cols):
                b.cells[r][c] = Cell()

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
        b.cells[0][0].neighbor_mines = 99

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

        b.cells[0][0].is_mine = False
        b.cells[0][0].is_flagged = True

        b.cells[0][1].is_mine = True
        b.cells[0][1].is_flagged = True

        b.cells[0][2].is_mine = True
        b.cells[0][2].is_flagged = False

        b.state = "LOST"

        tokens = self._get_row_tokens(b, 0)
        self.assertEqual(tokens, ["X", "F", "M"])