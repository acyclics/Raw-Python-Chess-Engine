import numpy as np
import colorama
from colorama import Fore, Back, Style

from chess import Chess


class Board():

    def __init__(self):
        pass

    def new_game(self):
        self.chess = Chess()
    
    def play(self):
        print("Please select gamemode:")
        print("Enter 1 for random play")
        print("Enter 2 for human vs ai")
        print("Enter 3 for manual play")

        gamemode = int(input())
        
        game_has_ended = False

        if gamemode == 1:
            while not game_has_ended:
                self.draw_board()
                game_has_ended = self.chess.random_loop()
        elif gamemode == 2:
            while not game_has_ended:
                self.draw_board()
                game_has_ended = self.chess.game_loop()
        else:
            while not game_has_ended:
                self.draw_board()
                game_has_ended = self.chess.manual_loop()
    
    def draw_board(self):
        for i in range(8):
            print(8 - i, end=" ")
            for j in range(8):
                if self.chess.canvas[i][j] == 'e':
                    if i % 2 == 0 and j % 2 == 0:
                        print(Back.RED + "   ", end="")
                    elif i % 2 != 0 and j % 2 != 0:
                        print(Back.RED + "   ", end="")
                    else:
                        print(Back.GREEN + "   ", end="")
                else:
                    if self.chess.chess_game.board[i][j].color == "W": 
                        if i % 2 == 0 and j % 2 == 0:
                            print(Back.RED + Fore.WHITE + " " + self.chess.canvas[i][j][2] + " ", end="")
                        elif i % 2 != 0 and j % 2 != 0:
                            print(Back.RED + Fore.WHITE + " " + self.chess.canvas[i][j][2] + " ", end="")
                        else:
                            print(Back.GREEN + Fore.WHITE + " " + self.chess.canvas[i][j][2] + " ", end="")
                    else:
                        if i % 2 == 0 and j % 2 == 0:
                            print(Style.DIM + Back.RED + Fore.BLACK + " " + self.chess.canvas[i][j][2] + " ", end="")
                        elif i % 2 != 0 and j % 2 != 0:
                            print(Style.DIM + Back.RED + Fore.BLACK + " " + self.chess.canvas[i][j][2] + " ", end="")
                        else:
                            print(Style.DIM + Back.GREEN + Fore.BLACK + " " + self.chess.canvas[i][j][2] + " ", end="")
            print()
           
        print("  ", end ="")
        for j in range(8):
            print(" " + chr(ord('a')+j) + " ", end="")
        print()
        print()


if __name__ == '__main__':
    colorama.init(autoreset=True)
    board = Board()
    board.new_game()
    board.play()
