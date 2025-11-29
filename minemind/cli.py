# minemind/cli.py

import cmd
from minemind.core.board import Board
from minemind.core.solver import MinemindSolver
from .render import display_board
from typing import List, Tuple, Any


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

        # Initialize the solver instance
        self.solver = MinemindSolver()

        # Show the fresh board
        display_board(self.board)

    # ------------------ Game Commands ------------------

    def do_new(self, arg):
        'Start a new game: new [beginner|intermediate|expert] or new <rows> <cols> <mines>'
        args = arg.split()
        
        if not args:
            self.board = Board(difficulty="beginner")
        elif len(args) == 1:
            self.board = Board(difficulty=args[0])
        elif len(args) == 3:
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
        
        print("Game reset. Ready to play.")
        display_board(self.board)

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

        # Bounds check
        if not (0 <= r < self.board.rows and 0 <= c < self.board.cols):
            print(
                f"Error: Coordinates ({r}, {c}) are outside the board "
                f"boundaries (0-{self.board.rows-1}, 0-{self.board.cols-1})."
            )
            return
        
        if self.board.state != "PLAYING":
            print(f"Cannot reveal. Game is already {self.board.state}.")
            display_board(self.board)
            return

        # Core logic execution
        self.board.reveal(r, c)
        
        # Check for game end state (output is handled inside board.py for now)
        if self.board.state != "PLAYING":
            print(f"Game over! Final state: {self.board.state}")
            # The renderer will show the final state (all mines)
            
        display_board(self.board)

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

        # Bounds check
        if not (0 <= r < self.board.rows and 0 <= c < self.board.cols):
            print(f"Error: Coordinates ({r}, {c}) are outside the board boundaries.")
            return
        
        if self.board.state != "PLAYING":
            print("Cannot flag. Game is over.")
            display_board(self.board)
            return

        # Core logic execution
        self.board.flag(r, c)
        
        # Show the updated board after flagging
        display_board(self.board)

    # ------------------ Utility Commands ------------------
    
    def do_solve(self, arg):
        'Ask the solver to find and apply all certain moves for the current board.'
        
        if self.board.state != "PLAYING":
            print(f"Cannot solve. Game is already {self.board.state}.")
            display_board(self.board)
            return

        print("--- Running Solver Step ---")
        
        # 1. Get certain moves from the solver
        moves: List[Tuple[int, int, str]] = self.solver.solve_step(self.board)

        if not moves:
            print("Solver found no logically certain moves. Time for manual play or quit.")
            display_board(self.board)
            return

        print(f"Solver: applying {len(moves)} certain move(s)...")
        
        # 2. Execute moves sequentially
        for r, c, action in moves:
            # Check game state before each move
            if self.board.state != "PLAYING":
                break 
                
            if action == "FLAG":
                print(f"  -> FLAG at ({r}, {c})")
                self.board.flag(r, c)
            elif action == "REVEAL":
                print(f"  -> REVEAL at ({r}, {c})")
                # Revealing a cell uses the same logic as the user's manual reveal
                self.board.reveal(r, c)
            else:
                print(f"  [WARN] Unknown solver action '{action}' at ({r}, {c})")

        # 3. Render the result
        display_board(self.board)
        
        if self.board.state != "PLAYING":
            print(f"Game over! Final state: {self.board.state}")


    def do_exit(self, arg):
        'Exit the shell: exit or quit'
        print("Exiting minemind. Goodbye!")
        return True

    def do_quit(self, arg):
        'Exit the shell: exit or quit'
        return self.do_exit(arg)


def main():
    MinemindShell().cmdloop()