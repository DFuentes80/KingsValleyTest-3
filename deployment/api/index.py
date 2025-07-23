from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
from enum import Enum

# Environment variables
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
db_name = os.environ.get('DB_NAME', 'kings_valley')

# MongoDB connection
client = AsyncIOMotorClient(mongo_url)
db = client[db_name]

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Game Enums
class PieceType(str, Enum):
    KING = "K"
    PAWN = "P"

class GameStatus(str, Enum):
    WAITING = "waiting"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"

# Game Models
class Piece(BaseModel):
    player: int
    type: PieceType
    
class Position(BaseModel):
    row: int
    col: int

class Move(BaseModel):
    from_pos: Position
    to_pos: Position

class Player(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    number: int

class GameState(BaseModel):
    board: List[List[Optional[Piece]]]
    current_player: int
    winner: Optional[int] = None

class Game(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    room_code: str = Field(default_factory=lambda: str(uuid.uuid4())[:6].upper())
    players: List[Player] = []
    state: GameState
    status: GameStatus = GameStatus.WAITING
    moves: List[Move] = []
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

# Game Logic Functions
def create_initial_board():
    board = [[None for _ in range(5)] for _ in range(5)]
    
    # Player 1 pieces (bottom)
    board[4][0] = Piece(player=1, type=PieceType.PAWN)
    board[4][1] = Piece(player=1, type=PieceType.PAWN) 
    board[4][2] = Piece(player=1, type=PieceType.KING)
    board[4][3] = Piece(player=1, type=PieceType.PAWN)
    board[4][4] = Piece(player=1, type=PieceType.PAWN)
    
    # Player 2 pieces (top)
    board[0][0] = Piece(player=2, type=PieceType.PAWN)
    board[0][1] = Piece(player=2, type=PieceType.PAWN)
    board[0][2] = Piece(player=2, type=PieceType.KING)
    board[0][3] = Piece(player=2, type=PieceType.PAWN)
    board[0][4] = Piece(player=2, type=PieceType.PAWN)
    
    return board

def is_valid_move(board: List[List[Optional[Piece]]], move: Move, current_player: int) -> bool:
    from_row, from_col = move.from_pos.row, move.from_pos.col
    to_row, to_col = move.to_pos.row, move.to_pos.col
    
    # Check bounds
    if not (0 <= from_row < 5 and 0 <= from_col < 5 and 0 <= to_row < 5 and 0 <= to_col < 5):
        return False
    
    # Check if there's a piece at the source
    piece = board[from_row][from_col]
    if not piece or piece.player != current_player:
        return False
    
    # Check if destination is empty
    if board[to_row][to_col] is not None:
        return False
    
    # Check if it's a valid sliding move
    row_diff = to_row - from_row
    col_diff = to_col - from_col
    
    # Must move in straight line (horizontal, vertical, or diagonal)
    if row_diff != 0 and col_diff != 0 and abs(row_diff) != abs(col_diff):
        return False
    
    # Calculate direction
    row_dir = 0 if row_diff == 0 else (1 if row_diff > 0 else -1)
    col_dir = 0 if col_diff == 0 else (1 if col_diff > 0 else -1)
    
    # Check path is clear and piece slides until blocked
    current_row, current_col = from_row + row_dir, from_col + col_dir
    last_valid_row, last_valid_col = from_row, from_col
    
    while 0 <= current_row < 5 and 0 <= current_col < 5:
        if board[current_row][current_col] is not None:
            break
        last_valid_row, last_valid_col = current_row, current_col
        current_row += row_dir
        current_col += col_dir
    
    return to_row == last_valid_row and to_col == last_valid_col

def check_win_condition(board: List[List[Optional[Piece]]]) -> Optional[int]:
    center_piece = board[2][2]
    if center_piece and center_piece.type == PieceType.KING:
        return center_piece.player
    return None

# API Endpoints
@app.get("/")
async def root():
    return {"message": "King's Valley Game API"}

@app.post("/game/create")
async def create_game(player_name: str):
    player = Player(name=player_name, number=1)
    initial_state = GameState(
        board=create_initial_board(),
        current_player=1
    )
    
    game = Game(
        players=[player],
        state=initial_state,
        status=GameStatus.WAITING
    )
    
    await db.games.insert_one(game.model_dump())
    return game

@app.post("/game/join")
async def join_game(room_code: str, player_name: str):
    game_doc = await db.games.find_one({"room_code": room_code})
    if not game_doc:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game = Game(**game_doc)
    
    if len(game.players) >= 2:
        raise HTTPException(status_code=400, detail="Game is full")
    
    player = Player(name=player_name, number=2)
    game.players.append(player)
    game.status = GameStatus.IN_PROGRESS
    game.updated_at = datetime.now()
    
    await db.games.update_one(
        {"room_code": room_code},
        {"$set": game.model_dump()}
    )
    
    return game

@app.get("/game/{game_id}")
async def get_game(game_id: str):
    game_doc = await db.games.find_one({"id": game_id})
    if not game_doc:
        raise HTTPException(status_code=404, detail="Game not found")
    return Game(**game_doc)

@app.get("/game/room/{room_code}")
async def get_game_by_room_code(room_code: str):
    game_doc = await db.games.find_one({"room_code": room_code})
    if not game_doc:
        raise HTTPException(status_code=404, detail="Game not found")
    return Game(**game_doc)

@app.post("/game/move")
async def make_move(game_id: str, move: Move):
    game_doc = await db.games.find_one({"id": game_id})
    if not game_doc:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game = Game(**game_doc)
    
    if game.status != GameStatus.IN_PROGRESS:
        raise HTTPException(status_code=400, detail="Game is not in progress")
    
    if not is_valid_move(game.state.board, move, game.state.current_player):
        raise HTTPException(status_code=400, detail="Invalid move")
    
    # Make the move
    piece = game.state.board[move.from_pos.row][move.from_pos.col]
    game.state.board[move.from_pos.row][move.from_pos.col] = None
    game.state.board[move.to_pos.row][move.to_pos.col] = piece
    
    # Check for win condition
    winner = check_win_condition(game.state.board)
    if winner:
        game.state.winner = winner
        game.status = GameStatus.FINISHED
    else:
        # Switch turns
        game.state.current_player = 2 if game.state.current_player == 1 else 1
    
    # Record the move
    game.moves.append(move)
    game.updated_at = datetime.now()
    
    await db.games.update_one(
        {"id": game_id},
        {"$set": game.model_dump()}
    )
    
    return game

# Handler for Vercel
handler = app