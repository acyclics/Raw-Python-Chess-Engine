def generate_translational_indexes(starting_index):
    indexes1 = [i for i in range(starting_index + 1, 8)]
    indexes2 = [i for i in range(starting_index - 1, -1, -1)]
    return indexes1, indexes2


def generate_diagonal_indexes(starting_i, starting_j):
    df = min(7 - starting_i, 7 - starting_j)
    indexes1 = [(starting_i + i, starting_j + i) for i in range(1, df + 1)]

    df = min(starting_i, starting_j)
    indexes2 = [(starting_i - i, starting_j - i) for i in range(1, df + 1)]

    df = min(7 - starting_i, starting_j)
    indexes3 = [(starting_i + i, starting_j - i) for i in range(1, df + 1)]

    df = min(starting_i, 7 - starting_j)
    indexes4 = [(starting_i - i, starting_j + i) for i in range(1, df + 1)]

    return indexes1, indexes2, indexes3, indexes4
