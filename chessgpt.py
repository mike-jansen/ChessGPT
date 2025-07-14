from openai import OpenAI
import chess
import base64
import os

client = OpenAI()

# called by the GUI when its black's turn to move
def choose_black_move(fen_str):
    board = chess.Board(fen_str)
    # legal_moves = list(board.legal_moves)
    legal_moves = [board.san(move) for move in list(board.legal_moves)]

    if legal_moves:
        # move = get_random_move(legal_moves)
        move = get_ai_response(fen_str, legal_moves)
        return move
    return None

def get_random_move(legal_moves):
    import random
    move = random.choice(legal_moves)
    # print(move, move.uci(), type(move), type(move.uci()))
    return move.uci()

# encode image into base64 (text)
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def get_ai_response(board, legal_moves):
    base64_image = encode_image('chess_board.png')
    
    response = client.responses.create(
        model="gpt-4.1",
        input=[
            {'role':'system', 'content':f"{system_prompt}"},
            # {'role':'user', 'content':f"{board} ||| {legal_moves}"}
            # {'role':'user', 'content':f"{legal_moves} ||| {image_base64}"}
            {
                "role": "user",
                "content": [
                    # {"type":"input_text", "text":''.join(legal_moves)},
                    {"type":"input_image","image_url": f"data:image/jpeg;base64,{base64_image}"},
                ],
            }
        ],
        temperature=0.5
    )

    move, reason = response.output_text.splitlines()
    move = move.replace('Move:', '').strip()
    reason = reason.replace('Reason:', '').strip()

    print(move, ':', reason)
    return(move)


system_prompt = '''
    You are a chess player that will play chess against the user. You will be playing as black, meaning you will go second. 

    You will get an image of the current board state, and need to determine which moves are legal, and then which are the best.

    When you make a move, first analyze the layout of the board to familiarize yourself with the location of pieces, then choose one of the legal moves. \
    When choosing a legal move, don't randomly pick on of the legal moves. Make sure you are choosing the move that makes the most sense and gives you the biggest advantage. \
    
    When outputting your choice, list the move in Standard Algebraic Notation (SAN), such as e4 or Nf3. You must absolutely guaranteed make sure that the \
    move is in SAN no matter what. Don't add extra characters. You should also provide one short sentence explaining \
    why you chose that move. You must follow this format exactly, do not add anything or say anything else:

    Move: (move in SAN)
    Reason: (explanation of why you chose that move)
'''