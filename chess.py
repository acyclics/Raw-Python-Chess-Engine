import numpy as np
import time
from copy import deepcopy

from chessgame import ChessGame
from engine.engine import Engine


class Chess():

    def __init__(self):
        self.chess_game = ChessGame()
        self.canvas = self.chess_game.draw_board()
        self.engine = Engine()

    def manual_loop(self):
        """
            returns True if game ended
        """
        is_checkmate, color = self.chess_game.is_checkmate()

        if is_checkmate:
            if color == "W":
                print("Black won!")
            else:
                print("White won!")
            return True

        while not self.chess_game.poll_and_make_move():
            continue

        self.canvas = self.chess_game.draw_board()
        return False

    def game_loop(self):
        is_checkmate, color = self.chess_game.is_checkmate()

        if is_checkmate:
            if color == "W":
                print("Black won!")
            else:
                print("White won!")
            return True

        if self.chess_game.total_moves % 2 == 0:
            while not self.chess_game.poll_and_make_move():
                continue
        else:
            from_pos, to_pos = self.engine.get_move(deepcopy(self.chess_game))

            valid_move, move_info = self.chess_game.is_move_valid(from_pos, to_pos)
            
            if not valid_move:
                print("Engine made an invalid move")
                return True

            self.chess_game.handle_move(from_pos, to_pos, move_info)

        self.canvas = self.chess_game.draw_board()

        return False
    
    def random_loop(self):
        is_checkmate, color = self.chess_game.is_checkmate()

        if is_checkmate:
            if color == "W":
                print("Black won!")
            else:
                print("White won!")
            return True

        if self.chess_game.total_moves % 2 == 0:
            all_moves = self.chess_game.generate_all_possible_moves("W")
            random_moves = []

            for pc_idx, all_move in enumerate(all_moves):
                possible_moves = all_move['possible_moves']
                possible_moves_mask = all_move['possible_moves_mask']
                is_capture = all_move['is_capture']

                for idx in range(len(possible_moves)):
                    if possible_moves_mask[idx]:
                        mypiece = self.chess_game.white_pieces[pc_idx]
                        
                        possible_move = possible_moves[idx]

                        from_pos = mypiece.pos
                        to_pos = [mypiece.pos[0] + possible_move[0], mypiece.pos[1] + possible_move[1]]

                        move_info = {
                            'possible_moves': possible_moves,
                            'possible_moves_mask': possible_moves_mask,
                            'is_capture': is_capture,
                            'move_id': idx,
                            'piece_id': pc_idx,
                            'from_pos': from_pos,
                            'to_pos': to_pos
                        }

                        random_moves.append(move_info)
            
            random_move = np.random.randint(0, len(random_moves))
            random_move = random_moves[random_move]

            self.chess_game.handle_move(random_move['from_pos'], random_move['to_pos'], random_move)
            
        else:
            from_pos, to_pos = self.engine.get_move(deepcopy(self.chess_game))

            valid_move, move_info = self.chess_game.is_move_valid(from_pos, to_pos)
            
            if not valid_move:
                print("Engine made an invalid move")
                return True

            self.chess_game.handle_move(from_pos, to_pos, move_info)

        self.canvas = self.chess_game.draw_board()

        return False
    
    def statistical_analysis(self):
        is_checkmate, color = self.chess_game.is_checkmate()

        statistical_info = {
            'is_engine': False
        }

        if is_checkmate:
            if color == "W":
                print("Black won!")
            else:
                print("White won!")

            statistical_info['engine_info'] = self.engine

            return True, statistical_info

        if self.chess_game.total_moves % 2 == 0:
            all_moves = self.chess_game.generate_all_possible_moves("W")
            random_moves = []

            for pc_idx, all_move in enumerate(all_moves):
                possible_moves = all_move['possible_moves']
                possible_moves_mask = all_move['possible_moves_mask']
                is_capture = all_move['is_capture']

                for idx in range(len(possible_moves)):
                    if possible_moves_mask[idx]:
                        mypiece = self.chess_game.white_pieces[pc_idx]
                        
                        possible_move = possible_moves[idx]

                        from_pos = mypiece.pos
                        to_pos = [mypiece.pos[0] + possible_move[0], mypiece.pos[1] + possible_move[1]]

                        move_info = {
                            'possible_moves': possible_moves,
                            'possible_moves_mask': possible_moves_mask,
                            'is_capture': is_capture,
                            'move_id': idx,
                            'piece_id': pc_idx,
                            'from_pos': from_pos,
                            'to_pos': to_pos
                        }

                        random_moves.append(move_info)
            
            random_move = np.random.randint(0, len(random_moves))
            random_move = random_moves[random_move]

            self.chess_game.handle_move(random_move['from_pos'], random_move['to_pos'], random_move)
            
        else:
            statistical_info['is_engine'] = True
            total_time = time.time()
            from_pos, to_pos = self.engine.get_move(deepcopy(self.chess_game))
            statistical_info['total_time'] = time.time() - total_time

            valid_move, move_info = self.chess_game.is_move_valid(from_pos, to_pos)
            
            if not valid_move:
                print("Engine made an invalid move")
                return True

            self.chess_game.handle_move(from_pos, to_pos, move_info)

        self.canvas = self.chess_game.draw_board()

        return False, statistical_info
