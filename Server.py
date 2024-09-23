
import socket
import threading
import random
from MathOperations import check_solution
from util import log_activity
from Database import update_score, init_db

# Initialize the database
init_db()

# Function to generate 4 random numbers
def generate_numbers():
    return [random.randint(1, 10) for _ in range(4)]

# Handling client connections
def handle_client(conn, addr, player_name, game_data):
    conn.sendall(f"Welcome {player_name}!".encode())  # Send welcome message to the player
    
    # Send the numbers to the player (even in single player mode)
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
        except socket.timeout:
            conn.sendall("Connection timed out. Please try again.".encode())
            break
        
        if check_solution(game_data['numbers'], solution):  # Check if the solution is correct
            conn.sendall("Correct! You won!".encode())
            update_score(player_name, 1)
            game_data['winner'] = player_name
            break
        else:
            conn.sendall("Incorrect. Try again.".encode())

    log_activity(f"Player {player_name} from {addr} solved the puzzle!")

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

    # Ask players if they want to play again
    for player, conn in players.items():
        conn.sendall("Play again? (yes/no)".encode())
    
    play_again = []
    for player, conn in players.items():
        try:
            response = conn.recv(1024).decode()
        except socket.timeout:
            response = "no"  # Default to "no" if player doesn't respond in time
        play_again.append(response.strip().lower())

    if "yes" in play_again:
        # Start a new game session
        start_game(players, game_data)
    else:
        for conn in players.values():
            conn.sendall("Thanks for playing! Exiting...".encode())
        print("Game over. Exiting...")
        for conn in players.values():
            conn.close()

def accept_connections(server):
    players = {}
    game_data = {'numbers': None, 'winner': None}

    # Accept a single player or two players
    conn, addr = server.accept()
    conn.settimeout(20)  # Set a timeout for the connection
    conn.sendall("Enter your name: ".encode())  # Ask for the player's name
    try:
        player_name = conn.recv(1024).decode()  # Receive the player's name
    except socket.timeout:
        print(f"Connection from {addr} timed out. Disconnecting.")
        conn.close()
        return
    players[player_name] = conn
    print(f"{player_name} connected from {addr}")
    
    # Start the game for single player mode
    start_game(players, game_data)

if __name__ == "__main__":
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 5555))  # This will allow connections from all network interfaces
    server.listen(2)
    print("Server is running and waiting for connections...")

    accept_connections(server)
