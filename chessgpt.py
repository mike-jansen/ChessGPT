from openai import OpenAI
import chess
import base64
import os
import json

client = OpenAI()

# called by the GUI when its black's turn to move
def choose_black_move(fen):
    # board = chess.Board(fen_str)
    # legal_moves = [board.san(move) for move in list(board.legal_moves)]
    # move = get_random_move(legal_moves)

    # move = get_ai_response(image)
    move = get_ai_response(fen)
    return move

def get_random_move(legal_moves):
    import random
    move = random.choice(legal_moves)
    return move.uci()

# encode image into base64 (text)
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")
    
def get_legal_moves(fen):
    print("Retrieving legal moves for board")
    board = chess.Board(fen)
    return ' '.join([board.san(move) for move in board.legal_moves])

tools = [
    {
        "type": "function",
        "name": "get_legal_moves",
        "description": "Returns all legal moves in SAN format, separated by spaces, for a given FEN board position",
        "parameters": {
            "type": "object",
            "properties": {
                "fen": {
                    "type": "string",
                    "description": "The current board position in Forsyth-Edwards Notation (FEN)"
                }
            },
            "required": ["fen"]
        }
    }
]

def call_function(name, args):
    if name == "get_legal_moves":
        return get_legal_moves(**args)

def get_ai_response(fen):
    input_messages = [
            {"role": "system", "content":f"{system_prompt}"},
            {"role": "user", "content": f"Board layout in FEN: {fen}"}
    ]

    response = client.responses.create(
        model="gpt-4.1",
        tools=tools,
        input=input_messages,
    )

    # check if the response contains a tool call
    for tool_call in response.output:
        if tool_call.type != "function_call":
            continue

        # call function
        name = tool_call.name
        args = json.loads(tool_call.arguments)
        result = call_function(name, args)

        input_messages.append(tool_call)  # append model's function call message
        input_messages.append({  # append message result
            "type": "function_call_output",
            "call_id": tool_call.call_id,
            "output": str(result)
        })

        response = client.responses.create(
            model="gpt-4.1",
            input=input_messages,
            tools=tools,
        )

    move, reason = response.output_text.splitlines()
    move = move.replace('Move:', '').strip()
    reason = reason.replace('Reason:', '').strip()

    print(move, ':', reason)
    return(move)


system_prompt = '''
    You are a chess player that will play chess against the user. You will be playing as black, meaning you will go second. 

    You will get a board layout in Forsyth-Edwards Notation (FEN) format, which represents the current state of the chess board. \
    You must call the function get_legal_moves with the FEN string to retrieve all legal moves in Standard Algebraic Notation (SAN) format. \
    
    When you make a move, first analyze the layout of the board to familiarize yourself with the location of pieces, then choose one of the legal moves. \
    When choosing a legal move, don't randomly pick on of the legal moves. Make sure you are choosing the move that makes the most sense and gives you the biggest advantage. \
    
    When outputting your choice, list the move in Standard Algebraic Notation (SAN), such as e4 or Nf3. You must absolutely guaranteed make sure that the \
    move is in SAN no matter what. Don't add extra characters. You should also provide one short sentence explaining \
    why you chose that move. You must follow this format exactly, do not add anything or say anything else:

    Move: (move in SAN)
    Reason: (explanation of why you chose that move)
'''