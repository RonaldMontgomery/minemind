import unittest

from minemind.core.board import Board, Cell
from minemind.core.solver import MinemindSolver


class TestSolverTrivialRules(unittest.TestCase):
    """Tests for the solver's basic flag/reveal logic (T1–T4)."""

    def setUp(self):
        self.solver = MinemindSolver()

    def test_basic_flag_rule_single_unknown_neighbor(self):
        """T1: single unknown neighbor must be a mine → FLAG it."""
        b = Board(rows=3, cols=3, mines=0, difficulty="whatever")

        for r in range(b.rows):
            for c in range(b.cols):
                b.cells[r][c] = Cell()

        b.cells[0][0].is_mine = True
        b._calculate_neighbor_counts()

        center_neighbors = b._get_neighbors_coords(1, 1)
        for nr, nc in center_neighbors:
            if (nr, nc) != (0, 0):
                b.cells[nr][nc].is_revealed = True

        b.cells[1][1].is_revealed = True

        moves = self.solver.solve_step(b)
        self.assertIn((0, 0, "FLAG"), moves)
        flag_moves = [m for m in moves if m[2] == "FLAG"]
        self.assertEqual(flag_moves, [(0, 0, "FLAG")])

    def test_basic_reveal_rule_all_mines_flagged(self):
        """T2: all mines flagged → remaining hidden neighbors are safe (REVEAL)."""
        b = Board(rows=3, cols=3, mines=0, difficulty="whatever")

        for r in range(b.rows):
            for c in range(b.cols):
                b.cells[r][c] = Cell()

        b.cells[0][0].is_mine = True
        b.cells[0][0].is_flagged = True
        b._calculate_neighbor_counts()

        b.cells[1][1].is_revealed = True

        moves = self.solver.solve_step(b)

        neighbors = set(b._get_neighbors_coords(1, 1))
        expected_reveals = sorted(
            (nr, nc, "REVEAL")
            for (nr, nc) in neighbors
            if (nr, nc) != (0, 0)
        )
        reveal_moves = sorted(m for m in moves if m[2] == "REVEAL")
        self.assertEqual(reveal_moves, expected_reveals)

    def test_no_certainty_returns_empty_move_list(self):
        """T3: ambiguous pattern → solver must return no moves."""
        b = Board(rows=3, cols=3, mines=0, difficulty="whatever")

        for r in range(b.rows):
            for c in range(b.cols):
                b.cells[r][c] = Cell()

        b.cells[0][0].is_mine = True
        b.cells[2][2].is_mine = True
        b._calculate_neighbor_counts()

        b.cells[1][0].is_revealed = True

        moves = self.solver.solve_step(b)
        self.assertEqual(moves, [])

    def test_flagged_neighbors_not_considered_for_moves(self):
        """T4: flagged neighbors are never returned as move targets."""
        b = Board(rows=3, cols=3, mines=0, difficulty="whatever")

        for r in range(b.rows):
            for c in range(b.cols):
                b.cells[r][c] = Cell()

        b.cells[0][0].is_mine = True
        b.cells[0][1].is_flagged = True
        b._calculate_neighbor_counts()

        b.cells[1][1].is_revealed = True

        moves = self.solver.solve_step(b)

        for r, c, action in moves:
            self.assertNotEqual((r, c), (0, 1))