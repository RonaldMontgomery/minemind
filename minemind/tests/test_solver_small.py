import unittest

from minemind.core.board import Board, Cell
from minemind.core.solver import MinemindSolver


class TestSolverSmallBoardSmoke(unittest.TestCase):
    """
    Small integration-style tests for the solver on tiny boards.
    These are intentionally lightweight sanity checks.
    """

    def test_solver_returns_moves_or_empty_on_fresh_board(self):
        b = Board(rows=2, cols=2, mines=1, difficulty="whatever")

        # Avoid randomness: put the mine at (0,0)
        for r in range(b.rows):
            for c in range(b.cols):
                b.cells[r][c] = Cell()

        b.cells[0][0].is_mine = True
        b._calculate_neighbor_counts()

        solver = MinemindSolver()
        moves = solver.solve_step(b)

        # Solver is allowed to return [] if it has no deterministic move,
        # but it should not crash and moves should be a list of triples.
        self.assertIsInstance(moves, list)
        for move in moves:
            self.assertEqual(len(move), 3)


if __name__ == "__main__":
    unittest.main()
