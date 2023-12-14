import chess
import random
import time
import tkinter as tk
from tkinter import messagebox
import os

# Define player_names as global variables
player_names = ["", "Computer"]

def main():
    board = chess.Board()
    move_history = []
    player_names = [input("Enter Player 1's name: "), "Computer"]
    player_ratings = [1500, 1500]  # Initial ratings for each player
    player_times = [600, 600]  # Initial time for each player (in seconds)

    print(f"Welcome to the Text-based Chess Game between {player_names[0]} ({player_ratings[0]} Elo) and {player_names[1]} ({player_ratings[1]} Elo)!")

    move_counter = 0
    skill_level = choose_skill_level()
    game_mode = choose_game_mode()
    board_size = choose_board_size()

    move_history_display = []

    while not board.is_game_over():
        print(f"{player_names[board.turn]} (Turn) - {player_names[0]}'s rating: {player_ratings[0]} Elo, {player_names[1]}'s rating: {player_ratings[1]} Elo")

        if move_history:
            print("Move History:")
            for idx, move in enumerate(move_history_display):
                if idx % 2 == 0:
                    print(f"{idx // 2 + 1}. {move}", end="\t")
                else:
                    print(f"{move}")

            print()  # Add a newline to separate the board and move history

        display_board(board, move_history_display)  # Call display_board only once

        if board.is_check():
            print("CHECK!")

        if board.turn == chess.WHITE:
            user_move = input("Enter your move (e.g., 'e2e4', 'promote' to promote a pawn, 'undo' to undo the last move, 'resign' to resign, 'save' to save the game, 'load' to load a game, 'quit' to quit, 'suggest' to get a move suggestion, 'draw' to offer a draw): ")

            if user_move.lower() == 'save':
                save_game(board, move_history, player_ratings)
                print("Game saved as 'chess_game.pgn'")
            elif user_move.lower() == 'load':
                board, move_history, player_ratings = load_game()
                print("Game loaded.")
            elif user_move.lower() == 'quit':
                print("Game quit.")
                break
            elif user_move.lower() == 'promote':
                promote_pawn(board, move_history)
            elif user_move.lower() == 'resign':
                print(f"{player_names[0]} resigns. {player_names[1]} wins!")
                update_elo_ratings(player_ratings, 0, 1)  # Player 0 (white) resigns, so player 1 (black) wins
                break
            elif user_move.lower() == 'undo':
                if move_history:
                    undo_move(board, move_history, move_history_display, player_times)
                else:
                    print("No move to undo.")
            elif user_move.lower() == 'suggest':
                suggested_move = get_suggested_move(board, skill_level)
                print(f"Computer suggests: {suggested_move.uci()}")
            elif user_move.lower() == 'draw':
                offer_draw = input(f"{player_names[0]} offers a draw. {player_names[1]}, do you accept? (yes/no): ").lower()
                if offer_draw == 'yes':
                    print("The game is a draw.")
                    update_elo_ratings(player_ratings, 0.5, 0.5)  # Both players agree to a draw
                    break
            elif is_valid_move(board, user_move):
                if make_move(board, user_move, move_history, move_history_display, player_times):
                    move_counter += 1
            else:
                print("Invalid move. Try again.")
        else:
            computer_move = get_computer_move(board, skill_level)
            if make_move(board, computer_move.uci(), move_history, move_history_display, player_times):
                move_counter += 1

    print("Game over")
    result = board.result()
    if result == "1-0":
        announce_winner(player_names[0])
        update_elo_ratings(player_ratings, 1, 0)  # Player 0 (white) wins
    elif result == "0-1":
        announce_winner(player_names[1])
        update_elo_ratings(player_ratings, 0, 1)  # Player 1 (black) wins
    else:
        if board.is_checkmate():
            print("Checkmate! It's a draw.")
        elif board.is_stalemate() or board.is_insufficient_material() or board.is_seventyfive_moves() or board.is_fivefold_repetition():
            print("The game is drawn.")
            update_elo_ratings(player_ratings, 0.5, 0.5)  # The game ends in a draw
        elif board.is_check():
            print("Stalemate! It's a draw.")
            update_elo_ratings(player_ratings, 0.5, 0.5)  # The game ends in a draw
        else:
            print("Draw by threefold repetition!")
            update_elo_ratings(player_ratings, 0.5, 0.5)  # The game ends in a draw

    print(f"{player_names[0]}'s new rating: {player_ratings[0]} Elo")
    print(f"{player_names[1]}'s new rating: {player_ratings[1]} Elo")

def choose_skill_level():
    while True:
        try:
            skill_level = int(input("Choose the computer's skill level (1 - 3): "))
            if 1 <= skill_level <= 3:
                return skill_level
            else:
                print("Invalid skill level. Choose a level between 1 and 3.")
        except ValueError:
            print("Invalid input. Please enter a number between 1 and 3.")

def choose_game_mode():
    while True:
        game_mode = input("Choose the game mode (classic/blitz): ").lower()
        if game_mode in ['classic', 'blitz']:
            return game_mode
        else:
            print("Invalid game mode. Choose 'classic' or 'blitz'.")

