from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
from enum import Enum


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


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
    player: int  # 1 or 2
    type: PieceType
    
class Position(BaseModel):
    row: int
    col: int

class Move(BaseModel):
    from_pos: Position
    to_pos: Position
    player: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class Player(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    player_number: int  # 1 or 2

class GameState(BaseModel):
    board: List[List[Optional[Piece]]] = Field(default_factory=lambda: [[None for _ in range(5)] for _ in range(5)])
    current_player: int = 1
    moves: List[Move] = []
    winner: Optional[int] = None

class Game(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    room_code: str
    players: List[Player] = []
    game_state: GameState = Field(default_factory=GameState)
    status: GameStatus = GameStatus.WAITING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Request/Response Models
class CreateGameRequest(BaseModel):
    player_name: str

class JoinGameRequest(BaseModel):
    room_code: str
    player_name: str

class MakeMoveRequest(BaseModel):
    game_id: str
    player_id: str
    from_row: int
    from_col: int
    to_row: int
    to_col: int

class GameResponse(BaseModel):
    game: Game
    your_player_number: Optional[int] = None

# Legacy Models (keeping for compatibility)
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

# Game Logic Functions
def initialize_board() -> List[List[Optional[Piece]]]:
    """Initialize the King's Valley board with starting positions"""
    board = [[None for _ in range(5)] for _ in range(5)]
    
    # Player 2 (top row)
    for i in range(5):
        piece_type = PieceType.KING if i == 2 else PieceType.PAWN
        board[0][i] = Piece(player=2, type=piece_type)
    
    # Player 1 (bottom row)
    for i in range(5):
        piece_type = PieceType.KING if i == 2 else PieceType.PAWN
        board[4][i] = Piece(player=1, type=piece_type)
    
    return board

def is_valid_move(board: List[List[Optional[Piece]]], from_pos: Position, to_pos: Position, player: int) -> bool:
    """Validate if a move is legal according to King's Valley rules"""
    # Check bounds
    if not (0 <= from_pos.row < 5 and 0 <= from_pos.col < 5):
        return False
    if not (0 <= to_pos.row < 5 and 0 <= to_pos.col < 5):
        return False
    
    # Check if there's a piece at from_pos
    piece = board[from_pos.row][from_pos.col]
    if not piece or piece.player != player:
        return False
    
    # Check if destination is empty
    if board[to_pos.row][to_pos.col] is not None:
        return False
    
    # Calculate direction
    dr = to_pos.row - from_pos.row
    dc = to_pos.col - from_pos.col
    
    # Must be straight or diagonal
    if dr != 0 and dc != 0 and abs(dr) != abs(dc):
        return False
    
    # Get step direction
    step_r = 0 if dr == 0 else (1 if dr > 0 else -1)
    step_c = 0 if dc == 0 else (1 if dc > 0 else -1)
    
    # Check path until blocked or edge
    r = from_pos.row + step_r
    c = from_pos.col + step_c
    
    while 0 <= r < 5 and 0 <= c < 5 and board[r][c] is None:
        if r == to_pos.row and c == to_pos.col:
            # Valid if this is the last square in the direction
            next_r = r + step_r
            next_c = c + step_c
            if (next_r < 0 or next_r >= 5 or 
                next_c < 0 or next_c >= 5 or 
                board[next_r][next_c] is not None):
                return True
            else:
                return False  # Could have gone further
        r += step_r
        c += step_c
    
    return False

def check_winner(board: List[List[Optional[Piece]]]) -> Optional[int]:
    """Check if there's a winner (king in center)"""
    center_piece = board[2][2]
    if center_piece and center_piece.type == PieceType.KING:
        return center_piece.player
    return None

def generate_room_code() -> str:
    """Generate a 6-character room code"""
    import random
    import string
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# API Endpoints
@api_router.post("/game/create", response_model=GameResponse)
async def create_game(request: CreateGameRequest):
    """Create a new game room"""
    room_code = generate_room_code()
    
    # Ensure room code is unique
    while await db.games.find_one({"room_code": room_code, "status": {"$ne": GameStatus.FINISHED}}):
        room_code = generate_room_code()
    
    player = Player(name=request.player_name, player_number=1)
    game_state = GameState(board=initialize_board())
    
    game = Game(
        room_code=room_code,
        players=[player],
        game_state=game_state,
        status=GameStatus.WAITING
    )
    
    await db.games.insert_one(game.dict())
    return GameResponse(game=game, your_player_number=1)

@api_router.post("/game/join", response_model=GameResponse)
async def join_game(request: JoinGameRequest):
    """Join an existing game room"""
    game_doc = await db.games.find_one({
        "room_code": request.room_code,
        "status": GameStatus.WAITING
    })
    
    if not game_doc:
        raise HTTPException(status_code=404, detail="Game room not found or already started")
    
    game = Game(**game_doc)
    
    if len(game.players) >= 2:
        raise HTTPException(status_code=400, detail="Game room is full")
    
    # Add second player
    player = Player(name=request.player_name, player_number=2)
    game.players.append(player)
    game.status = GameStatus.IN_PROGRESS
    game.updated_at = datetime.utcnow()
    
    await db.games.update_one(
        {"_id": game_doc["_id"]},
        {"$set": game.dict()}
    )
    
    return GameResponse(game=game, your_player_number=2)

@api_router.get("/game/{game_id}", response_model=Game)
async def get_game(game_id: str):
    """Get current game state"""
    game_doc = await db.games.find_one({"id": game_id})
    if not game_doc:
        raise HTTPException(status_code=404, detail="Game not found")
    
    return Game(**game_doc)

@api_router.post("/game/move")
async def make_move(request: MakeMoveRequest):
    """Make a move in the game"""
    game_doc = await db.games.find_one({"id": request.game_id})
    if not game_doc:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game = Game(**game_doc)
    
    if game.status != GameStatus.IN_PROGRESS:
        raise HTTPException(status_code=400, detail="Game is not in progress")
    
    # Find player
    player = next((p for p in game.players if p.id == request.player_id), None)
    if not player:
        raise HTTPException(status_code=403, detail="Player not in this game")
    
    if game.game_state.current_player != player.player_number:
        raise HTTPException(status_code=400, detail="Not your turn")
    
    # Validate move
    from_pos = Position(row=request.from_row, col=request.from_col)
    to_pos = Position(row=request.to_row, col=request.to_col)
    
    if not is_valid_move(game.game_state.board, from_pos, to_pos, player.player_number):
        raise HTTPException(status_code=400, detail="Invalid move")
    
    # Make the move
    piece = game.game_state.board[request.from_row][request.from_col]
    game.game_state.board[request.from_row][request.from_col] = None
    game.game_state.board[request.to_row][request.to_col] = piece
    
    # Record the move
    move = Move(from_pos=from_pos, to_pos=to_pos, player=player.player_number)
    game.game_state.moves.append(move)
    
    # Check for winner
    winner = check_winner(game.game_state.board)
    if winner:
        game.game_state.winner = winner
        game.status = GameStatus.FINISHED
    else:
        # Switch turns
        game.game_state.current_player = 3 - game.game_state.current_player
    
    game.updated_at = datetime.utcnow()
    
    await db.games.update_one(
        {"_id": game_doc["_id"]},
        {"$set": game.dict()}
    )
    
    return {"success": True, "winner": winner}

@api_router.get("/game/room/{room_code}", response_model=Game)
async def get_game_by_room(room_code: str):
    """Get game by room code"""
    game_doc = await db.games.find_one({"room_code": room_code})
    if not game_doc:
        raise HTTPException(status_code=404, detail="Game room not found")
    
    return Game(**game_doc)
@api_router.get("/")
async def root():
    return {"message": "Hello World"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
