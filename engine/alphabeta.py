import numpy as np
from copy import deepcopy

from engine.heuristic import eval_position, piece_value
from engine.transposition import Transposition
from engine.zobrist_hashing import ZobristHashing


class AlphaBetaSearch():

    def __init__(self, max_search_depth, max_quiescence_depth, aspiration_window):
        self.max_search_depth = max_search_depth
        self.quiescence_depth = max_quiescence_depth
        self.aspiration_window = aspiration_window
        self.win_utility = 1000000
        self.color = "B"
        self.zobrist_hashing = ZobristHashing()
        self.transposition = Transposition(100000)
        
        self.cutoffs = 0
        self.quies = 0
        self.trans_hits = 0

        #self.cutoffs_history = []
        #self.quies_history = []
        #self.trans_hits_history = []

    def is_terminal(self, state, alpha, beta):
        depth = state['depth']
        game = state['game']
        is_capture = state['is_capture']

        is_checkmate, color = game.is_checkmate()
    
        if is_checkmate:
            if self.color != color:
                return True, self.win_utility
            else:
                return True, -self.win_utility

        if depth == self.search_depth:
            if is_capture and depth >= 1:
                qstate = {
                    'game': game,
                    'depth': 0
                }
                return True, self.quiescence_search(qstate, alpha, beta)
            else:
                return True, eval_position(game, self.color)

        return False, None

    def alpha_beta_search(self, game):
        alpha = -np.inf
        beta = np.inf

        for depth in range(1, self.max_search_depth + 1):
            self.search_depth = depth

            state = {
                'game': deepcopy(game),
                'depth': 0,
                'is_capture': False
            }

            value, move = self.max_value(state, alpha, beta)

            if value <= alpha or value >= beta:
                value, move = self.max_value(state, -np.inf, np.inf)

            alpha = value - self.aspiration_window
            beta = value + self.aspiration_window

            print("Alpha beta search completed for depth", depth, end=". ")
            print("Number of cutoffs =", self.cutoffs, end=". ")
            print("Number of quiescence expansion =", self.quies, end=". ")
            print("Number of transposition table hits =", self.trans_hits, end=". ")
            print()

            #self.cutoffs_history.append(self.cutoffs)
            #self.quies_history.append(self.quies)
            #self.trans_hits_history.append(self.trans_hits)

            self.cutoffs = 0
            self.quies = 0
            self.trans_hits = 0

        return move

    def get_move_ordering(self, game, color):
        moves = []
        moves_priority = []

        def append_move(move, priority):
            moves.append(move)
            moves_priority.append(priority)

        all_moves = game.generate_all_possible_moves(color)

        # Principal variation (PC move) with depth smaller than the depth the algo is about to go to
        trans_move = self.query_transposition_move(game)
        if trans_move != None:
            append_move(trans_move, 100)
        
        for pc_idx, all_move in enumerate(all_moves):
            possible_moves = all_move['possible_moves']
            possible_moves_mask = all_move['possible_moves_mask']
            is_capture = all_move['is_capture']

            for idx in range(len(possible_moves)):
                if possible_moves_mask[idx]:
                    if color == "B":
                        mypiece = game.black_pieces[pc_idx]
                    else:
                        mypiece = game.white_pieces[pc_idx]
                    
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

                    if is_capture[idx]:
                        capturing_pc = mypiece.name
                        victim_pc = game.board[to_pos[0]][to_pos[1]].name
                        if victim_pc == "empty":
                            victim_pc = "pawn"
                        priority = piece_value(victim_pc) - piece_value(capturing_pc)
                        priority += 100
                    else:
                        priority = 0

                    append_move(move_info, priority)
        
        moves_priority = [[priority, idx] for idx, priority in enumerate(moves_priority)]
        sorted(moves_priority, reverse=True)

        sorted_moves = []
        for moves_p in moves_priority:
            sorted_moves.append(moves[moves_p[1]])
        
        return sorted_moves

    def max_value(self, state, alpha, beta):
        terminal, utility = self.is_terminal(state, alpha, beta)

        game = state['game']
        depth = state['depth']

        if terminal:
            return utility, None
        
        v, best_move = self.query_transposition(game, depth, self.search_depth)
        if v != None:
            return v, best_move
        
        v = -np.inf
        best_move = None

        moves = self.get_move_ordering(game, "B")
        
        for move in moves:
            to_pos_pc = game.board[move['to_pos'][0]][move['to_pos'][1]]
            info = game.handle_move(move['from_pos'], move['to_pos'], move)

            new_state = {
                'game': game,
                'depth': depth + 1,
                'is_capture': move['is_capture'][move['move_id']]
            }

            v2, a2 = self.min_value(new_state, alpha, beta)

            game.unmake_move(move['from_pos'], move['to_pos'], to_pos_pc, info)

            if v2 > v:
                v, best_move = v2, move
                alpha = max(alpha, v)
            
            if v >= beta:
                self.cutoffs += 1
                self.update_transposition(v, best_move, self.search_depth - depth, game)
                return v, best_move

        self.update_transposition(v, best_move, self.search_depth - depth, game)
        return v, best_move
    
    def min_value(self, state, alpha, beta):
        terminal, utility = self.is_terminal(state, alpha, beta)

        game = state['game']
        depth = state['depth']

        if terminal:
            return utility, None
        
        v, best_move = self.query_transposition(game, depth, self.search_depth)
        if v != None:
            return v, best_move
        
        v = np.inf
        best_move = None
        
        moves = self.get_move_ordering(game, "W")
    
        for move in moves:
            to_pos_pc = game.board[move['to_pos'][0]][move['to_pos'][1]]
            info = game.handle_move(move['from_pos'], move['to_pos'], move)

            new_state = {
                'game': game,
                'depth': depth + 1,
                'is_capture': move['is_capture'][move['move_id']]
            }

            v2, a2 = self.max_value(new_state, alpha, beta)

            game.unmake_move(move['from_pos'], move['to_pos'], to_pos_pc, info)

            if v2 < v:
                v, best_move = v2, move
                beta = min(beta, v)
            
            if v <= alpha:
                self.cutoffs += 1
                self.update_transposition(v, best_move, self.search_depth - depth, game)
                return v, best_move
        
        self.update_transposition(v, best_move, self.search_depth - depth, game)
        return v, best_move
    
    def update_transposition(self, value, move, depth, game):
        zobrist_key = self.zobrist_hashing.hash(game)
        self.transposition.add_entry(zobrist_key, depth, value, move)
    
    def query_transposition_move(self, game):
        zobrist_key = self.zobrist_hashing.hash(game)
        entry = self.transposition.lookup(zobrist_key)
        if entry == None or entry['key'] != zobrist_key:
            return None
        else:
            self.trans_hits += 1
            return entry['best_move']
    
    def query_transposition(self, game, depth, search_depth):
        zobrist_key = self.zobrist_hashing.hash(game)
        entry = self.transposition.lookup(zobrist_key)
        if entry != None and entry['key'] == zobrist_key and entry['depth'] >= search_depth - depth:
            v, a = entry['evaluation'], entry['best_move']
            self.trans_hits += 1
            return v, a
        else:
            return None, None
    
    def quiescence_search(self, qstate, alpha, beta):
        game = qstate['game']
        depth = qstate['depth']
        self.quies += 1

        if game.total_moves % 2 == 0:
            color = "W"
        else:
            color = "B"

        is_checkmate, check_color = game.is_checkmate()
        if is_checkmate:
            if self.color != color:
                return self.win_utility
            else:
                return -self.win_utility

        v, best_move = self.query_transposition(game, depth, self.quiescence_depth)
        if v != None:
            return v, best_move

        stand_pat = eval_position(game, self.color)

        if color == "B":
            if stand_pat >= beta:
                return beta
            if stand_pat > alpha:
                alpha = stand_pat
        else:
            if stand_pat <= alpha:
                return alpha
            if stand_pat < beta:
                beta = stand_pat

        if depth >= self.quiescence_depth:
            return stand_pat
        
        for move in self.get_move_ordering(game, color):
            if move['is_capture'][move['move_id']]:
                to_pos_pc = game.board[move['to_pos'][0]][move['to_pos'][1]]

                info = game.handle_move(move['from_pos'], move['to_pos'], move)
                
                qstate = {
                    'game': game,
                    'depth': depth + 1
                }

                score = self.quiescence_search(qstate, alpha, beta)

                game.unmake_move(move['from_pos'], move['to_pos'], to_pos_pc, info)

                if color == "B":
                    if score >= beta:
                        return beta
                    if score > alpha:
                        alpha = score
                else:
                    if score <= alpha:
                        return alpha
                    if score < beta:
                        beta = score
        
        if color == "B":
            return alpha
        else:
            return beta
