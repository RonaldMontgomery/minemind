import unittest

from minemind.core.board import Board, Cell
from minemind.core.solver import MinemindSolver


class TestSolverTrivialRules(unittest.TestCase):
    """Tests for the solver's basic flag/reveal logic."""

    def setUp(self):
        self.solver = MinemindSolver()

    def test_basic_flag_rule_single_unknown_neighbor(self):
        """
        T1: Basic Flag Rule (Mines Found)
        3x3 board.
        Mine at (0,0). Cell (1,1) is revealed with count=1, and all of its
        other neighbors are already revealed. The only hidden neighbor is (0,0),
        so the solver should FLAG (0,0).
        """
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
        """
        T2: Basic Reveal Rule (Safes Found)
        3x3 board.
        Mine at (0,0), which is flagged.
        Cell (1,1) is revealed with count=1. All other neighbors of (1,1)
        are hidden and unflagged. Solver should REVEAL those 7 neighbors.
        """
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
        """
        T3: No Certainty
        3x3 board, two mines at (0,0) and (2,2).
        Reveal (1,0) (count 1). There should not be a deterministically
        safe or mine cell, so the solver returns an empty move list.
        """
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
        """
        T4: Out-of-Bounds/Filtering – ignores flagged neighbors as candidates.
        3x3 board.
        Mine at (0,0). (0,1) is flagged. Reveal (1,1) (count 1).
        Solver must ignore flagged cells as targets.
        """
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


class TestSolverTrivialAndSubsetRules(unittest.TestCase):
    """Tests for solver trivial rules and subset-based deductions."""

    def setUp(self):
        self.solver = MinemindSolver()

    def test_flag_rule_success_two_mines(self):
        """
        T1: Flag Rule Success (Trivial 1, two hidden mines)
        Mines at (0,0) and (0,1). Reveal (1,1) with count=2.
        Solver should flag both (0,0) and (0,1).
        """
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
        self.assertEqual(b.cells[1][1].neighbor_mines, 2)

        moves = self.solver.solve_step(b)

        flag_moves = sorted(m for m in moves if m[2] == "FLAG")
        expected_flags = sorted([(0, 0, "FLAG"), (0, 1, "FLAG")])
        self.assertEqual(flag_moves, expected_flags)

    def test_reveal_rule_success_all_safes(self):
        """
        T2: Reveal Rule Success (Trivial 2, alternate layout)
        Single mine at (0,0). Reveal (1,1) (count=1). Flag (0,0) manually.
        Solver should reveal all remaining 7 hidden neighbors of (1,1).
        """
        b = Board(rows=3, cols=3, mines=0, difficulty="whatever")

        for r in range(b.rows):
            for c in range(b.cols):
                b.cells[r][c] = Cell()

        b.cells[0][0].is_mine = True
        b.cells[0][0].is_flagged = True
        b._calculate_neighbor_counts()

        b.cells[1][1].is_revealed = True
        self.assertEqual(b.cells[1][1].neighbor_mines, 1)

        moves = self.solver.solve_step(b)

        neighbors = set(b._get_neighbors_coords(1, 1))
        expected_reveals = sorted(
            (nr, nc, "REVEAL") for (nr, nc) in neighbors if (nr, nc) != (0, 0)
        )
        reveal_moves = sorted(m for m in moves if m[2] == "REVEAL")
        self.assertEqual(reveal_moves, expected_reveals)

    def test_no_certainty_returns_empty_list(self):
        """
        T3: No Certainty (Failure Case, alternate layout)
        3x3 board. Reveal (1,1) (count=1). No flags.
        All 8 neighbors of (1,1) are hidden -> [].
        """
        b = Board(rows=3, cols=3, mines=0, difficulty="whatever")

        for r in range(b.rows):
            for c in range(b.cols):
                b.cells[r][c] = Cell()

        b.cells[0][0].is_mine = True
        b._calculate_neighbor_counts()

        b.cells[1][1].is_revealed = True
        self.assertEqual(b.cells[1][1].neighbor_mines, 1)

        moves = self.solver.solve_step(b)
        self.assertEqual(moves, [])

    def test_overlap_check_unique_flag_from_multiple_frontiers(self):
        """
        T4: Overlap Check (Seen Moves)
        Two adjacent '1' cells share a single mine.
        Both frontier cells see the same remaining hidden neighbor (0,1),
        so solver should produce a single (0,1, 'FLAG') move.
        """
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

    def test_subset_basic_reveal(self):
        """
        T5: Basic Subset Reveal (Subset Deduction)
        Hidden_A = { (1,0), (1,1) }
        Hidden_B = { (1,0), (1,1), (2,1) }
        remaining_mines_A = remaining_mines_B = 1 -> (2,1) safe.
        """
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
        """
        T6: Subset Flag (Subset Deduction - mines in the difference set)
        Same geometry as T5, but remaining_mines_B = 2 so (2,1) must be a mine.
        """
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
        """
        Conceptual Subset Reveal Test.
        Hidden(A) ⊂ Hidden(B) and equal remaining mines => B \\ A are safe.
        """
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
