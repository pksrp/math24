import socket
import tkinter as tk
from tkinter import messagebox
from Music import play_music
from util import show_help  # Utility for showing in-game help

client = None

def send_solution():
    solution = solution_entry.get()
    client.send(solution.encode())
    result = client.recv(1024).decode()
    messagebox.showinfo("Result", result)

def receive_problem():
    problem = client.recv(1024).decode()
    problem_label.config(text=problem)

def connect_to_server():
    global client
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('127.0.0.1', 5555))
    name = name_entry.get()
    client.send(name.encode())
    receive_problem()

# GUI using Tkinter
root = tk.Tk()
root.title("Game 24 Client")

# Player name input
name_label = tk.Label(root, text="Enter your name:")
name_label.pack()
name_entry = tk.Entry(root)
name_entry.pack()

# Connect button
connect_button = tk.Button(root, text="Connect", command=connect_to_server)
connect_button.pack()

# Problem display
problem_label = tk.Label(root, text="Waiting for the problem...")
problem_label.pack()

# Solution entry
solution_label = tk.Label(root, text="Enter your solution:")
solution_label.pack()
solution_entry = tk.Entry(root)
solution_entry.pack()

# Submit button
submit_button = tk.Button(root, text="Submit", command=send_solution)
submit_button.pack()

# Play music button
music_button = tk.Button(root, text="Play Music", command=play_music)
music_button.pack()

# Help button (assuming show_help is defined in util)
help_button = tk.Button(root, text="Help", command=show_help)
help_button.pack()

root.mainloop()