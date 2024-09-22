import socket
import threading
from MathOperations import calculate
from Database import update_score

SERVER = "127.0.0.1"
PORT = 5555
ADDR = (SERVER, PORT)
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

clients = []
ready_players = []

def handle_client(client_socket, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    clients.append(client_socket)
    
    connected = True
    while connected:
        try:
            msg = client_socket.recv(1024).decode('utf-8')
            if msg == 'DISCONNECT':
                connected = False
            elif msg.startswith("PLAYER_READY"):
                ready_players.append(client_socket)
                if len(ready_players) == 2:
                    start_game()  # เริ่มเกมเมื่อมีผู้เล่นครบ 2 คน
            else:
                expression, username = msg.split('|')
                result = calculate(expression)
                update_score(username, result)
                client_socket.send(f"Result: {result}".encode('utf-8'))
        except:
            connected = False

    client_socket.close()
    print(f"[DISCONNECTED] {addr} disconnected.")

def start_game():
    for client in clients:
        client.send("GAME_START".encode('utf-8'))

def start():
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        client_socket, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        thread.start()

if __name__ == "__main__":
    print("[STARTING] Server is starting...")
    start()
