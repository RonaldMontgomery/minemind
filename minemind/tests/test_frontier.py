import unittest

from minemind.core.board import Board, Cell


class TestFrontierDetection(unittest.TestCase):
    """
    Tests that we can identify frontier cells conceptually:
    revealed numbered cells that still have at least one hidden neighbor.
    These tests don't depend on any specific Frontier class implementation.
    """

    def _collect_frontier_cells(self, board: Board):
        frontier = []
        for r in range(board.rows):
            for c in range(board.cols):
                cell = board.cells[r][c]
                if not cell.is_revealed or cell.is_mine:
                    continue
                nbrs = board._get_neighbors_coords(r, c)
                if any(not board.cells[nr][nc].is_revealed for nr, nc in nbrs):
                    frontier.append((r, c))
        return frontier

    def test_frontier_cells_exist_when_numbered_cell_has_hidden_neighbors(self):
        b = Board(rows=3, cols=3, mines=0, difficulty="whatever")

        for r in range(b.rows):
            for c in range(b.cols):
                b.cells[r][c] = Cell()

        # Single mine at (0,1) so neighbors have count >= 1
        b.cells[0][1].is_mine = True
        b._calculate_neighbor_counts()

        # Reveal the two edge cells (0,0) and (0,2), leave others hidden
        b.cells[0][0].is_revealed = True
        b.cells[0][2].is_revealed = True

        frontier = self._collect_frontier_cells(b)

        # Both revealed numbered cells have at least one hidden neighbor.
        self.assertIn((0, 0), frontier)
        self.assertIn((0, 2), frontier)

    def test_no_frontier_when_all_neighbors_revealed(self):
        b = Board(rows=2, cols=2, mines=0, difficulty="whatever")

        for r in range(b.rows):
            for c in range(b.cols):
                b.cells[r][c] = Cell()

        # Reveal everything
        for r in range(b.rows):
            for c in range(b.cols):
                b.cells[r][c].is_revealed = True

        frontier = self._collect_frontier_cells(b)
        self.assertEqual(frontier, [])
