import unittest

from minemind.core.board import Board, Cell
from minemind.core.solver import MinemindSolver


class TestSolverTrivialAndSubsetRules(unittest.TestCase):
    """Tests for solver trivial rules and subset-based deductions on small boards."""

    def setUp(self):
        self.solver = MinemindSolver()

    # --- Trivial rules again with slightly different layouts (T1–T4) ---

    def test_flag_rule_success_two_mines(self):
        b = Board(rows=3, cols=3, mines=0, difficulty="whatever")

        for r in range(b.rows):
            for c in range(b.cols):
                b.cells[r][c] = Cell()

        b.cells[0][0].is_mine = True
        b.cells[0][1].is_mine = True
        b._calculate_neighbor_counts()

        neighbors = b._get_neighbors_coords(1, 1)
        for nr, nc in neighbors:
            if (nr, nc) not in [(0, 0), (0, 1)]:
                b.cells[nr][nc].is_revealed = True

        b.cells[1][1].is_revealed = True

        moves = self.solver.solve_step(b)

        flag_moves = sorted(m for m in moves if m[2] == "FLAG")
        expected_flags = sorted([(0, 0, "FLAG"), (0, 1, "FLAG")])
        self.assertEqual(flag_moves, expected_flags)

    def test_reveal_rule_success_all_safes(self):
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
            (nr, nc, "REVEAL") for (nr, nc) in neighbors if (nr, nc) != (0, 0)
        )
        reveal_moves = sorted(m for m in moves if m[2] == "REVEAL")
        self.assertEqual(reveal_moves, expected_reveals)

    def test_no_certainty_returns_empty_list(self):
        b = Board(rows=3, cols=3, mines=0, difficulty="whatever")

        for r in range(b.rows):
            for c in range(b.cols):
                b.cells[r][c] = Cell()

        b.cells[0][0].is_mine = True
        b._calculate_neighbor_counts()

        b.cells[1][1].is_revealed = True

        moves = self.solver.solve_step(b)
        self.assertEqual(moves, [])

    def test_overlap_check_unique_flag_from_multiple_frontiers(self):
        b = Board(rows=3, cols=3, mines=0, difficulty="whatever")

        for r in range(b.rows):
            for c in range(b.cols):
                b.cells[r][c] = Cell()

        b.cells[0][1].is_mine = True
        b._calculate_neighbor_counts()

        for r in range(b.rows):
            for c in range(b.cols):
                if (r, c) != (0, 1):
                    b.cells[r][c].is_revealed = True

        self.assertEqual(b.cells[0][0].neighbor_mines, 1)
        self.assertEqual(b.cells[0][2].neighbor_mines, 1)

        moves = self.solver.solve_step(b)

        flag_moves = [m for m in moves if m[2] == "FLAG"]
        self.assertEqual(len(flag_moves), 1)
        self.assertEqual(flag_moves[0], (0, 1, "FLAG"))
        self.assertEqual(len(moves), len(set(moves)))

    # --- Subset logic tests (T5–T6 + conceptual subset test) ---

    def test_subset_basic_reveal(self):
        b = Board(rows=3, cols=3, mines=0, difficulty="whatever")

        for r in range(b.rows):
            for c in range(b.cols):
                b.cells[r][c] = Cell()

        A = (0, 1)
        B = (1, 1)

        for r in range(b.rows):
            for c in range(b.cols):
                b.cells[r][c].is_revealed = True

        hidden_A = {(1, 0), (1, 1)}
        hidden_B = {(1, 0), (1, 1), (2, 1)}
        all_hidden = hidden_B

        for (r, c) in all_hidden:
            b.cells[r][c].is_revealed = False

        b.cells[A[0]][A[1]].is_revealed = True
        b.cells[B[0]][B[1]].is_revealed = True
        b.cells[A[0]][A[1]].neighbor_mines = 1
        b.cells[B[0]][B[1]].neighbor_mines = 1

        moves = self.solver.solve_step(b)

        self.assertIn((2, 1, "REVEAL"), moves)
        self.assertNotIn((2, 1, "FLAG"), moves)

    def test_subset_basic_flag(self):
        b = Board(rows=3, cols=3, mines=0, difficulty="whatever")

        for r in range(b.rows):
            for c in range(b.cols):
                b.cells[r][c] = Cell()

        A = (0, 1)
        B = (1, 1)

        for r in range(b.rows):
            for c in range(b.cols):
                b.cells[r][c].is_revealed = True

        hidden_A = {(1, 0), (1, 1)}
        hidden_B = {(1, 0), (1, 1), (2, 1)}
        all_hidden = hidden_B

        for (r, c) in all_hidden:
            b.cells[r][c].is_revealed = False

        b.cells[A[0]][A[1]].is_revealed = True
        b.cells[B[0]][B[1]].is_revealed = True

        b.cells[A[0]][A[1]].neighbor_mines = 1
        b.cells[B[0]][B[1]].neighbor_mines = 2

        moves = self.solver.solve_step(b)

        self.assertIn((2, 1, "FLAG"), moves)
        self.assertNotIn((2, 1, "REVEAL"), moves)

    def test_subset_reveal_rule(self):
        b = Board(rows=3, cols=3, mines=0, difficulty="whatever")

        for r in range(b.rows):
            for c in range(b.cols):
                b.cells[r][c] = Cell()

        A = (0, 1)
        B = (1, 1)

        for r in range(b.rows):
            for c in range(b.cols):
                b.cells[r][c].is_revealed = True

        hidden_A = {(1, 0), (1, 1)}
        hidden_B = {(1, 0), (1, 1), (2, 1)}
        all_hidden = hidden_B

        for (r, c) in all_hidden:
            b.cells[r][c].is_revealed = False

        b.cells[A[0]][A[1]].is_revealed = True
        b.cells[B[0]][B[1]].is_revealed = True
        b.cells[A[0]][A[1]].neighbor_mines = 1
        b.cells[B[0]][B[1]].neighbor_mines = 1

        moves = self.solver.solve_step(b)

        self.assertIn((2, 1, "REVEAL"), moves)
        self.assertNotIn((2, 1, "FLAG"), moves)
