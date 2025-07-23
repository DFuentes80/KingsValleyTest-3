import React from 'react';

const GameBoard = ({ board, selectedSquare, onSquareClick, currentPlayer, gameStatus }) => {
  const renderPiece = (piece) => {
    if (!piece) return '';
    
    const color = piece.player === 1 ? 'text-blue-600' : 'text-red-600';
    return (
      <span className={`text-2xl font-bold ${color}`}>
        {piece.type}
      </span>
    );
  };

  const renderSquare = (row, col) => {
    const piece = board[row][col];
    const isSelected = selectedSquare && selectedSquare.row === row && selectedSquare.col === col;
    const isCenter = row === 2 && col === 2;
    
    let cellClasses = "w-15 h-15 border border-gray-400 flex items-center justify-center text-2xl cursor-pointer";
    
    if (isSelected) {
      cellClasses += " ring-4 ring-yellow-400";
    }
    
    if (isCenter) {
      cellClasses += " bg-yellow-50";
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
      <div className="grid grid-cols-5 gap-0.5 mb-4 bg-gray-300 p-2">
        {Array.from({ length: 5 }, (_, row) =>
          Array.from({ length: 5 }, (_, col) => renderSquare(row, col))
        )}
      </div>
      
      <div className="text-center">
        {gameStatus === 'waiting' && (
          <p className="text-lg text-gray-600">Waiting for second player...</p>
        )}
        {gameStatus === 'in_progress' && (
          <p className="text-lg font-semibold">
            Player {currentPlayer}'s turn
          </p>
        )}
        {gameStatus === 'finished' && (
          <p className="text-xl font-bold text-green-600">
            Game Over! Check winner status.
          </p>
        )}
      </div>
    </div>
  );
};

export default GameBoard;