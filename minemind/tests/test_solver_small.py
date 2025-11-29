# minemind/tests/test_solver.py

import unittest

from minemind.core.board import Board, Cell
from minemind.core.solver import MinemindSolver


class TestSolverTrivialRules(unittest.TestCase):
    """Tests for the solver's Trivial 1 (Flag) and Trivial 2 (Reveal) rules."""

    def setUp(self):
        self.solver = MinemindSolver()

    # T1: Flag Rule Success (Trivial 1)
    def test_flag_rule_success_two_mines(self):
        """
        3x3 board.
        Mines at (0,0) and (0,1). Reveal (1,1), which shows count=2.
        All other neighbors of (1,1) are already revealed (safe),
        so the only hidden neighbors are (0,0) and (0,1).

        The solver should flag (0,0) and (0,1).
        """
        b = Board(rows=3, cols=3, mines=0, difficulty="whatever")

        # Reset cells to clean state
        for r in range(b.rows):
            for c in range(b.cols):
                b.cells[r][c] = Cell()

        # Place two mines at (0,0) and (0,1)
        b.cells[0][0].is_mine = True
        b.cells[0][1].is_mine = True
        b._calculate_neighbor_counts()

        # Reveal all neighbors of (1,1) EXCEPT the two mine cells
        neighbors = b._get_neighbors_coords(1, 1)
        for nr, nc in neighbors:
            if (nr, nc) not in [(0, 0), (0, 1)]:
                b.cells[nr][nc].is_revealed = True

        # Reveal the numbered cell itself
        b.cells[1][1].is_revealed = True
        self.assertEqual(b.cells[1][1].neighbor_mines, 2)

        moves = self.solver.solve_step(b)

        flag_moves = sorted(m for m in moves if m[2] == "FLAG")
        expected_flags = sorted([(0, 0, "FLAG"), (0, 1, "FLAG")])
        self.assertEqual(flag_moves, expected_flags)

    # T2: Reveal Rule Success (Trivial 2)
    def test_reveal_rule_success_all_safes(self):
        """
        3x3 board.
        Single mine at (0,0). Reveal (1,1) (count=1). Flag (0,0) manually.

        Solver should reveal all remaining 7 hidden neighbors of (1,1).
        """
        b = Board(rows=3, cols=3, mines=0, difficulty="whatever")

        # Reset to clean cells
        for r in range(b.rows):
            for c in range(b.cols):
                b.cells[r][c] = Cell()

        # One mine at (0,0), flag it
        b.cells[0][0].is_mine = True
        b.cells[0][0].is_flagged = True
        b._calculate_neighbor_counts()

        # Reveal center (1,1), which should be '1'
        b.cells[1][1].is_revealed = True
        self.assertEqual(b.cells[1][1].neighbor_mines, 1)

        moves = self.solver.solve_step(b)

        # All neighbors of (1,1) except (0,0) (the flagged mine) should be REVEAL
        neighbors = set(b._get_neighbors_coords(1, 1))
        expected_reveals = sorted(
            (nr, nc, "REVEAL") for (nr, nc) in neighbors if (nr, nc) != (0, 0)
        )

        reveal_moves = sorted(m for m in moves if m[2] == "REVEAL")
        self.assertEqual(reveal_moves, expected_reveals)

    # T3: No Certainty (Failure Case)
    def test_no_certainty_returns_empty_list(self):
        """
        3x3 board.
        Reveal (1,1) (count=1). No flags. All 8 neighbors of (1,1) are hidden.

        The solver cannot deduce a certain mine or safe cell, so it returns [].
        """
        b = Board(rows=3, cols=3, mines=0, difficulty="whatever")

        # Reset cells
        for r in range(b.rows):
            for c in range(b.cols):
                b.cells[r][c] = Cell()

        # Place a single mine at (0,0) so (1,1) sees count=1
        b.cells[0][0].is_mine = True
        b._calculate_neighbor_counts()

        # Reveal (1,1), leave all neighbors hidden and unflagged
        b.cells[1][1].is_revealed = True
        self.assertEqual(b.cells[1][1].neighbor_mines, 1)

        moves = self.solver.solve_step(b)
        self.assertEqual(moves, [])

    # T4: Overlap Check (Seen Moves)
    def test_overlap_check_unique_flag_from_multiple_frontiers(self):
        """
        Two adjacent '1' cells share a single mine. The solver will analyze both
        frontier cells, but must only emit the flag move for that mine once.

        Example layout (M = mine, . = safe):

          .  M  .
          .  .  .
          .  .  .

        We force (0,0) and (0,2) to be revealed with neighbor_mines=1,
        and all their other neighbors revealed except the shared hidden mine (0,1).
        Both frontier cells see the same remaining hidden neighbor (0,1),
        so solver should produce a single (0,1,'FLAG') move.
        """
        b = Board(rows=3, cols=3, mines=0, difficulty="whatever")

        # Reset cells
        for r in range(b.rows):
            for c in range(b.cols):
                b.cells[r][c] = Cell()

        # Single mine at (0,1)
        b.cells[0][1].is_mine = True
        b._calculate_neighbor_counts()

        # Reveal neighbors around (0,0) and (0,2) so that:
        #  - For (0,0), the only hidden neighbor is (0,1)
        #  - For (0,2), the only hidden neighbor is (0,1)
        # We'll just reveal everything except (0,1).
        for r in range(b.rows):
            for c in range(b.cols):
                if (r, c) != (0, 1):
                    b.cells[r][c].is_revealed = True

        # Ensure (0,0) and (0,2) are frontier numbered cells with count=1
        self.assertEqual(b.cells[0][0].neighbor_mines, 1)
        self.assertEqual(b.cells[0][2].neighbor_mines, 1)

        moves = self.solver.solve_step(b)

        # Expect exactly one unique flag move at (0,1)
        flag_moves = [m for m in moves if m[2] == "FLAG"]
        self.assertEqual(len(flag_moves), 1)
        self.assertEqual(flag_moves[0], (0, 1, "FLAG"))

        # Also ensure there are no duplicate moves overall
        self.assertEqual(len(moves), len(set(moves)))


if __name__ == "__main__":
    unittest.main()