import numpy as np


def has_bishop_pair(game, color):
    if color == "W":
        pieces = game.white_pieces
    else:
        pieces = game.black_pieces

    b1 = pieces[10]
    b2 = pieces[13]

    if b1.is_alive() and b2.is_alive():
        return True
    else:
        return False


def has_rook_pair(game, color):
    if color == "W":
        pieces = game.white_pieces
    else:
        pieces = game.black_pieces

    r1 = pieces[8]
    r2 = pieces[15]

    if r1.is_alive() and r2.is_alive():
        return True
    else:
        return False


def has_knight_pair(game, color):
    if color == "W":
        pieces = game.white_pieces
    else:
        pieces = game.black_pieces

    k1 = pieces[9]
    k2 = pieces[14]

    if k1.is_alive() and k2.is_alive():
        return True
    else:
        return False


def has_pawns(game, color):
    if color == "W":
        pieces = game.white_pieces
    else:
        pieces = game.black_pieces

    for idx in range(0, 8):
        if pieces[idx].is_alive():
            return True
    
    return False


def compute_material_score(game, color):
    if color == "W":
        pieces = game.white_pieces
    else:
        pieces = game.black_pieces

    material_score = 0

    for piece in pieces:
        if piece.is_alive():
            if piece.name == "pawn":
                material_score += 100
            elif piece.name == "knight":
                material_score += 350
            elif piece.name == "bishop":
                material_score += 350
            elif piece.name == "rook":
                material_score += 525
            elif piece.name == "queen":
                material_score += 1000
            else:
                material_score += 10000
    
    return material_score


def pawn_structure(game, color):
    board = game.board
    pawn_score = 0

    if color == "W":
        pawns = game.white_pieces[0:8]
        # Past pawn
        for pawn in pawns:
            if pawn.pos[0] <= 3:
                pawn_score += 10
        # Isolated pawn and doubled pawn check
        surrounds = [[-1, -1], [-1, 0], [0, -1], [1, 1], [1, 0], [0, 1], [-1, 1], [1, -1]]
        for pawn in pawns:
            is_isolated = True
            is_doubled = False
            for surround in surrounds:
                i = pawn.pos[0] + surround[0]
                j = pawn.pos[1] + surround[1]
                if i < 0 or i > 7 or j < 0 or j > 7:
                    continue
                if board[i][j].name == "pawn" and board[i][j].color == color:
                    is_isolated = False
                if i == 0 and board[i][j].name == "pawn" and board[i][j].color == color:
                    is_doubled = True

            if is_isolated:
                pawn_score -= 10
            
            if is_doubled:
                pawn_score -= 10
    
    if color == "B":
        pawns = game.black_pieces[0:8]
        # Past pawn
        for pawn in pawns:
            if pawn.pos[0] >= 4:
                pawn_score += 10
        # Isolated pawn and doubled pawn check
        surrounds = [[-1, -1], [-1, 0], [0, -1], [1, 1], [1, 0], [0, 1], [-1, 1], [1, -1]]
        for pawn in pawns:
            is_isolated = True
            is_doubled = False
            for surround in surrounds:
                i = pawn.pos[0] + surround[0]
                j = pawn.pos[1] + surround[1]
                if i < 0 or i > 7 or j < 0 or j > 7:
                    continue
                if board[i][j].name == "pawn" and board[i][j].color == color:
                    is_isolated = False
                if i == 0 and board[i][j].name == "pawn" and board[i][j].color == color:
                    is_doubled = True

            if is_isolated:
                pawn_score -= 10
            
            if is_doubled:
                pawn_score -= 10

    return pawn_score


def queen_nonlinearity(game, color):
    if color == "W":
        queen = game.white_pieces[11]
    else:
        queen = game.black_pieces[11]
    if queen.is_alive():
        return 1000
    else:
        return 0


def eval_color_position(game, color):
    material_score = compute_material_score(game, color)

    if has_bishop_pair(game, color):
        bishop_pair = 20
    else:
        bishop_pair = 0
    
    if has_rook_pair(game, color):
        rook_pair = -20
    else:
        rook_pair = 0
    
    if has_knight_pair(game, color):
        knight_pair = -20
    else:
        knight_pair = 0
    
    if has_pawns(game, color):
        pawns_alive = 0
    else:
        pawns_alive = -50
    
    pawn_structure_score = pawn_structure(game, color)

    queen_score = queen_nonlinearity(game, color)

    eval_score = material_score + 0.7 * (bishop_pair + rook_pair + knight_pair) + 0.1 * (pawns_alive + pawn_structure_score) + 1.0 * queen_score

    return eval_score


def eval_position(game, color):
    """
        Engine is always black
    """
    evaluation = eval_color_position(game, "B") - eval_color_position(game, "W")
    return evaluation


def piece_value(piece_name):
    if piece_name == "pawn":
        return 1
    if piece_name == "knight":
        return 3.5
    if piece_name == "bishop":
        return 3.5
    if piece_name == "rook":
        return 5.25
    if piece_name == "queen":
        return 10
    return 100
