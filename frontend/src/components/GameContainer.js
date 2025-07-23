import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import GameLobby from './GameLobby';
import GameBoard from './GameBoard';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const GameContainer = () => {
  const [gameState, setGameState] = useState(null);
  const [playerInfo, setPlayerInfo] = useState(null);
  const [selectedSquare, setSelectedSquare] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [winner, setWinner] = useState(null);

  // Poll for game updates
  const fetchGameState = useCallback(async () => {
    if (!gameState?.id) return;
    
    try {
      const response = await axios.get(`${API}/game/${gameState.id}`);
      const updatedGame = response.data;
      
      setGameState(updatedGame);
      
      // Check for winner
      if (updatedGame.game_state.winner) {
        setWinner(updatedGame.game_state.winner);
      }
    } catch (err) {
      console.error('Error fetching game state:', err);
    }
  }, [gameState?.id]);

  // Poll every 2 seconds when game is active
  useEffect(() => {
    if (gameState && gameState.status !== 'finished') {
      const interval = setInterval(fetchGameState, 2000);
      return () => clearInterval(interval);
    }
  }, [fetchGameState, gameState?.status]);

  const handleCreateGame = async (playerName) => {
    setIsLoading(true);
    setError('');
    
    try {
      const response = await axios.post(`${API}/game/create`, {
        player_name: playerName
      });
      
      const data = response.data;
      setGameState(data.game);
      setPlayerInfo({
        id: data.game.players[0].id,
        name: playerName,
        number: data.your_player_number
      });
    } catch (err) {
      setError('Failed to create game. Please try again.');
      console.error('Create game error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleJoinGame = async (roomCode, playerName) => {
    setIsLoading(true);
    setError('');
    
    try {
      const response = await axios.post(`${API}/game/join`, {
        room_code: roomCode,
        player_name: playerName
      });
      
      const data = response.data;
      setGameState(data.game);
      setPlayerInfo({
        id: data.game.players.find(p => p.player_number === data.your_player_number).id,
        name: playerName,
        number: data.your_player_number
      });
    } catch (err) {
      if (err.response?.status === 404) {
        setError('Game room not found or already started.');
      } else if (err.response?.status === 400) {
        setError('Game room is full.');
      } else {
        setError('Failed to join game. Please try again.');
      }
      console.error('Join game error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSquareClick = async (row, col) => {
    if (!gameState || gameState.status !== 'in_progress') return;
    if (gameState.game_state.current_player !== playerInfo?.number) return;
    
    const piece = gameState.game_state.board[row][col];
    
    if (selectedSquare) {
      // Attempting to make a move
      if (selectedSquare.row === row && selectedSquare.col === col) {
        // Deselect if clicking the same square
        setSelectedSquare(null);
        return;
      }
      
      // Try to move the piece
      try {
        const response = await axios.post(`${API}/game/move`, {
          game_id: gameState.id,
          player_id: playerInfo.id,
          from_row: selectedSquare.row,
          from_col: selectedSquare.col,
          to_row: row,
          to_col: col
        });
        
        if (response.data.success) {
          setSelectedSquare(null);
          if (response.data.winner) {
            setWinner(response.data.winner);
          }
          // Fetch updated game state
          await fetchGameState();
        }
      } catch (err) {
        if (err.response?.status === 400) {
          setError('Invalid move. Please try a different move.');
        } else {
          setError('Failed to make move. Please try again.');
        }
        console.error('Move error:', err);
        setTimeout(() => setError(''), 3000);
      }
    } else {
      // Selecting a piece
      if (piece && piece.player === playerInfo?.number) {
        setSelectedSquare({ row, col });
      }
    }
  };

  const handleNewGame = () => {
    setGameState(null);
    setPlayerInfo(null);
    setSelectedSquare(null);
    setWinner(null);
    setError('');
  };

  if (!gameState) {
    return (
      <div className="min-h-screen bg-gray-100 py-8">
        <GameLobby 
          onCreateGame={handleCreateGame}
          onJoinGame={handleJoinGame}
          isLoading={isLoading}
        />
        {error && (
          <div className="max-w-md mx-auto mt-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
            {error}
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 py-8">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold mb-4">King's Valley</h1>
            <p className="text-gray-600 text-lg">Room Code: <span className="font-mono font-bold text-2xl bg-gray-100 px-3 py-1 rounded">{gameState.room_code}</span></p>
            <div className="flex justify-center space-x-6 mt-4">
              {gameState.players.map((player, index) => (
                <div key={player.id} className="text-base flex items-center space-x-2">
                  <div className={`w-4 h-4 rounded-full ${player.player_number === 1 ? 'bg-blue-500' : 'bg-red-500'}`}></div>
                  <span className={`font-semibold ${player.player_number === 1 ? 'text-blue-600' : 'text-red-600'}`}>
                    {player.name}
                  </span>
                  {player.id === playerInfo?.id && <span className="text-gray-500 text-sm">(You)</span>}
                </div>
              ))}
            </div>
          </div>

          {winner && (
            <div className="mb-6 p-6 bg-green-100 border border-green-400 text-green-700 rounded-lg text-center">
              <h2 className="text-2xl font-bold mb-2">🎉 Game Over! 🎉</h2>
              <p className="text-lg">Player {winner} wins!</p>
              {winner === playerInfo?.number ? (
                <p className="font-semibold text-xl mt-2">🏆 Congratulations! You won! 🏆</p>
              ) : (
                <p className="text-lg mt-2">Better luck next time!</p>
              )}
            </div>
          )}

          <div className="flex justify-center">
            <GameBoard
              board={gameState.game_state.board}
              selectedSquare={selectedSquare}
              onSquareClick={handleSquareClick}
              currentPlayer={gameState.game_state.current_player}
              gameStatus={gameState.status}
            />
          </div>

          {error && (
            <div className="mt-6 p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg text-center">
              {error}
            </div>
          )}

          <div className="mt-8 text-center">
            <button
              onClick={handleNewGame}
              className="bg-gray-500 text-white py-3 px-6 rounded-lg hover:bg-gray-600 text-lg"
            >
              Back to Lobby
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GameContainer;