import socket
import threading
import random
import sqlite3

from MathOperations import check_solution
from util import log_activity
from Database import update_score, init_db

from MathOperations import strict_validate_solution  # Import the correct function

def handle_client(conn, addr, player_name, game_data):
    conn.sendall(f"Welcome {player_name}!".encode())  # Send welcome message to the player
    
    # Send the numbers to the player
    numbers_str = ' '.join(map(str, game_data['numbers']))  # Convert numbers to string
    try:
        conn.sendall(numbers_str.encode())  # Send the problem (numbers) to the client
    except Exception as e:
        print(f"Failed to send problem: {e}")
        conn.close()
        return

    while True:
        try:
            solution = conn.recv(1024).decode()  # Receive the player's solution
            print(f"Received solution from {player_name}: {solution}")  # Debugging
        except socket.timeout:
            conn.sendall("Connection timed out. Please try again.".encode())
            break
        
        # Use strict validation for the solution
        if strict_validate_solution(solution, game_data['numbers']):  # Check if the solution is correct
            conn.sendall("Correct! You won!".encode())
            game_data['winner'] = player_name
            break
        else:
            conn.sendall("Incorrect. Try again.".encode())

    conn.close()  # Close connection after game ends

# Initialize the database
init_db()

def get_score_history():
    """Retrieve the score history of a specific player from the database."""
    conn = sqlite3.connect('game24.db')
    c = conn.cursor()
    c.execute("SELECT * FROM scores",)
    result = c.fetchall()
    conn.close()
    return result

# Function to generate 4 random numbers
def generate_numbers():
    return [random.randint(1, 10) for _ in range(4)]

# Handling client connections
def handle_client(conn, addr, player_name, game_data):
    # Send welcome message and problem
    numbers_str = ' '.join(map(str, game_data['numbers']))
    try:
        conn.sendall(numbers_str.encode())
    except Exception as e:
        print(f"Failed to send problem: {e}")
        conn.close()
        return

    while True:
        try:
            message = conn.recv(1024).decode()
            if message == "get_score_history":
                score_history = get_score_history()
                if score_history:
                    history_str = "\n".join([f"Player: {player}, Score: {score}" for player, score in score_history])
                else:
                    history_str = "No score history available."
                conn.sendall(history_str.encode())
                continue
            
            solution = message  # The message could also be the player's solution
            print(f"Received solution from {player_name}: {solution}")
            
            if check_solution(game_data['numbers'], solution):  # Check if solution is correct
                conn.sendall("Correct! You won!".encode())
                update_score(player_name, 1)
                game_data['winner'] = player_name
                break
            else:
                conn.sendall("Incorrect. Try again.".encode())
                break
        except socket.timeout:
            conn.sendall("Connection timed out. Please try again.".encode())
            break
        except Exception as e:
            print(f"Error handling client: {e}")
            conn.close()
            break
    conn.close()

def start_game(players, game_data):
    game_data['numbers'] = generate_numbers()
    game_data['winner'] = None

    # Wait for a winner (no need to wait in single player mode)
    if len(players) > 1:
        while not game_data['winner']:
            pass
    else:
        # Instead of 'player1', use the actual player's name
        player_name = list(players.keys())[0]
        handle_client(players[player_name], None, player_name, game_data)

def accept_connections(server):
    while True:
        conn, addr = server.accept()  # Accept new connection
        conn.settimeout(30)  # Set a timeout for the connection
        
        threading.Thread(target=client_thread, args=(conn, addr)).start()  # Start a new thread for each client

def client_thread(conn, addr):
    game_data = {'numbers': None, 'winner': None}

    conn.sendall("game start".encode())  # Ask for the player's name
    try:
        player_name = conn.recv(1024).decode()  # Receive the player's name
        print(f"Player {player_name} connected from {addr}")  # Debugging
    except socket.timeout:
        print(f"Connection from {addr} timed out. Disconnecting.")
        conn.close()
        return

    players = {player_name: conn}

    # Start the game for single player mode
    start_game(players, game_data)

if __name__ == "__main__":
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('127.0.0.1', 5555))  # This will allow connections from all network interfaces
    server.listen(5)  # Listen for up to 5 connections
    print("Server is running and waiting for connections...")

    accept_connections(server)