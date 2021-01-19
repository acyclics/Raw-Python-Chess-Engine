import numpy as np

from utils import generate_diagonal_indexes, generate_translational_indexes


def is_attack_translational(pc_class):
    if pc_class == 'Q':
        return True
    elif pc_class == 'R':
        return True
    else:
        return False


def check_horizontal(board, color, king_pos, indexes):
    for i in indexes:
        pc = board[i][king_pos[1]]
        sym = pc.symbol
        pc_color = pc.color
        if sym == 'E':
            continue
        if pc_color == color:
            return False
        if is_attack_translational(sym):
            return True
        else:
            return False
    return False


def check_vertical(board, color, king_pos, indexes):
    for i in indexes:
        pc = board[king_pos[0]][i]
        sym = pc.symbol
        pc_color = pc.color
        if sym == 'E':
            continue
        if pc_color == color:
            return False
        if is_attack_translational(sym):
            return True
        else:
            return False
    return False
    

def is_attack_diagonal(pc_class):
    if pc_class == 'Q':
        return True
    elif pc_class == 'B':
        return True
    else:
        return False


def check_diagonal(board, color, king_pos, indexes):
    for (i, j) in indexes:
        pc = board[i][j]
        sym = pc.symbol
        pc_color = pc.color
        if sym == 'E':
            continue
        if pc_color == color:
            return False
        if is_attack_diagonal(sym):
            return True
        else:
            return False
    return False


def is_eight_way_check(board, color, king_pos):
   # First check all translational
    indexes1, indexes2 = generate_translational_indexes(king_pos[0])
    hori1 = check_horizontal(board, color, king_pos, indexes1)
    hori2 = check_horizontal(board, color, king_pos, indexes2)
    if hori1 | hori2:
        return True
    
    indexes1, indexes2 = generate_translational_indexes(king_pos[1])        
    verti1 = check_vertical(board, color, king_pos, indexes1)
    verti2 = check_vertical(board, color, king_pos, indexes2)
    if verti1 | verti2:
        return True
    
    # Then check all diagonals
    indexes1, indexes2, indexes3, indexes4 = generate_diagonal_indexes(king_pos[0], king_pos[1])
    diag1 = check_diagonal(board, color, king_pos, indexes1)
    diag2 = check_diagonal(board, color, king_pos, indexes2)
    diag3 = check_diagonal(board, color, king_pos, indexes3)
    diag4 = check_diagonal(board, color, king_pos, indexes4)
    if diag1 | diag2 | diag3 | diag4:
        return True

    return False


def is_knight_check(board, color, king_pos):
    i = king_pos[0]
    j = king_pos[1]

    def is_N_check(b,d):
        if b < 0 or b >= 8 or d < 0 or d >= 8:
            return False
        pc = board[b][d]
        sym = pc.symbol
        pc_color = pc.color
        if sym == 'E':
            return False
        if sym == 'N' and pc_color != color:
            return True
        else:
            return False
    
    if is_N_check(i - 2, j + 1):
        return True
    
    if is_N_check(i - 2, j - 1):
        return True
    
    if is_N_check(i - 1, j - 2):
        return True
    
    if is_N_check(i - 1, j + 2):
        return True
    
    if is_N_check(i + 1, j - 2):
        return True
    
    if is_N_check(i + 1, j + 2):
        return True
    
    if is_N_check(i + 2, j - 1):
        return True
    
    if is_N_check(i + 2, j + 1):
        return True
    
    return False


def is_pawn_check(board, color, king_pos):
    for i in [-1, 1]:
        for j in [-1, 1]:
            if king_pos[0] + i < 0 or king_pos[0] + i >= 8 or king_pos[1] + j < 0 or king_pos[1] + j >= 8:
                continue
            pc = board[king_pos[0] + i][king_pos[1] + j]
            sym = pc.symbol
            pc_color = pc.color
            if sym == 'E':
                continue
            if pc_color == color:
                continue
            if sym == 'P':
                if color == 'W':
                    if king_pos[0] < king_pos[0] + i:
                        continue
                    else:
                        return True
                else:
                    if king_pos[0] > king_pos[0] + i:
                        continue
                    else:
                        return True
    return False


def is_king_check(board, color, king_pos):
    mvs = [[-1, -1], [-1, 0], [0, -1], [1, 1], [1, 0], [0, 1], [-1, 1], [1, -1]]
    for mv in mvs:
        if king_pos[0] + mv[0] < 0 or king_pos[0] + mv[0] > 7 or king_pos[1] + mv[1] < 0  or  king_pos[1] + mv[1] > 7:
            continue
        pc = board[king_pos[0] + mv[0]][king_pos[1] + mv[1]]
        sym = pc.symbol
        pc_color = pc.color
        if pc_color != color and sym ==  'K':
            return True
    return False


def is_check(board, color, king_pos):
    if is_eight_way_check(board, color, king_pos):
        return True
    
    if is_knight_check(board, color, king_pos):
        return True
    
    if is_pawn_check(board, color, king_pos):
        return True
    
    if is_king_check(board, color, king_pos):
        return True
    
    return False
