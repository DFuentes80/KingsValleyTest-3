#!/usr/bin/env python3
"""
Debug King's Valley Move Validation
"""

import requests
import json

BACKEND_URL = "https://047e5b13-9185-4dd7-8536-a0f87f82e64e.preview.emergentagent.com/api"

def debug_move_validation():
    session = requests.Session()
    
    # Create a new game
    print("Creating new game...")
    create_response = session.post(f"{BACKEND_URL}/game/create", json={"player_name": "Alice"})
    if create_response.status_code != 200:
        print(f"Failed to create game: {create_response.status_code}")
        return
    
    game_data = create_response.json()
    game_id = game_data["game"]["id"]
    room_code = game_data["game"]["room_code"]
    player1_id = game_data["game"]["players"][0]["id"]
    
    print(f"Game created: {game_id}, Room: {room_code}")
    
    # Join game with second player
    print("Joining game with second player...")
    join_response = session.post(f"{BACKEND_URL}/game/join", json={"room_code": room_code, "player_name": "Bob"})
    if join_response.status_code != 200:
        print(f"Failed to join game: {join_response.status_code}")
        return
    
    join_data = join_response.json()
    player2_id = join_data["game"]["players"][1]["id"]
    
    # Get current board state
    print("\nGetting current board state...")
    game_response = session.get(f"{BACKEND_URL}/game/{game_id}")
    if game_response.status_code != 200:
        print(f"Failed to get game state: {game_response.status_code}")
        return
    
    game = game_response.json()
    board = game["game_state"]["board"]
    current_player = game["game_state"]["current_player"]
    
    print(f"Current player: {current_player}")
    print("\nBoard state:")
    for i, row in enumerate(board):
        row_str = ""
        for j, cell in enumerate(row):
            if cell:
                row_str += f"P{cell['player']}{cell['type']} "
            else:
                row_str += "--- "
        print(f"Row {i}: {row_str}")
    
    # Test various moves to understand the sliding rules
    test_moves = [
        # Player 1 moves (bottom row pieces)
        {"from": (4, 0), "to": (3, 0), "desc": "P1 pawn up 1 square"},
        {"from": (4, 0), "to": (2, 0), "desc": "P1 pawn up 2 squares"},
        {"from": (4, 0), "to": (1, 0), "desc": "P1 pawn up 3 squares"},
        {"from": (4, 0), "to": (0, 0), "desc": "P1 pawn up 4 squares (blocked by P2 pawn)"},
        {"from": (4, 1), "to": (3, 1), "desc": "P1 pawn up 1 square"},
        {"from": (4, 1), "to": (0, 1), "desc": "P1 pawn up to blocked position"},
    ]
    
    print(f"\nTesting moves for Player {current_player}:")
    for move in test_moves:
        from_row, from_col = move["from"]
        to_row, to_col = move["to"]
        
        payload = {
            "game_id": game_id,
            "player_id": player1_id if current_player == 1 else player2_id,
            "from_row": from_row,
            "from_col": from_col,
            "to_row": to_row,
            "to_col": to_col
        }
        
        response = session.post(f"{BACKEND_URL}/game/move", json=payload)
        status = "✅ VALID" if response.status_code == 200 else "❌ INVALID"
        
        piece_at_from = board[from_row][from_col]
        piece_desc = f"P{piece_at_from['player']}{piece_at_from['type']}" if piece_at_from else "Empty"
        
        print(f"{status}: {move['desc']} - ({from_row},{from_col}) to ({to_row},{to_col}) - Piece: {piece_desc}")
        if response.status_code != 200:
            try:
                error_detail = response.json().get("detail", "Unknown error")
                print(f"   Error: {error_detail}")
            except:
                print(f"   Error: {response.text}")
        
        # If move was successful, break to avoid changing game state
        if response.status_code == 200:
            print("   Move successful! Stopping further tests to preserve game state.")
            break

if __name__ == "__main__":
    debug_move_validation()