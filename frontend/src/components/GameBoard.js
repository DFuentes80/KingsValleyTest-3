import React from 'react';

const GameBoard = ({ board, selectedSquare, onSquareClick, currentPlayer, gameStatus }) => {
  const renderPiece = (piece) => {
    if (!piece) return null;
    
    const isKing = piece.type === 'K';
    const baseClasses = "w-16 h-16 rounded-full flex items-center justify-center shadow-lg border-4 transition-all duration-200";
    
    if (piece.player === 1) {
      // Player 1 - Blue pieces
      if (isKing) {
        return (
          <div className={`${baseClasses} bg-blue-600 border-blue-800 relative`}>
            <div className="w-10 h-10 bg-yellow-300 rounded-full border-2 border-yellow-500 flex items-center justify-center">
              <div className="text-blue-800 font-bold text-lg">♔</div>
            </div>
          </div>
        );
      } else {
        return (
          <div className={`${baseClasses} bg-blue-500 border-blue-700`}>
            <div className="w-6 h-6 bg-blue-200 rounded-full"></div>
          </div>
        );
      }
    } else {
      // Player 2 - Red pieces  
      if (isKing) {
        return (
          <div className={`${baseClasses} bg-red-600 border-red-800 relative`}>
            <div className="w-10 h-10 bg-yellow-300 rounded-full border-2 border-yellow-500 flex items-center justify-center">
              <div className="text-red-800 font-bold text-lg">♔</div>
            </div>
          </div>
        );
      } else {
        return (
          <div className={`${baseClasses} bg-red-500 border-red-700`}>
            <div className="w-6 h-6 bg-red-200 rounded-full"></div>
          </div>
        );
      }
    }
  };

  const renderSquare = (row, col) => {
    const piece = board[row][col];
    const isSelected = selectedSquare && selectedSquare.row === row && selectedSquare.col === col;
    const isCenter = row === 2 && col === 2;
    
    let cellClasses = "w-24 h-24 border-2 border-gray-500 flex items-center justify-center cursor-pointer transition-all duration-200 hover:bg-gray-100";
    
    if (isSelected) {
      cellClasses += " ring-4 ring-yellow-400 ring-opacity-75 bg-yellow-50";
    }
    
    if (isCenter) {
      cellClasses += " bg-gradient-to-br from-yellow-100 to-yellow-200 border-yellow-500";
    } else {
      cellClasses += " bg-white";
    }
    
    return (
      <div
        key={`${row}-${col}`}
        className={cellClasses}
        onClick={() => onSquareClick(row, col)}
      >
        {renderPiece(piece)}
      </div>
    );
  };

  return (
    <div className="flex flex-col items-center">
      <div className="grid grid-cols-5 gap-1 mb-6 bg-gray-600 p-3 rounded-lg shadow-xl">
        {Array.from({ length: 5 }, (_, row) =>
          Array.from({ length: 5 }, (_, col) => renderSquare(row, col))
        )}
      </div>
      
      <div className="text-center">
        {gameStatus === 'waiting' && (
          <p className="text-xl text-gray-600 font-medium">Waiting for second player...</p>
        )}
        {gameStatus === 'in_progress' && (
          <div className="flex items-center justify-center space-x-3">
            <div className={`w-6 h-6 rounded-full ${currentPlayer === 1 ? 'bg-blue-500' : 'bg-red-500'}`}></div>
            <p className="text-xl font-bold">
              Player {currentPlayer}'s turn
            </p>
          </div>
        )}
        {gameStatus === 'finished' && (
          <p className="text-2xl font-bold text-green-600">
            Game Over! Check winner status.
          </p>
        )}
      </div>
      
      <div className="mt-4 flex justify-center space-x-8 text-sm text-gray-600">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 bg-blue-500 rounded-full border-2 border-blue-700 flex items-center justify-center">
            <div className="w-3 h-3 bg-blue-200 rounded-full"></div>
          </div>
          <span>Player 1</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 bg-red-500 rounded-full border-2 border-red-700 flex items-center justify-center">
            <div className="w-3 h-3 bg-red-200 rounded-full"></div>
          </div>
          <span>Player 2</span>
        </div>
        <div className="flex items-center space-x-2">  
          <div className="w-8 h-8 bg-blue-600 rounded-full border-2 border-blue-800 flex items-center justify-center">
            <div className="w-5 h-5 bg-yellow-300 rounded-full border border-yellow-500 flex items-center justify-center text-blue-800 text-sm font-bold">♔</div>
          </div>
          <span>King</span>
        </div>
      </div>
    </div>
  );
};

export default GameBoard;