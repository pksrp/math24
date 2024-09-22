import socket
import threading
import random
from Database import update_score, init_db
from MathOperations import check_solution
from util import log_activity  # Assuming util has logging or utility functions

# Initialize the database
init_db()

# Function to generate 4 random numbers
def generate_numbers():
    return [random.randint(1, 10) for _ in range(4)]

# Handling client connections
def handle_client(conn, addr, player_name, game_data):
    conn.sendall(f"Welcome {player_name}!".encode())
    while True:
        conn.sendall(f"Your numbers are: {game_data['numbers']}".encode())
        solution = conn.recv(1024).decode()
        
        if check_solution(game_data['numbers'], solution):
            conn.sendall("Correct! You won!".encode())
            update_score(player_name, 1)
            game_data['winner'] = player_name
            break
        else:
            conn.sendall("Incorrect. Try again.".encode())
    
    # Logging activity (example utility function)
    log_activity(f"Player {player_name} from {addr} solved the puzzle!")

# Start the server and game logic
def start_game():
    # Set up server socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('192.168.100.48', 5555))  # Replace 0.0.0.0 with your machine's IP
    server.listen(2)
    print("Server is running and waiting for connections...")

    players = {}
    game_data = {
        'numbers': generate_numbers(),
        'winner': None
    }

    while len(players) < 2:
        conn, addr = server.accept()
        conn.sendall("Enter your name: ".encode())
        player_name = conn.recv(1024).decode()
        players[player_name] = conn
        print(f"{player_name} connected from {addr}")
        threading.Thread(target=handle_client, args=(conn, addr, player_name, game_data)).start()

    # Wait for the winner
    while not game_data['winner']:
        pass

    # Announce winner to both players
    for player, conn in players.items():
        if player == game_data['winner']:
            conn.sendall("You are the winner!".encode())
        else:
            conn.sendall("You lost. Better luck next time.".encode())

    server.close()

if __name__ == "__main__":
    start_game()