import pygame
import chess
import os
import random

# Constants
WIDTH, HEIGHT = 480, 480
SQ_SIZE = WIDTH // 8
WHITE = (240, 217, 181)
BROWN = (181, 136, 99)
RED = (255, 80, 80)

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess with Images")

# Load board
board = chess.Board()

# Load images
piece_images = {}

def load_images():
    pieces = ['p', 'n', 'b', 'r', 'q', 'k']
    for color in ['w', 'b']:
        for piece in pieces:
            filename = f"{color}{piece}.png"
            path = os.path.join("images", filename)
            image = pygame.image.load(path)
            image = pygame.transform.scale(image, (SQ_SIZE, SQ_SIZE))
            piece_images[color + piece] = image

# Convert square index to pixel coords
def square_to_coords(square):
    file = chess.square_file(square)
    rank = 7 - chess.square_rank(square)
    return file * SQ_SIZE, rank * SQ_SIZE

# Convert pixel to square index
def coords_to_square(x, y):
    file = x // SQ_SIZE
    rank = 7 - (y // SQ_SIZE)
    return chess.square(file, rank)

# Draw board and selected square
def draw_board(selected_square=None):
    for rank in range(8):
        for file in range(8):
            square = chess.square(file, 7 - rank)
            if selected_square == square:
                color = RED  # Highlight selected square
            else:
                color = WHITE if (rank + file) % 2 == 0 else BROWN
            pygame.draw.rect(screen, color, (file * SQ_SIZE, rank * SQ_SIZE, SQ_SIZE, SQ_SIZE))

# Draw chess pieces
def draw_pieces():
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            color = 'w' if piece.color == chess.WHITE else 'b'
            name = piece.symbol().lower()
            image = piece_images.get(color + name)
            if image:
                x, y = square_to_coords(square)
                screen.blit(image, (x, y))

# New function to update display
def update_display(selected_square=None):
    draw_board(selected_square)
    draw_pieces()
    pygame.display.flip()

import chessgpt  # import your AI module
def make_black_move():
    if board.turn == chess.BLACK:
        # passing the board layout as FEN makes parsing easier, question is just if GPT understands FEN or if you need to use ASCII
        # san_move = chessgpt.choose_black_move(board.fen())  # FEN Representation
        # uci_move = chessgpt.choose_black_move(str(board))  # ASCII Representation
        san_move = chessgpt.choose_black_move(board.fen())

        if san_move:
            move = board.parse_san(san_move)
            if move in board.legal_moves:
                board.push(move)                


# Main loop
def main():
    load_images()
    running = True
    selected_square = None

    while running:
        update_display(selected_square)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and board.turn == chess.WHITE:
                x, y = pygame.mouse.get_pos()
                clicked_square = coords_to_square(x, y)
                piece = board.piece_at(clicked_square)

                if selected_square is None:
                    if piece and piece.color == chess.WHITE:
                        selected_square = clicked_square
                else:
                    if piece and piece.color == chess.WHITE:
                        # Switch to new selection
                        selected_square = clicked_square
                    else:
                        move = chess.Move(selected_square, clicked_square)
                        if move in board.legal_moves:
                            board.push(move)
                            selected_square = None
                            update_display()  # Call before wait to show updated board with move
                            pygame.image.save(screen, "chess_board.png")  # Save the current board state as an image
                            pygame.time.wait(300)
                            make_black_move()
                            update_display()
                            pygame.image.save(screen, "chess_board.png")  # Save the current board state as an image


                            # pygame.image.save(screen, "chess_board.png")  # Save the current board state as an image

                        else:
                            selected_square = None

    pygame.quit()

if __name__ == "__main__":
    main()
