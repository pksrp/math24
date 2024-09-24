
import socket
import tkinter as tk
from tkinter import messagebox
from Music import play_music
import time

client = None
max_retries = 3  # Maximum number of retries for connection

def show_result_and_options(result):
    """Show result (win/lose) and ask to play again or quit."""
    result_window = tk.Toplevel(root)
    result_window.title("Game Result")

    result_label = tk.Label(result_window, text=result)
    result_label.pack()

    def play_again():
        result_window.destroy()
        reset_game()

    def quit_game():
        client.close()
        root.destroy()

    play_again_button = tk.Button(result_window, text="Play Again", command=play_again)
    play_again_button.pack()

    quit_button = tk.Button(result_window, text="Quit", command=quit_game)
    quit_button.pack()

def reset_game():
    """Resets the game for a new round."""
    problem_label.config(text="Waiting for a new problem...")
    solution_entry.delete(0, tk.END)
    connect_to_server()  # Reconnect for a new game

def send_solution():
    solution = solution_entry.get()
    try:
        client.send(solution.encode())
        result = client.recv(1024).decode()  # Receive the result (Correct/Incorrect) from the server
        show_result_and_options(result)
    except socket.timeout:
        messagebox.showerror("Timeout", "Connection timed out while sending solution. Please try again.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to send solution: {e}")

    # After game ends, receive the play again prompt
    try:
        play_again_prompt = client.recv(1024).decode()
        if play_again_prompt == 'yes':
            client.send("yes".encode())
            receive_problem()  # Start a new game session
        else:
            client.send("no".encode())
            messagebox.showinfo("Exit", "Thanks for playing!")
            root.quit()  # Close the GUI
    except socket.timeout:
        messagebox.showerror("Timeout", "Connection timed out while receiving play again prompt. Please try again.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to receive play again prompt: {e}")

def receive_problem():
    """Receives the welcome message and problem (numbers) from the server and displays it in the GUI."""
    try:
        welcome_msg = client.recv(1024).decode()  # Receive the welcome message
        messagebox.showinfo("Welcome", welcome_msg)  # Display the welcome message

        problem = client.recv(1024).decode()  # Now receive the numbers from the server
        problem_label.config(text=f"Your numbers are: {problem}")  # Update the problem label
    except socket.timeout:
        messagebox.showerror("Timeout", "Connection timed out while receiving problem. Please try again.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to receive problem: {e}")

def connect_to_server():
    global client
    retry_count = 0
    while retry_count < max_retries:
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.settimeout(30)  # Set longer timeout for the connection
            client.connect(('127.0.0.1', 5555))  # Ensure IP matches your server
            name = name_entry.get()
            client.send(name.encode())  # Send player name to server
            
            # After connecting, immediately receive the welcome message and problem (numbers) from the server
            receive_problem()  # Now, wait to receive both the welcome and the problem
            break
        except socket.timeout:
            retry_count += 1
            messagebox.showwarning("Timeout", f"Connection timed out. Retrying {retry_count}/{max_retries}...")
            time.sleep(2)  # Wait for 2 seconds before retrying
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect to server: {e}")
            break
    else:
        messagebox.showerror("Error", "Failed to connect after multiple attempts. Please try again later.")

# GUI setup
root = tk.Tk()
root.title("Game 24 Client")

# Play background music
play_music()

# Player name input
name_label = tk.Label(root, text="Enter your name:")
name_label.pack()
name_entry = tk.Entry(root)
name_entry.pack()

# Connect button
connect_button = tk.Button(root, text="Connect", command=connect_to_server)
connect_button.pack()

# Problem display
problem_label = tk.Label(root, text="You will see the numbers here once connected...")
problem_label.pack()

# Solution input
solution_label = tk.Label(root, text="Enter your solution:")
solution_label.pack()
solution_entry = tk.Entry(root)
solution_entry.pack()

# Submit button
submit_button = tk.Button(root, text="Submit Solution", command=send_solution)
submit_button.pack()

# Start the GUI main loop
root.mainloop()
