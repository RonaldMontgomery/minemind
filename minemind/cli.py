# minemind/cli.py

import cmd
from minemind.core.board import Board
from minemind.render import display_board


class MinemindShell(cmd.Cmd):
    """
    Implements the custom REPL for the minemind game, handling user input, 
    command parsing, and state management.
    """
    
    intro = 'Welcome to minemind. Type help or ? to list commands.\n'
    prompt = '(minemind) '

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Create a default beginner board immediately upon starting the shell
        print("Starting new Beginner game...")
        self.board = Board(difficulty="beginner")

    # ------------------ Game Commands ------------------

    def do_new(self, arg):
        'Start a new game: new [beginner|intermediate|expert] or new <rows> <cols> <mines>'
        args = arg.split()
        
        if not args:
            # Default to beginner if no arguments are given
            self.board = Board(difficulty="beginner")
        elif len(args) == 1:
            # New game by difficulty string (e.g., 'new intermediate')
            self.board = Board(difficulty=args[0])
        elif len(args) == 3:
            # New game by custom size (e.g., 'new 10 10 15')
            try:
                rows = int(args[0])
                cols = int(args[1])
                mines = int(args[2])
                self.board = Board(rows=rows, cols=cols, mines=mines, difficulty="custom")
            except ValueError:
                print("Error: Custom dimensions/mines must be integers.")
                return
        else:
            print("Error: Usage is 'new [difficulty]' or 'new <rows> <cols> <mines>'")
            return
        
        # After creating a new board, render it (Next step!)
        # self._render_board() 
        print(f"Game reset. Ready to play.")


    def do_reveal(self, arg):
        'Reveal a cell: reveal <row> <col>'
        
        args = arg.split()
        if len(args) != 2:
            print("Error: Usage is 'reveal <row> <col>'")
            return

        try:
            r = int(args[0])
            c = int(args[1])
        except ValueError:
            print("Error: Coordinates must be integers.")
            return

        # Check bounds before calling the board
        if not (0 <= r < self.board.rows and 0 <= c < self.board.cols):
            print(f"Error: Coordinates ({r}, {c}) are outside the board boundaries (0-{self.board.rows-1}, 0-{self.board.cols-1}).")
            return
        
        if self.board.state != "PLAYING":
            print(f"Cannot reveal. Game is already {self.board.state}.")
            return

        # Core logic execution
        self.board.reveal(r, c)
        
        # NOTE: Rendering the board happens here (next step!)
        # self._render_board() 
        
        # Check for game end state (output is handled inside board.py for now)
        if self.board.state != "PLAYING":
            print(f"Game over! Final state: {self.board.state}")
            # Logic to reveal the whole board goes here.

    def do_flag(self, arg):
        'Toggle flag on a cell: flag <row> <col>'
        
        args = arg.split()
        if len(args) != 2:
            print("Error: Usage is 'flag <row> <col>'")
            return

        try:
            r = int(args[0])
            c = int(args[1])
        except ValueError:
            print("Error: Coordinates must be integers.")
            return

        # Check bounds
        if not (0 <= r < self.board.rows and 0 <= c < self.board.cols):
            print(f"Error: Coordinates ({r}, {c}) are outside the board boundaries.")
            return
        
        if self.board.state != "PLAYING":
            print(f"Cannot flag. Game is over.")
            return

        # Core logic execution
        self.board.flag(r, c)
        
        # NOTE: Rendering the board happens here (next step!)
        # self._render_board() 

    # ------------------ Utility Commands ------------------
    
    def do_solve(self, arg):
        'Start the solver for the current board.'
        # This will eventually call the logic in core/solver.py
        print("Solver activated.")

    def do_exit(self, arg):
        'Exit the shell: exit or quit'
        return True # Quits the Cmd loop

    def do_quit(self, arg):
        'Exit the shell: exit or quit'
        return self.do_exit(arg)

# ------------------ Main Entry Point ------------------

def main():
    MinemindShell().cmdloop()