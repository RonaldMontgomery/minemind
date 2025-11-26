# minemind/core/board.py

import math
from dataclasses import dataclass
from typing import List, Optional, Union


@dataclass
class Cell:
    """Represents the state of a single square on the Minesweeper board."""
    
    # Structural state
    is_mine: bool = False
    neighbor_mines: int = 0
    
    # User-facing state
    is_revealed: bool = False
    is_flagged: bool = False
    
    def __repr__(self):
        # A simple representation for printing/debugging
        if self.is_revealed:
            return 'M' if self.is_mine else str(self.neighbor_mines)
        return 'F' if self.is_flagged else '#'
    
    # Property for easier access to coordinates (helpful for complex logic later)
    # self.coords = (r, c) # If you decide to add coordinates to the cell itself
    

class Board:
    """Manages the 2D grid of Cells and the overall game state."""
    
    STANDARD_CONFIGS = {
        "beginner": (9, 9, 10),
        "intermediate": (16, 16, 40),
        "expert": (30, 16, 99),
    }
    DEFAULT_DENSITY = 0.15  # 15% mine density for calculated custom boards

    # minemind/core/board.py (Snippet 4: _get_config FIX)

    def _get_config(self, rows: Optional[int], cols: Optional[int], 
                    mines: Optional[int], difficulty: str) -> tuple[int, int, int]:
        
        # Define the absolute default fallback (Beginner config)
        DEFAULT_ROWS, DEFAULT_COLS, DEFAULT_MINES = self.STANDARD_CONFIGS["beginner"]

        # 1. Handle standard difficulty setting
        if difficulty in self.STANDARD_CONFIGS and rows is None and cols is None:
            return self.STANDARD_CONFIGS[difficulty]
        
        # 2. If difficulty is invalid, but NO custom sizes were specified, use the absolute default.
        if difficulty not in self.STANDARD_CONFIGS and rows is None and cols is None:
            return DEFAULT_ROWS, DEFAULT_COLS, DEFAULT_MINES # ⬅️ FIX: Explicitly return standard config

        # 3. Handle custom dimensions (using provided or default if necessary)
        # If we reach here, either rows/cols were specified OR the difficulty was invalid, 
        # but we must proceed with calculating custom config based on default size.
        final_rows = rows if isinstance(rows, int) and rows > 0 else DEFAULT_ROWS
        final_cols = cols if isinstance(cols, int) and cols > 0 else DEFAULT_COLS
        
        # ... (rest of the mine calculation and clamping logic remains the same)
        total_cells = final_rows * final_cols
        
        # ... (calculate final_mines based on total_cells * DEFAULT_DENSITY or the given mines count)
        
        # ... (return final_rows, final_cols, final_mines)
        # Assuming the final calculation is robust and is what produced 12 mines.
        
        # Placeholder return for the fixed logic:
        # NOTE: You need to ensure the final return logic is reached after this fix.
        
        # Fallback Calculation (This is the section that runs when the difficulty is invalid 
        # BUT the user provided rows/cols, OR if they provided rows/cols alone)
        
        # Calculate or clamp the mine count
        if mines is None:
            final_mines = math.floor(total_cells * self.DEFAULT_DENSITY)
        else:
            final_mines = mines
            
        final_mines = min(final_mines, total_cells - 1) 
        final_mines = max(final_mines, 0)
        
        return final_rows, final_cols, final_mines
    
    def __init__(self, rows: Optional[int] = None, cols: Optional[int] = None, 
                 mines: Optional[int] = None, difficulty: str = "beginner"):
        
        # Determine final configuration using the helper method
        final_rows, final_cols, final_mines = self._get_config(rows, cols, mines, difficulty)

        self.rows = final_rows
        self.cols = final_cols
        self.mines = final_mines
        self.total_cells = final_rows * final_cols
        
        # Initial game state
        self.state = "PLAYING"
        
        # 2. Initialize the 2D grid of Cell objects
        self.cells: List[List[Cell]] = []
        for r in range(self.rows):
            row = []
            for c in range(self.cols):
                row.append(Cell()) # Creates an unrevealed, non-mine cell
            self.cells.append(row)
            
        print(f"Initialized board: {self.rows}x{self.cols} with {self.mines} mines.")
        
        # Placeholder for the next step:
        # self._place_mines() 
        # self._calculate_neighbor_counts()


def main():
    # Test cases:
    Board(difficulty="intermediate")  # Standard intermediate
    Board(rows=10, cols=10)           # Custom 10x10, uses 15% density (15 mines)
    Board(rows=5, cols=5, mines=2)    # Custom 5x5, 2 mines

if __name__ == '__main__':
    main()