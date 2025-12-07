# minemind/tests/test_cli.py

import unittest
from io import StringIO
from contextlib import redirect_stdout

from minemind.core.board import Board
from minemind.cli import MinemindShell


class TestCliNewCommand(unittest.TestCase):
    """Tests for the 'new' command creating boards."""

    def test_new_beginner_creates_beginner_board(self):
        shell = MinemindShell()
        self.assertIsNone(shell.board, "Shell should start with no board.")

        with redirect_stdout(StringIO()):
            shell.do_new("beginner")

        self.assertIsInstance(shell.board, Board)
        self.assertEqual(
            (shell.board.rows, shell.board.cols, shell.board.mines),
            Board.STANDARD_CONFIGS["beginner"],
        )

    def test_new_invalid_difficulty_does_not_crash(self):
        """
        Passing an invalid difficulty should not crash the shell.
        Exact error message can vary; we only assert that it runs and
        does not replace an existing valid board.
        """
        shell = MinemindShell()

        # First create a good board
        with redirect_stdout(StringIO()):
            shell.do_new("beginner")
        good_board = shell.board

        buf = StringIO()
        with redirect_stdout(buf):
            shell.do_new("not-a-diff")

        # Board should still exist and not be None
        self.assertIsNotNone(shell.board)
        # And we didn't blow away the existing board object
        self.assertIs(shell.board, good_board)


class TestCliRevealAndFlag(unittest.TestCase):
    """Tests for reveal/flag commands and basic validation behavior."""

    def setUp(self):
        self.shell = MinemindShell()
        # Create a beginner game for each test
        with redirect_stdout(StringIO()):
            self.shell.do_new("beginner")
        self.assertIsInstance(self.shell.board, Board)

    def test_reveal_valid_coordinates_updates_board(self):
        """
        A valid 'reveal r c' command should call Board.reveal and mark
        that cell as revealed.
        """
        r, c = 0, 0
        self.assertFalse(self.shell.board.cells[r][c].is_revealed)

        with redirect_stdout(StringIO()):
            self.shell.do_reveal(f"{r} {c}")

        self.assertTrue(
            self.shell.board.cells[r][c].is_revealed,
            "do_reveal should reveal the specified cell.",
        )

    def test_flag_valid_coordinates_toggles_flag(self):
        """
        A valid 'flag r c' should toggle the flag state on the given cell.
        """
        r, c = 0, 1
        self.assertFalse(self.shell.board.cells[r][c].is_flagged)

        with redirect_stdout(StringIO()):
            self.shell.do_flag(f"{r} {c}")

        self.assertTrue(self.shell.board.cells[r][c].is_flagged)

        # Second call should unflag it
        with redirect_stdout(StringIO()):
            self.shell.do_flag(f"{r} {c}")

        self.assertFalse(self.shell.board.cells[r][c].is_flagged)

    def test_reveal_with_invalid_args_does_not_crash(self):
        """
        Invalid arguments (non-integer or wrong arity) must not crash
        the shell. We only assert that it runs to completion.
        """
        buf = StringIO()
        with redirect_stdout(buf):
            # Examples of invalid input
            self.shell.do_reveal("abc def")
            self.shell.do_reveal("0")       # too few args
            self.shell.do_reveal("0 1 2")   # too many args

        output = buf.getvalue()
        # It's nice (but not required) if the implementation includes
        # some kind of 'invalid' wording; if not, you can loosen/remove
        # this assertion.
        self.assertTrue(
            output.strip() == "" or "invalid" in output.lower()
            or "error" in output.lower(),
            "Expected some graceful handling of invalid reveal args.",
        )

    def test_reveal_out_of_bounds_does_not_crash(self):
        """
        Coordinates outside the current board should be handled gracefully.
        """
        rows, cols = self.shell.board.rows, self.shell.board.cols
        buf = StringIO()
        with redirect_stdout(buf):
            self.shell.do_reveal(f"{rows} {cols}")  # definitely OOB

        # Just ensure no exception and the game is still playable
        self.assertEqual(self.shell.board.state, "PLAYING")


if __name__ == "__main__":
    unittest.main()
