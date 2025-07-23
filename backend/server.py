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

# Add your routes to the router instead of directly to app
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
