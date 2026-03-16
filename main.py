# Cheese uwu

# Global constants for board's dimensions(the core and the start)
rows = 8
cols = 8

# --- BASE PIECE CLASS ---
class Piece:
    """Parent class that handles basic attributes and shared movement logic."""
    def __init__(self, color:str, position:tuple)-> None:
        self.color = color # "w" for White, "b" for Black
        self.position = position # Stored as (row, col)
        
    def __repr__(self):
        # Displays as "wR" (White Rook) or "bP" (Black Pawn) on the board
        return f"{self.color}{self.name}"
    
    def sliding_piece(self, board, offsets):
        """Logic for pieces that move in straight lines until blocked (Rook, Bishop, Queen)."""
        r, c = self.position
        moves = []
        for dr, dc in offsets:
            for i in range(1, 8):
                nr, nc = (r + (dr * i)), (c + (dc * i))
                if 0 <= nr < 8 and 0 <= nc < 8:
                    if board[nr][nc] == "--": # Empty square
                        moves.append((nr, nc))
                        continue
                    if board[nr][nc].color != self.color: # Enemy piece (capture)
                        moves.append((nr, nc))
                        break
                    else: # Friendly piece (blocked)
                        break
        return moves
    
    def stepping_piece(self, board, offsets):
        """Logic for pieces that move a fixed distance (Knight, King)."""
        r, c = self.position
        moves = []
        for dr, dc in offsets:
            nr, nc = (r + dr), (c + dc)
            if 0 <= nr < 8 and 0 <= nc < 8:
                # Can move if square is empty OR contains an enemy
                if board[nr][nc] == "--" or board[nr][nc].color != self.color:
                    moves.append((nr, nc))
        return moves

# SPECIFIC PIECE SUBCLASSES 
class Knight(Piece):
    name = "N"
    def get_possible_moves(self, board):
        offsets = [(-2, 1), (-1, 2), (1, 2), (2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1)] # offsets to determine the piece's movements
        return self.stepping_piece(board, offsets)
    
class Bishop(Piece):
    name = "B"
    def get_possible_moves(self, board):
        offsets = [(1,1), (1,-1), (-1,1), (-1,-1)]
        return self.sliding_piece(board, offsets)

class Rook(Piece):
    name = "R"
    def get_possible_moves(self, board):
        offsets = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        return self.sliding_piece(board, offsets)

class King(Piece):
    name = "K"
    def get_possible_moves(self, board):
        offsets = [(1,1), (1,0), (1, -1), (0, -1), (-1,-1), (-1,0), (-1,1), (0,1)]
        return self.stepping_piece(board, offsets)

class Queen(Piece):
    name = "Q"
    def get_possible_moves(self, board):
        # Queen = Rook + Bishop movement
        offsets = [(1,1), (1,-1), (-1,1), (-1,-1), (1, 0), (-1, 0), (0, 1), (0, -1)]
        return self.sliding_piece(board, offsets)

class Pawn(Piece): # This piece is actually problematic. 
    name = "P"

    def add_pawn_capture(self, board, r, c, dc, direction, moves):
        """Helper to check diagonal squares for enemy captures."""
        nr, nc = r + direction, c + dc
        if 0 <= nr < 8 and 0 <= nc < 8:
            target = board[nr][nc]
            if target != "--" and target.color != self.color:
                moves.append((nr, nc))

    def get_possible_moves(self, board):
        direction = 1 if self.color == "w" else -1
        r, c = self.position
        moves = []

        # 1. Forward movement (must be empty)
        nr = r + direction
        if 0 <= nr < 8 and board[nr][c] == "--":
            moves.append((nr, c))
            # Double move from start (row 1 for White, 6 for Black)
            start_rank = 1 if self.color == "w" else 6
            nr2 = r + 2 * direction
            if r == start_rank and 0 <= nr2 < 8 and board[nr2][c] == "--":
                moves.append((nr2, c))

        # 2. Diagonal Captures
        self.add_pawn_capture(board, r, c, +1, direction, moves)
        self.add_pawn_capture(board, r, c, -1, direction, moves)
        return moves

# Starting Point
def setup_board():
    """Creates an 8x8 nested list and populates it with Piece objects."""
    board = [[ "--" for _ in range(rows)] for _ in range(cols)]
    for r in [0, 1, 6, 7]:
        color = "w" if r < 2 else "b"
        for c in range(8):
            if r == 1 or r == 6:
                board[r][c] = Pawn(color, (r,c))
            elif r == 0 or r == 7:
                piece_order = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
                board[r][c] = piece_order[c](color, (r,c))
    return board

# Main Game Class
class Game:
    def __init__(self):
        self.board = setup_board()
        self.current_turn = "w"

    def display(self):
        """Prints the board with column/row indices for the user."""
        print("\n   0  1  2  3  4  5  6  7") # Column headers
        for i, row in enumerate(self.board):
            x = " ".join([(str(piece)) for piece in row])
            print(f"{i} {x}") # Row headers

    def move_piece(self, start_pos, end_pos):
        """Validates and executes a move. Handles win conditions and promotion."""
        r, c = start_pos
        nr, nc = end_pos
        
        # 1. Out of Bounds Check
        if not (0 <= r < 8 and 0 <= c < 8) or not (0 <= nr < 8 and 0 <= nc < 8):
            print("Error: Coordinates out of bounds!")
            return False
            
        piece = self.board[r][c]
        if piece == "--":
            print("Error: No piece selected.")
            return False

        # 2. Turn & Friendly Fire Check
        if piece.color != self.current_turn:
            print(f"Error: It's {self.current_turn}'s turn!")
            return False

        target = self.board[nr][nc]
        if target != "--" and target.color == piece.color:
            print("Error: Friendly fire not allowed.")
            return False

        # 3. Piece Move Rule Check
        if end_pos not in piece.get_possible_moves(self.board):
            print("Error: Invalid move for this piece.")
            return False

        # 4. EXECUTION (The actual move)
        self.board[nr][nc] = piece
        self.board[r][c] = "--"
        piece.position = (nr, nc)

        # 5. WIN CONDITION: King Capture
        if isinstance(target, King):
            self.display()
            print(f"\nGG! {piece.color.upper()} WINS BY KING CAPTURE!")
            exit()

        # 6. PAWN PROMOTION
        if isinstance(piece, Pawn):
            promotion_rank = 7 if piece.color == "w" else 0
            if nr == promotion_rank:
                self.board[nr][nc] = Queen(piece.color, (nr, nc))
                print(f"Promotion! Pawn transformed to Queen at {nr, nc}")

        # 7. SWITCH TURN
        self.current_turn = "b" if self.current_turn == "w" else "w"
        return True
    
    def engine(self):
        """Main game loop."""
        while True:
            self.display()
            try:
                # inputs coordinates like "1,0"
                start = tuple(map(int, input(f"\n({self.current_turn}) Move from (r,c): ").split(',')))
                end = tuple(map(int, input("To (r,c): ").split(',')))
                self.move_piece(start, end)
            except (ValueError, IndexError):
                print("Input error: Please type coordinates like: row,col (e.g., 1,0)")

#  START GAME 
if __name__ == "__main__":
    cheese_game = Game()
    cheese_game.engine()