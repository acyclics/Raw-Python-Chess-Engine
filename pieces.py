from moves import is_check
from utils import generate_diagonal_indexes, generate_translational_indexes


class Piece():

    def __init__(self, name, symbol, color, pos, king):
        self.name = name
        self.symbol = symbol
        self.color = color
        self.pos = pos
        self.alive = True
        self.king = king
        self.history = [(pos, 0)]

    def captured(self):
        self.alive = False
    
    def revive(self):
        self.alive = True

    def is_alive(self):
        if self.alive:
            return True
        else:
            return False

    def update_pos(self, i, j):
        old_pos = list(self.pos)
        self.pos = [i, j]
        return old_pos
    
    def update_history(self, pos, total_moves):
        self.history.append((pos, total_moves))


class ChessPiece(Piece):
    
    def promote(self):
        self.name = "queen"
        self.symbol = "Q"
    
    def unpromote(self):
        self.name = "pawn"
        self.symbol = "P"

    def is_king_safe(self, move, board):
        if self.name == "king":
            king_pos = [self.pos[0] + move[0], self.pos[1] + move[1]]
        else:
            king_pos = self.king.pos
        next_pos = [self.pos[0] + move[0], self.pos[1] + move[1]]
        
        og_piece = board[next_pos[0]][next_pos[1]]
        board[next_pos[0]][next_pos[1]] = board[self.pos[0]][self.pos[1]]
        board[self.pos[0]][self.pos[1]] = Piece("empty", "E", "E", None, None)

        king_check = is_check(board, self.color, king_pos)

        board[self.pos[0]][self.pos[1]] = board[next_pos[0]][next_pos[1]]
        board[next_pos[0]][next_pos[1]] = og_piece

        return not king_check

    def check_for_enpassant(self, state):
        assert self.name == "pawn"

        board = state['board']
        total_moves = state['total_moves']

        i = self.pos[0]
        j = self.pos[1]

        enpassants = []

        if self.color == "W":
            if (i == 3 and j - 1 >= 0 and
                board[i - 1][j - 1].symbol == 'E' and
                board[i][j - 1].symbol == 'P' and board[i][j - 1].color != 'W'):
                # en passant
                if board[i][j - 1].history[-1][1] == total_moves and board[i][j - 1].history[-2][0][0] == 1:
                    enpassants.append([-1, -1])
            if (i == 3 and j + 1 <= 7 and
                board[i - 1][j + 1].symbol == 'E' and
                board[i][j + 1].symbol == 'P' and board[i][j + 1].color != 'W'):
                # en passant
                if board[i][j + 1].history[-1][1] == total_moves and board[i][j+ 1].history[-2][0][0] == 1:
                    enpassants.append([-1, 1])
        else:
            if (i == 4 and j - 1 >= 0 and
                board[i + 1][j - 1].symbol == 'E' and
                board[i][j - 1].symbol == 'P' and board[i][j - 1].color != 'B'):
                # en passant
                if board[i][j - 1].history[-1][1] == total_moves and board[i][j - 1].history[-2][0][0] == 6:
                    enpassants.append([1, -1])
            if (i == 4 and j + 1 <= 7 and
                board[i + 1][j + 1].symbol == 'E' and
                board[i][j + 1].symbol == 'P' and board[i][j + 1].color != 'B'):
                # en passant
                if board[i][j + 1].history[-1][1] == total_moves and board[i][j+ 1].history[-2][0][0] == 6:
                    enpassants.append([1, 1])
                
        return enpassants

    def get_castling_rights(self, state):
        assert self.name == "king"

        board = state['board']
        total_moves = state['total_moves']

        i = self.pos[0]
        j = self.pos[1]
        
        castling = [False, False]   # queenside, kingside

        if self.color == "W":
            if len(self.history) == 1 and board[7][7].symbol == "R" and len(board[7][7].history) == 1:
                castling[1] = True
            
            if len(self.history) == 1 and board[7][0].symbol == "R" and len(board[7][0].history) == 1:
                castling[0] = True
        
        if self.color == "B":
            if len(self.history) == 1 and board[0][7].symbol == "R" and len(board[0][7].history) == 1:
                castling[1] = True
            
            if len(self.history) == 1 and board[0][0].symbol == "R" and len(board[0][0].history) == 1:
                castling[0] = True
        
        return castling

    def get_possible_moves(self, state):
        """
            Get all possible moves for the piece
            Does not account for checks. So perform check after this.
        """
        board = state['board']
        total_moves = state['total_moves']

        i = self.pos[0]
        j = self.pos[1]

        if self.name == "pawn":
            possible_moves = [None, None, None, None, None, None]
            possible_moves_mask = [False, False, False, False, False, False]
            is_capture = [False, False, False, False, False, False]

            if not self.alive:
                return possible_moves, possible_moves_mask, is_capture

            if self.color == "W":
                if i - 1 >= 0 and board[i - 1][j].symbol == 'E' and self.is_king_safe([-1, 0], board):
                    possible_moves[0] = [-1, 0]
                    possible_moves_mask[0] = True
                if i - 1 >= 0 and j + 1 <=  7 and board[i - 1][j + 1].symbol != 'E' and board[i - 1][j + 1].color != 'W' and self.is_king_safe([-1, 1], board):
                    possible_moves[1] = [-1, 1]
                    possible_moves_mask[1] = True
                    is_capture[1] = True
                if i - 1 >= 0 and j - 1 >= 0 and board[i - 1][j - 1].symbol != 'E' and board[i - 1][j - 1].color != 'W' and self.is_king_safe([-1, -1], board):
                    possible_moves[2] = [-1, -1]
                    possible_moves_mask[2] = True
                    is_capture[2] = True
                if i == 6:
                    if i - 2 >= 0 and board[i - 2][j].symbol == 'E' and self.is_king_safe([-2, 0], board):
                        possible_moves[3] = [-2, 0]
                        possible_moves_mask[3] = True
                if (i == 3 and j - 1 >= 0 and
                    board[i - 1][j - 1].symbol == 'E' and
                    self.is_king_safe([-1, -1], board) and
                    board[i][j - 1].symbol == 'P' and board[i][j - 1].color != 'W'):
                    # en passant
                    if board[i][j - 1].history[-1][1] == total_moves and board[i][j - 1].history[-2][0][0] == 1:
                        possible_moves[4] = [-1, -1]
                        possible_moves_mask[4] = True
                        is_capture[4] = True
                if (i == 3 and j + 1 <= 7 and
                    board[i - 1][j + 1].symbol == 'E' and
                    self.is_king_safe([-1, 1], board) and
                    board[i][j + 1].symbol == 'P' and board[i][j + 1].color != 'W'):
                    # en passant
                    if board[i][j + 1].history[-1][1] == total_moves and board[i][j+ 1].history[-2][0][0] == 1:
                        possible_moves[5] = [-1, 1]
                        possible_moves_mask[5] = True
                        is_capture[5] = True
            else:
                if i + 1 <= 7 and board[i + 1][j].symbol == 'E' and self.is_king_safe([1, 0], board):
                    possible_moves[0] = [1, 0]
                    possible_moves_mask[0] = True
                if i + 1 <= 7 and j + 1 <= 7 and board[i + 1][j + 1].symbol != 'E' and board[i + 1][j + 1].color != 'B' and self.is_king_safe([1, 1], board):
                    possible_moves[1] = [1, 1]
                    possible_moves_mask[1] = True
                    is_capture[1] = True
                if i + 1 <= 7 and j - 1 >= 0 and board[i + 1][j - 1].symbol != 'E' and board[i + 1][j - 1].color != 'B' and self.is_king_safe([1, -1], board):
                    possible_moves[2] = [1, -1]
                    possible_moves_mask[2] = True
                    is_capture[2] = True
                if i == 1:
                    if i + 2 <= 7 and board[i + 2][j].symbol == 'E' and self.is_king_safe([2, 0], board):
                        possible_moves[3] = [2, 0]
                        possible_moves_mask[3] = True
                if (i == 4 and j - 1 >= 0 and
                    board[i + 1][j - 1].symbol == 'E' and
                    self.is_king_safe([1, -1], board) and
                    board[i][j - 1].symbol == 'P' and board[i][j - 1].color != 'B'):
                    # en passant
                    if board[i][j - 1].history[-1][1] == total_moves and board[i][j - 1].history[-2][0][0] == 6:
                        possible_moves[4] = [1, -1]
                        possible_moves_mask[4] = True
                        is_capture[4] = True
                if (i == 4 and j + 1 <= 7 and
                    board[i + 1][j + 1].symbol == 'E' and
                    self.is_king_safe([1, 1], board) and
                    board[i][j + 1].symbol == 'P' and board[i][j + 1].color != 'B'):
                    # en passant
                    if board[i][j + 1].history[-1][1] == total_moves and board[i][j+ 1].history[-2][0][0] == 6:
                        possible_moves[5] = [1, 1]
                        possible_moves_mask[5] = True
                        is_capture[5] = True
        
        if self.name == "rook":
            possible_moves = [None for _ in range(7 + 7)]
            possible_moves_mask = [False for _ in range(7 + 7)]
            is_capture = [False for _ in range(7 + 7)]
            mv_id = 0

            if not self.alive:
                return possible_moves, possible_moves_mask, is_capture

            def rook_move(sym, move, mv_id, cl):
                if sym == 'E' and self.is_king_safe(move, board):
                    possible_moves[mv_id] = move
                    possible_moves_mask[mv_id] = True
                if sym != 'E' and cl != self.color and self.is_king_safe(move, board):
                    possible_moves[mv_id] = move
                    possible_moves_mask[mv_id] = True
                    is_capture[mv_id] = True
            
            vert_indexes = generate_translational_indexes(i)

            for vert_index in vert_indexes:
                occluded = False
                for y in vert_index:
                    if not occluded:
                        sym = board[y][j].symbol
                        cl = board[y][j].color
                        move = [y - i, 0]
                        rook_move(sym, move, mv_id, cl)
                        if sym != 'E':
                            occluded = True
                    mv_id += 1

            hori_indexes = generate_translational_indexes(j)

            for hori_index in hori_indexes:
                occluded = False
                for x in hori_index:
                    if not occluded:
                        sym = board[i][x].symbol
                        cl = board[i][x].color
                        move = [0, x - j]
                        rook_move(sym, move, mv_id, cl)
                        if sym != 'E':
                            occluded = True
                    mv_id += 1
        
        if self.name == "bishop":
            possible_moves = [None for _ in range(7 + 7)]
            possible_moves_mask = [False for _ in range(7 + 7)]
            is_capture = [False for _ in range(7 + 7)]
            mv_id = 0

            if not self.alive:
                return possible_moves, possible_moves_mask, is_capture

            def bishop_move(sym, move, mv_id, cl):
                if sym == 'E' and self.is_king_safe(move, board):
                    possible_moves[mv_id] = move
                    possible_moves_mask[mv_id] = True
                if sym != 'E' and cl != self.color and self.is_king_safe(move, board):
                    possible_moves[mv_id] = move
                    possible_moves_mask[mv_id] = True
                    is_capture[mv_id] = True
            
            diagonal_indexes = generate_diagonal_indexes(i, j)

            for diagonal_index in diagonal_indexes:
                occluded = False
                for (y, x) in diagonal_index:
                    if not occluded:
                        sym = board[y][x].symbol
                        cl = board[y][x].color
                        move = [y - i, x - j]
                        bishop_move(sym, move, mv_id, cl)
                        if sym != 'E':
                            occluded = True
                    mv_id += 1

        if self.name == "queen":
            possible_moves = [None for _ in range(7 * 8)]
            possible_moves_mask = [False for _ in range(7 * 8)]
            is_capture = [False for _ in range(7 * 8)]
            mv_id = 0

            if not self.alive:
                return possible_moves, possible_moves_mask, is_capture

            def queen_move(sym, move, mv_id, cl):
                if sym == 'E' and self.is_king_safe(move, board):
                    possible_moves[mv_id] = move
                    possible_moves_mask[mv_id] = True
                if sym != 'E' and cl != self.color and self.is_king_safe(move, board):
                    possible_moves[mv_id] = move
                    possible_moves_mask[mv_id] = True
                    is_capture[mv_id] = True
            
            vert_indexes = generate_translational_indexes(i)

            for vert_index in vert_indexes:
                occluded = False
                for y in vert_index:
                    if not occluded:
                        sym = board[y][j].symbol
                        cl = board[y][j].color
                        move = [y - i, 0]
                        queen_move(sym, move, mv_id, cl)
                        if sym != 'E':
                            occluded = True
                    mv_id += 1

            hori_indexes = generate_translational_indexes(j)

            for hori_index in hori_indexes:
                occluded = False
                for x in hori_index:
                    if not occluded:
                        sym = board[i][x].symbol
                        cl = board[i][x].color
                        move = [0, x - j]
                        queen_move(sym, move, mv_id, cl)
                        if sym != 'E':
                            occluded = True
                    mv_id += 1
        
            diagonal_indexes = generate_diagonal_indexes(i, j)

            for diagonal_index in diagonal_indexes:
                occluded = False
                for (y, x) in diagonal_index:
                    if not occluded:
                        sym = board[y][x].symbol
                        cl = board[y][x].color
                        move = [y - i, x - j]
                        queen_move(sym, move, mv_id, cl)
                        if sym != 'E':
                            occluded = True
                    mv_id += 1
        
        if self.name == "knight":
            possible_moves = [
                [-2, 1], [-2, -1], [-1, -2], [-1, 2], [1, -2], [1, 2], [2, -1], [2, 1]
            ]
            possible_moves_mask = [False for _ in range(8)]
            is_capture = [False for _ in range(8)]

            if not self.alive:
                return possible_moves, possible_moves_mask, is_capture

            def knight_move(sym, move, mv_id, cl):
                if sym == 'E' and self.is_king_safe(move, board):
                    possible_moves_mask[mv_id] = True
                if sym != 'E' and cl != self.color and self.is_king_safe(move, board):
                    possible_moves_mask[mv_id] = True
                    is_capture[mv_id] = True

            for idx in range(8):
                move = possible_moves[idx]
                if i + move[0] >= 0 and i + move[0] <= 7 and j + move[1] >= 0 and j + move[1] <= 7:
                    sym = board[i + move[0]][j + move[1]].symbol
                    cl = board[i + move[0]][j + move[1]].color
                    knight_move(sym, move, idx, cl)
           
        if self.name == "king":
            possible_moves = [[-1, -1], [-1, 0], [0, -1], [1, 1], [1, 0], [0, 1], [-1, 1], [1, -1], [0, 6 - j], [0, 2 - j]]
            possible_moves_mask = [False for _ in range(10)]
            is_capture = [False for _ in range(10)]

            if not self.alive:
                return possible_moves, possible_moves_mask, is_capture

            def king_move(sym, move, mv_id, cl):
                if sym == 'E' and self.is_king_safe(move, board):
                    possible_moves_mask[mv_id] = True
                if sym != 'E' and cl != self.color and self.is_king_safe(move, board):
                    possible_moves_mask[mv_id] = True
                    is_capture[mv_id] = True
            
            for idx in range(8):
                move = possible_moves[idx]
                if i + move[0] >= 0 and i + move[0] <= 7 and j + move[1] >= 0 and j + move[1] <= 7:
                    sym = board[i + move[0]][j + move[1]].symbol
                    cl = board[i + move[0]][j + move[1]].color
                    king_move(sym, move, idx, cl)
            
            if self.color == "W":
                if self.is_king_safe([0, 0], board) and len(self.history) == 1:
                    if board[7][7].symbol == "R" and len(board[7][7].history) == 1:
                        occluded = False
                        for ep in range(5, 7):
                            if board[7][ep].symbol != 'E' or not self.is_king_safe([0, ep - j], board):
                                occluded = True
                        if not occluded:
                            possible_moves_mask[8] = True
                    if board[7][0].symbol == "R" and len(board[7][0].history) == 1:
                        occluded = False
                        for ep in range(1, 4):
                            if board[7][ep].symbol != 'E' or not self.is_king_safe([0, ep - j], board):
                                occluded = True
                        if not occluded:
                            possible_moves_mask[9] = True
            else:
                if self.is_king_safe([0, 0], board) and len(self.history) == 1:
                    if board[0][7].symbol == "R" and len(board[0][7].history) == 1:
                        occluded = False
                        for ep in range(5, 7):
                            if board[0][ep].symbol != 'E' or not self.is_king_safe([0, ep - j], board):
                                occluded = True
                        if not occluded:
                            possible_moves_mask[8] = True
                    if board[0][0].symbol == "R" and len(board[0][0].history) == 1:
                        occluded = False
                        for ep in range(1, 4):
                            if board[0][ep].symbol != 'E' or not self.is_king_safe([0, ep - j], board):
                                occluded = True
                        if not occluded:
                            possible_moves_mask[9] = True
        
        return possible_moves, possible_moves_mask, is_capture
