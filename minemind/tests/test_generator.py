import unittest

from minemind.core.board import Board, Cell


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
