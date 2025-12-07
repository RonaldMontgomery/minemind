# minemind/core/board.py 

import math
from dataclasses import dataclass
from typing import List, Optional, Union, Tuple
import random 
from collections import deque

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
    

class Board:
    """Manages the 2D grid of Cells and the overall game state."""
    
    STANDARD_CONFIGS = {
        "beginner": (9, 9, 10),
        "intermediate": (16, 16, 40),
        "expert": (30, 16, 99),
    }
    DEFAULT_DENSITY = 0.15  # 15% mine density for calculated custom boards

    def _get_config(self, rows: Optional[int], cols: Optional[int], 
                    mines: Optional[int], difficulty: str) -> Tuple[int, int, int]:
        """
        Determines the final (rows, cols, mines) configuration, handling 
        difficulty strings and custom dimensions/mine counts.
        """
        
        DEFAULT_ROWS, DEFAULT_COLS, DEFAULT_MINES = self.STANDARD_CONFIGS["beginner"]

        # 1. Handle standard difficulty setting
        if difficulty in self.STANDARD_CONFIGS and rows is None and cols is None:
            return self.STANDARD_CONFIGS[difficulty]
        
        # 2. Handle invalid difficulty with NO custom sizes
        is_custom_size_provided = rows is not None or cols is not None
        if difficulty not in self.STANDARD_CONFIGS and not is_custom_size_provided:
             return DEFAULT_ROWS, DEFAULT_COLS, DEFAULT_MINES 
        
        # 3. Handle custom dimensions
        final_rows = rows if isinstance(rows, int) and rows > 0 else DEFAULT_ROWS
        final_cols = cols if isinstance(cols, int) and cols > 0 else DEFAULT_COLS
        total_cells = final_rows * final_cols
        
        # 4. Calculate or clamp the mine count
        if mines is None:
            final_mines = math.floor(total_cells * self.DEFAULT_DENSITY)
        else:
            final_mines = mines
            
        final_mines = min(final_mines, total_cells - 1) 
        final_mines = max(final_mines, 0)
        
        return final_rows, final_cols, final_mines

    def __init__(self, rows: Optional[int] = None, cols: Optional[int] = None, 
                 mines: Optional[int] = None, difficulty: str = "beginner"):
        
        # Determine final configuration
        final_rows, final_cols, final_mines = self._get_config(rows, cols, mines, difficulty)

        self.rows = final_rows
        self.cols = final_cols
        self.mines = final_mines
        self.total_cells = final_rows * final_cols
        self.state = "PLAYING"
        self.mines_placed = False # Flag for deferred setup

        # Initialize the grid of Cell objects
        self.cells: List[List[Cell]] = []
        for r in range(self.rows):
            row = []
            for c in range(self.cols):
                row.append(Cell())
            self.cells.append(row)
            
        # print(f"Initialized board: {self.rows}x{self.cols} with {self.mines} mines.")
        
    # --- CORE LOGIC ---

    def _get_neighbors_coords(self, r: int, c: int) -> List[Tuple[int, int]]:
        """
        Helper to get all 8 neighbor coordinates, checking board bounds.
        Used for mine placement, counting, and flood-fill.
        """
        nbrs: List[Tuple[int, int]] = []
        
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                # Skip the center cell itself
                if dr == 0 and dc == 0:
                    continue
                    
                nr, nc = r + dr, c + dc 
                
                # Check bounds: ensure neighbor is on the board
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    nbrs.append((nr, nc))
                    
        return nbrs

    def _place_mines(self, safe_r: int, safe_c: int) -> None:
        """
        Randomly places self.mines, guaranteeing the safe area (first click 
        and its 8 neighbors) is clear.
        """
        
        # 1. Define the safe zone
        safe_coords = set(self._get_neighbors_coords(safe_r, safe_c))
        safe_coords.add((safe_r, safe_c))
        
        # 2. Create pool of all possible coordinates
        all_coords = [(r, c) for r in range(self.rows) for c in range(self.cols)]
        
        # 3. Exclude the safe zone
        mine_candidates = [coords for coords in all_coords if coords not in safe_coords]
        
        # Adjust mine count if the safe zone is too large for the board size
        if self.mines > len(mine_candidates):
            self.mines = len(mine_candidates) 

        # 4. Random selection
        mine_locations = random.sample(mine_candidates, self.mines)
        
        # 5. Set the mines on the cells
        for r, c in mine_locations:
            self.cells[r][c].is_mine = True
        
        self.mines_placed = True
        print(f"Mines placed: {self.mines} mines set.")


    def _calculate_neighbor_counts(self) -> None:
        """
        Iterates over all cells and computes the neighbor_mines count.
        Called once after mines are placed.
        """
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.cells[r][c]
                
                # We only need to count for non-mine cells
                if not cell.is_mine:
                    mine_count = 0
                    
                    # Iterate over neighbors using the helper method
                    for nr, nc in self._get_neighbors_coords(r, c):
                        neighbor_cell = self.cells[nr][nc]
                        if neighbor_cell.is_mine:
                            mine_count += 1
                            
                    cell.neighbor_mines = mine_count


    # --- Game Flow  ---

    def reveal(self, r: int, c: int) -> None:
        """Handles the user clicking a cell to reveal it."""
        from collections import deque

        # 1. Input/State Validation
        if not (0 <= r < self.rows and 0 <= c < self.cols and self.state == "PLAYING"):
            return

        cell = self.cells[r][c]
        if cell.is_revealed or cell.is_flagged:
            return
            
        # 2. Deferred Setup (FIRST CLICK LOGIC)
        if not self.mines_placed:
            self._place_mines(r, c)
            self._calculate_neighbor_counts()
            # Note: self.mines_placed is set to True inside _place_mines
            
        # 3. Mine Check (LOSE CONDITION)
        if cell.is_mine:
            cell.is_revealed = True
            self.state = "LOST"
            # print("GAME OVER: You hit a mine!") # CLI handles user output
            return
            
        # 4. Reveal & Flood-Fill
        cell.is_revealed = True
        
        if cell.neighbor_mines == 0:
            self._flood_reveal(r, c, deque)
            
        # 5. Check Win Condition
        self._check_win_condition()

    def flag(self, r: int, c: int) -> None:
        """Toggles the flag state of an unrevealed cell."""
        if self.state == "PLAYING" and 0 <= r < self.rows and 0 <= c < self.cols:
            cell = self.cells[r][c]
            if not cell.is_revealed:
                cell.is_flagged = not cell.is_flagged

    def _flood_reveal(self, start_r: int, start_c: int, deque_class) -> None:
        """
        Performs a Breadth-First Search (BFS) to cascade reveals from a zero cell.
        """
        queue = deque_class([(start_r, start_c)])
        
        while queue:
            r, c = queue.popleft()
            
            # Iterate over neighbors
            for nr, nc in self._get_neighbors_coords(r, c):
                neighbor_cell = self.cells[nr][nc]
                
                # Skip if already revealed or flagged
                if neighbor_cell.is_revealed or neighbor_cell.is_flagged:
                    continue
                    
                neighbor_cell.is_revealed = True
                
                # ONLY continue the flood (add to queue) if the neighbor is also a zero
                if neighbor_cell.neighbor_mines == 0:
                    queue.append((nr, nc))

    def _check_win_condition(self) -> None:
        """Checks if all non-mine cells have been revealed."""
        hidden_non_mines = 0
        
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.cells[r][c]
                
                # Count hidden cells that are NOT mines
                if not cell.is_revealed and not cell.is_mine:
                    hidden_non_mines += 1
                    
        if hidden_non_mines == 0:
            self.state = "WON"

