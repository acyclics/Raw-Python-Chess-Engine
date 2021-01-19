from pieces import Piece, ChessPiece
from moves import is_check


class ChessGame():

    def __init__(self):
        self._create_pieces()
        self._create_board()
        self.total_moves = 0
    
    def _create_pieces(self):
        self.wking = wking = ChessPiece("king", "K", "W", [7, 4], None)
        self.bking = bking = ChessPiece("king", "K", "B", [0, 4], None)

        self.white_pieces = [
            ChessPiece("pawn", "P", "W", [6, 0], wking),
            ChessPiece("pawn", "P", "W", [6, 1], wking),
            ChessPiece("pawn", "P", "W", [6, 2], wking),
            ChessPiece("pawn", "P", "W", [6, 3], wking),
            ChessPiece("pawn", "P", "W", [6, 4], wking),
            ChessPiece("pawn", "P", "W", [6, 5], wking),
            ChessPiece("pawn", "P", "W", [6, 6], wking),
            ChessPiece("pawn", "P", "W", [6, 7], wking),
            ChessPiece("rook", "R", "W", [7, 0], wking),
            ChessPiece("knight", "N", "W", [7, 1], wking),
            ChessPiece("bishop", "B", "W", [7, 2], wking),
            ChessPiece("queen", "Q", "W", [7, 3], wking),
            wking,
            ChessPiece("bishop", "B", "W", [7, 5], wking),
            ChessPiece("knight", "N", "W", [7, 6], wking),
            ChessPiece("rook", "R", "W", [7, 7], wking)
        ]
        self.black_pieces = [
            ChessPiece("pawn", "P", "B", [1, 0], bking),
            ChessPiece("pawn", "P", "B", [1, 1], bking),
            ChessPiece("pawn", "P", "B", [1, 2], bking),
            ChessPiece("pawn", "P", "B", [1, 3], bking),
            ChessPiece("pawn", "P", "B", [1, 4], bking),
            ChessPiece("pawn", "P", "B", [1, 5], bking),
            ChessPiece("pawn", "P", "B", [1, 6], bking),
            ChessPiece("pawn", "P", "B", [1, 7], bking),
            ChessPiece("rook", "R", "B", [0, 0], bking),
            ChessPiece("knight", "N", "B", [0, 1], bking),
            ChessPiece("bishop", "B", "B", [0, 2], bking),
            ChessPiece("queen", "Q", "B", [0, 3], bking),
            bking,
            ChessPiece("bishop", "B", "B", [0, 5], bking),
            ChessPiece("knight", "N", "B", [0, 6], bking),
            ChessPiece("rook", "R", "B", [0, 7], bking)
        ]
        self.empty_piece = self.create_empty_piece()

    def create_empty_piece(self):
        return Piece("empty", "E", "E", None, None)

    def _create_board(self):
        self.board = [
            [self.black_pieces[i] for i in range(8, 16)],
            [self.black_pieces[i] for i in range(0, 8)],
            [self.empty_piece for _ in range(8)],
            [self.empty_piece for _ in range(8)],
            [self.empty_piece for _ in range(8)],
            [self.empty_piece for _ in range(8)],
            [self.white_pieces[i] for i in range(0, 8)],
            [self.white_pieces[i] for i in range(8, 16)]
        ]
    
    def get_state(self):
        state = {
            'board': self.board,
            'total_moves': self.total_moves
        }
        return state

    def generate_all_possible_moves(self, color):
        all_moves = [None for _ in range(16)]
        if color == "W":
            for idx, white_piece in enumerate(self.white_pieces):
                possible_moves, possible_moves_mask, is_capture = white_piece.get_possible_moves(self.get_state())
                all_moves[idx] = {
                    'name': white_piece.name,
                    'possible_moves': possible_moves,
                    'possible_moves_mask': possible_moves_mask,
                    'is_capture': is_capture
                }
        else:
            for idx, black_piece in enumerate(self.black_pieces):
                possible_moves, possible_moves_mask, is_capture = black_piece.get_possible_moves(self.get_state())
                all_moves[idx] = {
                    'name': black_piece.name,
                    'possible_moves': possible_moves,
                    'possible_moves_mask': possible_moves_mask,
                    'is_capture': is_capture
                }
        return all_moves
    
    def handle_capture(self, from_pos, to_pos, move_index, info):
        """
            Specifically to handle cases like en passant
        """
        attacker = self.board[from_pos[0]][from_pos[1]]
        attacker_color = attacker.color

        if attacker.name != "pawn":
            victim = self.board[to_pos[0]][to_pos[1]]
            victim.captured()
        else:
            if move_index == 4:
                victim = self.board[from_pos[0]][from_pos[1] - 1]
                victim.captured()
                
                info['is_enpassant'] = True
                info['enpassant_pos'] = [from_pos[0], from_pos[1] - 1]
                info['enpassant_pc'] = victim

                self.board[from_pos[0]][from_pos[1] - 1] = self.create_empty_piece()
                
            if move_index == 5:
                victim = self.board[from_pos[0]][from_pos[1] + 1]
                victim.captured()
        
                info['is_enpassant'] = True
                info['enpassant_pos'] = [from_pos[0], from_pos[1] + 1]
                info['enpassant_pc'] = victim

                self.board[from_pos[0]][from_pos[1] + 1] = self.create_empty_piece()
            else:
                victim = self.board[to_pos[0]][to_pos[1]]
                victim.captured()
            
    def is_move_valid(self, from_pos, to_pos):
        pc = self.board[from_pos[0]][from_pos[1]]
        possible_moves, possible_moves_mask, is_capture = pc.get_possible_moves(self.get_state())
        candidate_move = [to_pos[0] - from_pos[0], to_pos[1] - from_pos[1]]
        for idx in range(len(possible_moves)):
            if possible_moves[idx] == candidate_move and possible_moves_mask[idx]:
                move_info = {
                    'possible_moves': possible_moves,
                    'possible_moves_mask': possible_moves_mask,
                    'is_capture': is_capture,
                    'move_id': idx
                }
                return True, move_info
        return False, None
    
    def handle_move(self, from_pos, to_pos, move_info):
        is_capture = move_info['is_capture']
        move_id = move_info['move_id']

        info = {
            'is_enpassant': False,
            'is_castle': False,
            'is_promotion': False
        }

        if is_capture[move_id]:
            self.handle_capture(from_pos, to_pos, move_id, info)
        
        # Promotion
        if self.board[from_pos[0]][from_pos[1]].name == "pawn" and (to_pos[0] == 0 or to_pos[0] == 7):
            self.board[from_pos[0]][from_pos[1]].promote()
            info['is_promotion'] = True
        
        # Castling
        if (self.board[from_pos[0]][from_pos[1]].name == "king"):
            if self.board[from_pos[0]][from_pos[1]].color == "W":
                switch_idx = 7
            else:
                switch_idx = 0

            if move_id == 8:
                info['is_castle'] = True
                info['init_rook_pos'] = [switch_idx, 7]
                info['final_rook_pos'] = [switch_idx, 5]
                self.board[switch_idx][7].update_pos(switch_idx, 5)
                self.board[switch_idx][7].update_history([switch_idx, 5], self.total_moves + 1)
                self.board[switch_idx][5] = self.board[switch_idx][7]
                self.board[switch_idx][7] = self.create_empty_piece()
            elif move_id == 9:
                info['is_castle'] = True
                info['init_rook_pos'] = [switch_idx, 0]
                info['final_rook_pos'] = [switch_idx, 3]
                self.board[switch_idx][0].update_pos(switch_idx, 3)
                self.board[switch_idx][0].update_history([switch_idx, 3], self.total_moves + 1)
                self.board[switch_idx][3] = self.board[switch_idx][0]
                self.board[switch_idx][0] = self.create_empty_piece()
                
        self.board[from_pos[0]][from_pos[1]].update_pos(to_pos[0], to_pos[1])
        self.board[from_pos[0]][from_pos[1]].update_history(to_pos, self.total_moves + 1)
        
        self.board[to_pos[0]][to_pos[1]] = self.board[from_pos[0]][from_pos[1]]
        self.board[from_pos[0]][from_pos[1]] = self.create_empty_piece()

        self.total_moves += 1

        return info

    def is_checkmate(self):
        if is_check(self.board, "W", self.white_pieces[12].pos):
            white_checkmated = True

            for white_piece in self.white_pieces:
                possible_moves, possible_moves_mask, is_capture = white_piece.get_possible_moves(self.get_state())
                if True in possible_moves_mask:
                    white_checkmated = False
                    break
                    
            if white_checkmated:
                return True, "W"
    
        if is_check(self.board, "B", self.black_pieces[12].pos):
            black_checkmated = True

            for black_piece in self.black_pieces:
                possible_moves, possible_moves_mask, is_capture = black_piece.get_possible_moves(self.get_state())
                if True in possible_moves_mask:
                    black_checkmated = False
                    break
        
            if black_checkmated:
                return True, "B"

        return False, None

    def unmake_move(self, from_pos, to_pos, to_pos_pc, info):
        from_pos_pc = self.board[to_pos[0]][to_pos[1]]

        if info['is_enpassant']:
            enpassant_pc = info['enpassant_pc']
            enpassant_pos = info['enpassant_pos']
            enpassant_pc.revive()
            enpassant_pc.update_pos(enpassant_pos[0], enpassant_pos[1])
            self.board[enpassant_pos[0]][enpassant_pos[1]] = enpassant_pc
        elif info['is_castle']:
            init_rook_pos = info['init_rook_pos']
            final_rook_pos = info['final_rook_pos']
            rook_pc = self.board[final_rook_pos[0]][final_rook_pos[1]]
            rook_pc.update_pos(init_rook_pos[0], init_rook_pos[1])
            if len(rook_pc.history) > 1:
                rook_pc.history.pop()
            self.board[init_rook_pos[0]][init_rook_pos[1]] = rook_pc
            self.board[final_rook_pos[0]][final_rook_pos[1]] = self.create_empty_piece()
        elif info['is_promotion']:
            from_pos_pc.unpromote()
        
        if to_pos_pc.symbol != 'E':
            to_pos_pc.revive()
            to_pos_pc.update_pos(to_pos[0], to_pos[1])
            self.board[to_pos[0]][to_pos[1]] = to_pos_pc
        else:
            self.board[to_pos[0]][to_pos[1]] = self.create_empty_piece()
        
        from_pos_pc.update_pos(from_pos[0], from_pos[1])
        if len(from_pos_pc.history) > 1:
            from_pos_pc.history.pop()
        self.board[from_pos[0]][from_pos[1]] = from_pos_pc

        self.total_moves -= 1
    
    def input_to_move(self, usr_inp):
        from_pos = usr_inp[0]
        to_pos = usr_inp[1]

        from_alp = ord(from_pos[0]) - ord('a')
        from_num = 8 - int(from_pos[1])

        to_alp = ord(to_pos[0]) - ord('a')
        to_num = 8 - int(to_pos[1])

        from_pos = [from_num, from_alp]
        to_pos = [to_num, to_alp]

        return from_pos, to_pos

    def poll_and_make_move(self):
        if self.total_moves % 2 == 0:
            usr_inp = input("White turn to move: ")
        else:
            usr_inp = input("Black turn to move: ")

        usr_inp = [usr_inp[0:2], usr_inp[3:]]
        from_pos, to_pos = self.input_to_move(usr_inp)

        if self.total_moves % 2 == 0:
            if self.board[from_pos[0]][from_pos[1]].color != 'W':
                return False
        else:
            if self.board[from_pos[0]][from_pos[1]].color != 'B':
                return False

        valid_move, move_info = self.is_move_valid(from_pos, to_pos)
        if not valid_move:
            return False

        self.handle_move(from_pos, to_pos, move_info)

        return True
    
    def draw_board(self):
        canvas = [['e' for _ in range(8)] for _ in range(8)]
        for white_piece in self.white_pieces:
            if white_piece.is_alive():
                pos = white_piece.pos
                canvas[pos[0]][pos[1]] = str(white_piece.color) + "_" + white_piece.symbol
        for black_piece in self.black_pieces:
            if black_piece.is_alive():
                pos = black_piece.pos
                canvas[pos[0]][pos[1]] = str(black_piece.color) + "_" + black_piece.symbol
        return canvas
