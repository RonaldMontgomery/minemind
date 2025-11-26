import unittest
from minemind.core.board import Board, Cell 

class TestBoardInitialization(unittest.TestCase):
    
    # --- Tests for Cell Class Defaults ---
    
    def test_cell_initial_state(self):
        """Checks if a new Cell is created with correct defaults."""
        cell = Cell()
        self.assertFalse(cell.is_mine)
        self.assertFalse(cell.is_revealed)
        self.assertFalse(cell.is_flagged)
        self.assertEqual(cell.neighbor_mines, 0)

    # --- Tests for Board Dimensions and Mine Count ---
    
    def test_beginner_config(self):
        """Tests the standard Beginner configuration (9x9, 10 mines)."""
        board = Board(difficulty="beginner")
        self.assertEqual(board.rows, 9)
        self.assertEqual(board.cols, 9)
        self.assertEqual(board.mines, 10)
        self.assertEqual(board.total_cells, 81)
        self.assertEqual(board.state, "PLAYING")
        
    def test_expert_config(self):
        """Tests the standard Expert configuration (30x16, 99 mines)."""
        board = Board(difficulty="expert")
        self.assertEqual(board.rows, 30)
        self.assertEqual(board.cols, 16)
        self.assertEqual(board.mines, 99)
        
    def test_invalid_difficulty_defaults_to_beginner(self):
        """Tests that an invalid string falls back to the beginner configuration."""
        board = Board(difficulty="impossible")
        self.assertEqual(board.rows, 9)
        self.assertEqual(board.mines, 10)
        
    # --- Tests for Custom Configurations and Clamping ---
    
    def test_custom_density_calculation(self):
        """Tests mine calculation for a custom 20x20 board (15% density)."""
        # 20 * 20 = 400 total cells. 400 * 0.15 = 60 mines.
        board = Board(rows=20, cols=20)
        self.assertEqual(board.rows, 20)
        self.assertEqual(board.cols, 20)
        self.assertEqual(board.mines, 60)

    def test_mine_clamping(self):
        """Tests that the mine count is clamped to total_cells - 1."""
        # A 5x5 board has 25 cells. Requesting 30 mines should result in 24.
        board = Board(rows=5, cols=5, mines=30)
        self.assertEqual(board.total_cells, 25)
        self.assertEqual(board.mines, 24) 
        
    # --- Tests for Grid Structure Integrity ---
    
    def test_grid_initialization_size(self):
        """Tests that the cells attribute is a 2D grid of the correct size."""
        ROWS = 5
        COLS = 8
        board = Board(rows=ROWS, cols=COLS)
        self.assertEqual(len(board.cells), ROWS)
        self.assertEqual(len(board.cells[0]), COLS)
        
    def test_grid_contains_cell_objects(self):
        """Tests that every element in the grid is an instance of Cell."""
        board = Board(difficulty="beginner")
        self.assertIsInstance(board.cells[2][2], Cell)


if __name__ == '__main__':
    unittest.main()