def reveal(self, r: int, c: int) -> None:
    """Handles the user clicking a cell to reveal it."""
    
    # 1. Input/State Validation
    if not (0 <= r < self.rows and 0 <= c < self.cols and self.state == "PLAYING"):
        return

    cell = self.cells[r][c]
    if cell.is_revealed or cell.is_flagged:
        return
        
    # 2. Deferred Setup
    if not self.mines_placed:
        self._place_mines(r, c)
        self._calculate_neighbor_counts()
        # self.mines_placed is set to True inside _place_mines
        
    # 3. Mine Check (LOSE CONDITION)
    if cell.is_mine:
        cell.is_revealed = True
        self.state = "LOST"
        print("GAME OVER: You hit a mine!")
        return
        
    # 4. Reveal & fill
    cell.is_revealed = True
    
    if cell.neighbor_mines == 0:
        self._flood_reveal(r, c)
        
    # 5. Check Win Condition
    self._check_win_condition()

def _flood_reveal(self, start_r: int, start_c: int) -> None:
    """
    Performs a Breadth-First Search (BFS) to cascade reveals from a zero cell.
    """
    queue = deque([(start_r, start_c)])
    
    while queue:
        r, c = queue.popleft()
        
        # Iterate over neighbors
        for nr, nc in self._get_neighbors_coords(r, c):
            neighbor_cell = self.cells[nr][nc]
            
            # Skip if already revealed or flagged
            if neighbor_cell.is_revealed or neighbor_cell.is_flagged:
                continue
                
            neighbor_cell.is_revealed = True
            
            # ONLY continue the flood (add to queue) if the neighbor is also a zero
            if neighbor_cell.neighbor_mines == 0:
                queue.append((nr, nc))
                
            # If neighbor_cell.neighbor_mines > 0, we stop the flood at that cell.

def _check_win_condition(self) -> None:
    """Checks if all non-mine cells have been revealed."""
    hidden_cells = 0
    
    for r in range(self.rows):
        for c in range(self.cols):
            cell = self.cells[r][c]
            
            # count hidden cells that are NOT mines
            if not cell.is_revealed and not cell.is_mine:
                hidden_cells += 1
                
    if hidden_cells == 0:
        self.state = "WON"
        print("CONGRATULATIONS: You won the game!")


def flag(self, r: int, c: int) -> None:
    """Toggles the flag state of an unrevealed cell."""
    if self.state == "PLAYING":
        cell = self.cells[r][c]
        if not cell.is_revealed:
            cell.is_flagged = not cell.is_flagged                


# --- Example Main for Local Testing ---
def main():
    # Example setup for a tiny board for quick debugging:
    b = Board(rows=5, cols=5, mines=3)
    
    # Simulate first click (this triggers mine placement)
    b._place_mines(safe_r=2, safe_c=2)
    b._calculate_neighbor_counts()
    
if __name__ == '__main__':
    main()