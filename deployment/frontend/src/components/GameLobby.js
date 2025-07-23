import React, { useState } from 'react';

const GameLobby = ({ onCreateGame, onJoinGame, isLoading }) => {
  const [playerName, setPlayerName] = useState('');
  const [roomCode, setRoomCode] = useState('');
  const [activeTab, setActiveTab] = useState('create');
  const [language, setLanguage] = useState('en');

  const handleCreateGame = (e) => {
    e.preventDefault();
    if (playerName.trim()) {
      onCreateGame(playerName.trim());
    }
  };

  const handleJoinGame = (e) => {
    e.preventDefault();
    if (playerName.trim() && roomCode.trim()) {
      onJoinGame(roomCode.trim().toUpperCase(), playerName.trim());
    }
  };

  const rules = {
    en: {
      title: "How to Play:",
      rules: [
        "Get your King (♔) to the center square to win",
        "Pieces slide until blocked by another piece or board edge",
        "You must move to the last available square in your direction",
        "Players alternate turns",
        "Blue pieces are Player 1, Red pieces are Player 2"
      ]
    },
    es: {
      title: "Cómo Jugar:",
      rules: [
        "Lleva tu Rey (♔) al cuadro central para ganar",
        "Las piezas se deslizan hasta ser bloqueadas por otra pieza o el borde",
        "Debes mover al último cuadro disponible en tu dirección",
        "Los jugadores alternan turnos",
        "Las piezas azules son el Jugador 1, las rojas son el Jugador 2"
      ]
    }
  };

  return (
    <div className="max-w-md mx-auto mt-8 p-6 bg-white rounded-lg shadow-lg">
      <h1 className="text-3xl font-bold text-center mb-6">King's Valley</h1>
      
      <div className="flex mb-4">
        <button
          className={`flex-1 py-2 px-4 rounded-l-lg ${
            activeTab === 'create' 
              ? 'bg-blue-500 text-white' 
              : 'bg-gray-200 text-gray-700'
          }`}
          onClick={() => setActiveTab('create')}
        >
          Create Game
        </button>
        <button
          className={`flex-1 py-2 px-4 rounded-r-lg ${
            activeTab === 'join' 
              ? 'bg-blue-500 text-white' 
              : 'bg-gray-200 text-gray-700'
          }`}
          onClick={() => setActiveTab('join')}
        >
          Join Game
        </button>
      </div>

      {activeTab === 'create' ? (
        <form onSubmit={handleCreateGame} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Your Name
            </label>
            <input
              type="text"
              value={playerName}
              onChange={(e) => setPlayerName(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter your name"
              maxLength={20}
              required
            />
          </div>
          <button
            type="submit"
            disabled={isLoading || !playerName.trim()}
            className="w-full bg-blue-500 text-white py-2 px-4 rounded-md hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? 'Creating...' : 'Create Game Room'}
          </button>
        </form>
      ) : (
        <form onSubmit={handleJoinGame} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Room Code
            </label>
            <input
              type="text"
              value={roomCode}
              onChange={(e) => setRoomCode(e.target.value.toUpperCase())}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 uppercase"
              placeholder="Enter room code"
              maxLength={6}
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Your Name
            </label>
            <input
              type="text"
              value={playerName}
              onChange={(e) => setPlayerName(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter your name"
              maxLength={20}
              required
            />
          </div>
          <button
            type="submit"
            disabled={isLoading || !playerName.trim() || !roomCode.trim()}
            className="w-full bg-green-500 text-white py-2 px-4 rounded-md hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? 'Joining...' : 'Join Game'}
          </button>
        </form>
      )}
      
      <div className="mt-6 text-sm text-gray-600">
        <div className="flex justify-between items-center mb-2">
          <h3 className="font-semibold">{rules[language].title}</h3>
          <div className="flex bg-gray-100 rounded-md">
            <button
              onClick={() => setLanguage('en')}
              className={`px-2 py-1 text-xs rounded-l-md ${
                language === 'en' ? 'bg-blue-500 text-white' : 'text-gray-600'
              }`}
            >
              EN
            </button>
            <button
              onClick={() => setLanguage('es')}
              className={`px-2 py-1 text-xs rounded-r-md ${
                language === 'es' ? 'bg-blue-500 text-white' : 'text-gray-600'
              }`}
            >
              ES
            </button>
          </div>
        </div>
        <ul className="space-y-1 text-xs">
          {rules[language].rules.map((rule, index) => (
            <li key={index}>• {rule}</li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default GameLobby;