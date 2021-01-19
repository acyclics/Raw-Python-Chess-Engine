import numpy as np

from engine.alphabeta import AlphaBetaSearch
from engine.opening_book import open_reader


class Engine():

    def __init__(self):
        self.minimax = AlphaBetaSearch(4, 5, 1000)
        self.opening_book = open_reader("./engine/performance.bin")
    
    def get_move(self, game):
        # Use opening book if possible
        use_opening_book = True
        try:
            entry = self.opening_book.choice(game)
        except:
            use_opening_book = False
        
        if use_opening_book:
            entry = entry.move_name
            from_pos = [8 - int(entry[1]), ord(entry[0]) - ord('a')]
            to_pos = [8 - int(entry[3]), ord(entry[2]) - ord('a')]
            return from_pos, to_pos
        
        # Finally, resort to alpha beta search
        move = self.minimax.alpha_beta_search(game)
        pc_idx = move['piece_id']
        possible_move = move['possible_moves'][move['move_id']]
        from_pos = game.black_pieces[pc_idx].pos
        to_pos = [from_pos[0] + possible_move[0], from_pos[1] + possible_move[1]]
        
        return from_pos, to_pos
