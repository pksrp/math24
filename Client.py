import socket
import tkinter as tk
from tkinter import messagebox
from Music import play_music

client = None

def send_solution():
    solution = solution_entry.get()
    client.send(solution.encode())
    result = client.recv(1024).decode()  # Receive the result (Correct/Incorrect) from the server
    messagebox.showinfo("Result", result)

    # After game ends, receive the play again prompt
    play_again_prompt = client.recv(1024).decode()
    answer = messagebox.askquestion("Game Over", play_again_prompt)
    
    if answer == 'yes':
        client.send("yes".encode())
        receive_problem()  # Start a new game session
    else:
        client.send("no".encode())
        messagebox.showinfo("Exit", "Thanks for playing!")
        root.quit()  # Close the GUI

def receive_problem():
    """Receives the welcome message and problem (numbers) from the server and displays it in the GUI."""
    try:
        welcome_msg = client.recv(1024).decode()  # Receive the welcome message
        messagebox.showinfo("Welcome", welcome_msg)  # Display the welcome message

        problem = client.recv(1024).decode()  # Now receive the numbers from the server
        problem_label.config(text=f"Your numbers are: {problem}")  # Update the problem label
    except Exception as e:
        messagebox.showerror("Error", f"Failed to receive problem: {e}")

def connect_to_server():
    global client
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(('192.168.100.48', 5555))  # Ensure IP matches your server
        name = name_entry.get()
        client.send(name.encode())  # Send player name to server
        
        # After connecting, immediately receive the welcome message and problem (numbers) from the server
        receive_problem()  # Now, wait to receive both the welcome and the problem
    except Exception as e:
        print(f"Error connecting to server: {e}")
        messagebox.showerror("Connection Error", f"Failed to connect to server: {e}")

# GUI setup
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
problem_label = tk.Label(root, text="Your numbers are:")
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

# Help button
help_button = tk.Button(root, text="Help", command=lambda: messagebox.showinfo("Help", "Enter your solution to reach 24"))
help_button.pack()

root.mainloop()