def choose_board_size():
    while True:
        board_size = input("Choose the board size (standard/custom): ").lower()
        if board_size in ['standard', 'custom']:
            return board_size
        else:
            print("Invalid board size. Choose 'standard' or 'custom'.")

def get_computer_move(board, skill_level):
    if skill_level == 1:
        return random.choice(list(board.legal_moves))
    elif skill_level == 2:
        if random.random() < 0.1:
            return random.choice(list(board.legal_moves))
        else:
            return get_suggested_move(board, skill_level)
    else:
        return get_suggested_move(board, skill_level)

def get_suggested_move(board, skill_level):
    if skill_level == 1:
        return random.choice(list(board.legal_moves))
    elif skill_level == 2:
        return random.choice(list(board.legal_moves))
    else:
        evaluation = {}
        for move in board.legal_moves:
            board.push(move)
            evaluation[move] = evaluate_position(board)
            board.pop()
        best_move = max(evaluation, key=evaluation.get)
        return best_move

def evaluate_position(board):
    return sum(piece_value(piece) for piece in board.piece_map().values())

def piece_value(piece):
    if piece.color == chess.WHITE:
        return {
            chess.PAWN: 1,
            chess.KNIGHT: 3,
            chess.BISHOP: 3,
            chess.ROOK: 5,
            chess.QUEEN: 9,
            chess.KING: 0
        }[piece.piece_type]
    else:
        return {
            chess.PAWN: -1,
            chess.KNIGHT: -3,
            chess.BISHOP: -3,
            chess.ROOK: -5,
            chess.QUEEN: -9,
            chess.KING: 0
        }[piece.piece_type]

def display_board(board, move_history_display):
    os.system('cls' if os.name == 'nt' else 'clear')  # Clear the console screen
    print(board)

    print("Move History:")
    for idx, move in enumerate(move_history_display):
        if idx % 2 == 0:
            print(f"{idx // 2 + 1}. {move}", end="\t")
        else:
            print(f"{move}")

    print()  # Add a newline to separate the board and move history

    input("Press Enter to continue...")

def save_game(board, move_history, player_ratings):
    pgn = chess.pgn.Game()
    pgn.setup(board)
    pgn.headers["White"] = f"{player_names[0]} ({player_ratings[0]} Elo)"
    pgn.headers["Black"] = f"{player_names[1]} ({player_ratings[1]} Elo)"
    for move in move_history:
        try:
            pgn.add_variation(chess.Move.from_uci(move))
        except ValueError:
            pass
    with open('chess_game.pgn', 'w') as f:
        f.write(str(pgn))

def load_game():
    board = chess.Board()
    move_history = []
    player_ratings = [1500, 1500]  # Reset player ratings when loading a game
    try:
        pgn = chess.pgn.read_game(open('chess_game.pgn'))
        board.setup(pgn.board())
        for move in pgn.mainline_moves():
            move_history.append(move.uci())
            board.push(move)
    except FileNotFoundError:
        print("No saved game found.")
    return board, move_history, player_ratings

def promote_pawn(board, move_history):
    print("Promote your pawn:")
    print("Q - Queen")
    print("R - Rook")
    print("N - Knight")
    print("B - Bishop")

    promotion_choice = input("Choose promotion piece (Q/R/N/B): ")

    if promotion_choice in ['Q', 'R', 'N', 'B']:
        board.pop()
        promotion_move = chess.Move.from_uci(f"{move_history[-1][:2]}{move_history[-1][3:5]}{promotion_choice}")
        board.push(promotion_move)

def announce_winner(winner):
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo("Game Over", f"{winner} wins!")
    root.destroy()

def is_valid_move(board, move):
    try:
        chess.Move.from_uci(move)
        return chess.Move.from_uci(move) in board.legal_moves
    except ValueError:
        return False

def make_move(board, move, move_history, move_history_display, player_times):
    try:
        move = chess.Move.from_uci(move)
        board.push(move)
        move_history.append(move.uci())
        move_history_display.append(move.uci())
        if len(move_history_display) % 2 == 0:
            move_history_display.append('')  # Add an empty space to align moves
        return True
    except ValueError:
        print("Invalid move. Try again.")
        return False

def undo_move(board, move_history, move_history_display, player_times):
    if len(move_history) >= 2:
        board.pop()
        move_history.pop()
        move_history_display.pop()
        move_history_display.pop()  # Remove the empty space if necessary
        player_times[board.turn] += 10  # Add back 10 seconds to the player's time
        print("Undo successful.")
    else:
        print("No move to undo.")

def update_elo_ratings(player_ratings, player0_score, player1_score, k=32):
    expected_score_player0 = 1 / (1 + 10 ** ((player_ratings[1] - player_ratings[0]) / 400))
    expected_score_player1 = 1 / (1 + 10 ** ((player_ratings[0] - player_ratings[1]) / 400))

    new_rating_player0 = player_ratings[0] + k * (player0_score - expected_score_player0)
    new_rating_player1 = player_ratings[1] + k * (player1_score - expected_score_player1)

    player_ratings[0] = int(new_rating_player0)
    player_ratings[1] = int(new_rating_player1)

if __name__ == "__main__":
    main()
