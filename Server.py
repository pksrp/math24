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
    
    # Send the same numbers to both players
    numbers_str = ' '.join(map(str, game_data['numbers']))  # Convert numbers to string
    conn.sendall(numbers_str.encode())  # Send the problem (numbers) to the client
    
    while True:
        solution = conn.recv(1024).decode()  # Receive the player's solution
        
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

    # Wait for a winner
    while not game_data['winner']:
        pass

    # Announce the winner to both players
    for player, conn in players.items():
        if player == game_data['winner']:
            conn.sendall("You are the winner!".encode())
        else:
            conn.sendall("You lost. Better luck next time.".encode())

    # Ask both players if they want to play again
    for player, conn in players.items():
        conn.sendall("Play again? (yes/no)".encode())
    
    play_again = []
    for player, conn in players.items():
        response = conn.recv(1024).decode()
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

    # Accept two players
    while len(players) < 2:
        conn, addr = server.accept()
        conn.sendall("Enter your name: ".encode())  # Ask for the player's name
        player_name = conn.recv(1024).decode()  # Receive the player's name
        players[player_name] = conn
        print(f"{player_name} connected from {addr}")
    
    # Start the game
    start_game(players, game_data)

if __name__ == "__main__":
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('192.168.100.48', 5555))  # Ensure this IP matches your machine's IP
    server.listen(2)
    print("Server is running and waiting for connections...")

    accept_connections(server)