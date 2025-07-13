from openai import OpenAI
import chess

client = OpenAI()

# called by the GUI when its black's turn to move
def choose_black_move(fen_str):
    board = chess.Board(fen_str)
    legal_moves = list(board.legal_moves)
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

def get_ai_response(board, legal_moves):
    response = client.responses.create(
        model="gpt-4.1",
        input=[
            {'role':'system', 'content':f"{system_prompt}"},
            {'role':'user', 'content':f"{board} ||| {legal_moves}"}
        ],
        temperature=0.5
        # input="Write a one-paragraph bedtime story about a unicorn."
    )

    move, reason = response.output_text.splitlines()
    move = move.replace('Move:', '').strip()
    reason = reason.replace('Reason:', '').strip()

    print(reason)
    return(move)


system_prompt = '''
    You are a chess player that will play chess against the user. You will be playing as black, meaning you will go second. 

    You will receive a prompt of the current board state, as well as legal moves you can make. You will first get the current board layout, represented in FEN, \
    followed by "|||" as the separator, and then a list of legal moves you can make. \
   
    When you make a move, first analyze the layout of the board to familiarize yourself with the location of pieces, then choose one of the legal moves. \
    When choosing a legal move, don't randomly pick on of the legal moves. Make sure you are choosing the move that makes the most sense and gives you the biggest advantage. \
    
    When outputting your choice, list the move in Universal Chess Interface (UCI), such as e2e4 or g1f3. You should also provide one short sentence explaining \
    why you chose that move. You must follow this format exactly, do not add anything or say anything else:

    Move: (move in UCI)
    Reason: (explanation of why you chose that move)
'''

