import socket
import tkinter as tk
from tkinter import messagebox
from Music import play_music
import time
from util import show_help  # Import the show_help function from the other file
import operator
from itertools import permutations, product
from PIL import Image, ImageTk

server_ip =''
client = None
max_retries = 3  # Maximum number of retries for connection

# Auto-solver function to find a solution for the given numbers
def find_solution(problem, target=24):
    if client is None:  # Check if the client is connected
        messagebox.showerror("Connection Error", "You are not connected to the server. Please connect first.")
        return
    
    ops = ['+', '-', '*', '/']
    
    for num_order in permutations(problem):
        for op_order in product(ops, repeat=3):
            expression = f"({num_order[0]} {op_order[0]} {num_order[1]}) {op_order[1]} {num_order[2]} {op_order[2]} {num_order[3]}"
            try:
                if eval(expression) == target:
                    return expression
            except ZeroDivisionError:
                continue
    return None

# Hint function that gives the first operator as a hint
def give_hint(problem):
    if client is None:  # Check if the client is connected
        messagebox.showerror("Connection Error", "You are not connected to the server. Please connect first.")
        return
    
    solution = find_solution(problem)
    if solution:
        return f"Try using '{solution.split()[1]}' as the first operator"
    return "No valid solution found."


# Function to find and display the solution
def show_solution():
    if client is None:  # Check if the client is connected
        messagebox.showerror("Connection Error", "You are not connected to the server. Please connect first.")
        return
    
    problem = problem_label.cget("text").replace("Your numbers are: ", "").split(", ")
    problem = [int(num) for num in problem]  # Convert string numbers to integers
    
    solution = find_solution(problem)
    if solution:
        messagebox.showinfo("Solution", f"Solution: {solution}")
    else:
        messagebox.showinfo("Solution", "No valid solution found.")
        
# Append a value to the solution entry
def append_to_solution(value):
    current_solution = solution_entry.get()
    # Check if the current solution is valid before appending
    if value in ['+', '-', '*', '/'] and (current_solution == '' or current_solution[-1] in ['+', '-', '*', '/']):
        messagebox.showerror("Invalid Input", "You cannot add another operator.")
        solution_entry.delete(0, tk.END)  # Clear on invalid operator
        return
    
    solution_entry.delete(0, tk.END)
    solution_entry.insert(0, current_solution + str(value))

# Calculate the solution and check if it equals 24
def calculate_solution():
    solution = solution_entry.get()
    try:
        # Evaluate the expression and check if it equals 24
        result = eval(solution)  # Use with caution; ensure input is sanitized
        if result == 24:
            send_solution(solution)  # Send to server
        else:
            messagebox.showerror("Invalid Solution", "The solution does not equal 24.")
            solution_entry.delete(0, tk.END)  # Clear on invalid solution
    except Exception as e:
        messagebox.showerror("Error", f"Invalid calculation: {e}")
        solution_entry.delete(0, tk.END)  # Clear on error

#Show result (win/lose) and ask to play again or quit
def show_result_and_options(result):
    result_window = tk.Toplevel(root)
    result_window.title("Game Result")

    result_label = tk.Label(result_window, text=result)
    result_label.pack()

    def play_again():
        result_window.destroy()
        reset_game()

    def quit_game():
        if client:
            client.close()
        root.destroy()

    play_again_button = tk.Button(result_window, text="Play Again", command=play_again)
    play_again_button.pack()

    quit_button = tk.Button(result_window, text="Quit", command=quit_game)
    quit_button.pack()

# Resets the game for a new round
def reset_game():
    """Resets the game for a new round."""
    problem_label.config(text="Waiting for a new problem...")
    solution_entry.delete(0, tk.END)
    connect_to_server()  # Reconnect for a new game

# Show result (win/lose) and ask to play again or quit
def send_solution():
    solution = solution_entry.get()
    
    if not solution:  # Check if the solution is empty
        messagebox.showwarning("Invalid Input", "Solution cannot be empty. Please try again.")
        return
    
    try:
        client.send(solution.encode())
        print(f"Solution sent: {solution}")  # Debugging
        result = client.recv(1024).decode()  # Receive the result (Correct/Incorrect) from the server
        show_result_and_options(result)
    except socket.timeout:
        messagebox.showerror("Timeout", "Connection timed out while sending solution. Please try again.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to send solution: {e}")

    # After game ends, receive the play again prompt
    try:
        play_again_prompt = client.recv(1024).decode()
        print(f"Play again response: {play_again_prompt}")  # Debugging
        if play_again_prompt == 'yes':
            client.send("yes".encode())
            receive_problem()  # Start a new game session
        elif play_again_prompt == 'no':
            client.send("no".encode())
            messagebox.showinfo("Exit", "Thanks for playing!")
            root.quit()  # Close the GUI
    except socket.timeout:
        messagebox.showerror("Timeout", "Connection timed out while receiving play again prompt. Please try again.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to receive play again prompt: {e}")
        
# Receives the welcome message and problem (numbers) from the server and displays it in the GUI
def receive_problem():
    try:
        welcome_msg = client.recv(1024).decode()  # Receive the welcome message
        messagebox.showinfo("Welcome", welcome_msg)  # Display the welcome message

        problem_str = client.recv(1024).decode()  # Now receive the numbers as a string from the server
        problem_label.config(text=f"Your numbers are: {problem_str}")  # Update the problem label
        problem = [int(num) for num in problem_str.split()]  # Convert string numbers to a list of integers
        print(f"Received problem: {problem}")  # Debugging
        
        # Provide the solution and hint based on the received problem
        solution = find_solution(problem)  # Pass the problem as a list of integers
        hint = give_hint(problem)
        print(f"Solution: {solution}, Hint: {hint}")  # Debugging
        
        # Show Hint button
        hint_button = tk.Button(main_frame, text="Show Hint", bg="#cceeff", font=("Helvetica", 12), command=lambda: animate_button_click(connect_button) or messagebox.showinfo("Hint", hint))
        hint_button.pack(pady=5)

        # Show Solution button
        solution_button = tk.Button(main_frame, text="Show Solution", bg="#cceeff", font=("Helvetica", 12), command=lambda: animate_button_click(connect_button) or messagebox.showinfo("solution", find_solution(problem)))  # Pass the current problem
        solution_button.pack(pady=5)
        
    except socket.timeout:
        messagebox.showerror("Timeout", "Connection timed out while receiving problem. Please try again.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to receive problem: {e}")

# Establish a connection to the server and handle retries
def connect_to_server():
    global client
    retry_count = 0
    while retry_count < max_retries:
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.settimeout(30)  # Set longer timeout for the connection
            client.connect((server_ip, 5555))  # Ensure IP matches your server
            name = name_entry.get()
            client.send(name.encode())  # Send player name to server
            print(f"Player name sent: {name}")  # Debugging
            
            # After connecting, immediately receive the welcome message and problem (numbers) from the server
            receive_problem()  # Now, wait to receive both the welcome and the problem
            
            connect_button.pack_forget()  # Hide the "Connect" button after successful connection
            break
        except socket.timeout:
            retry_count += 1
            messagebox.showwarning("Timeout", f"Connection timed out. Retrying {retry_count}/{max_retries}...")
            time.sleep(2)  # Wait for 2 seconds before retrying
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect to server: {e}")
            break
    if retry_count == max_retries:
        messagebox.showerror("Error", "Failed to connect after multiple attempts.")
        
# Request and display the player's score history from the server           
def show_score_history():
    
    if client is None:  # Check if the client is connected
        messagebox.showerror("Connection Error", "You are not connected to the server. Please connect first.")
        return
    
    try:
        client.send("get_score_history".encode())  # Send a request to get the score history
        score_history = client.recv(4096).decode()  # Receive the score history (ensure the buffer size is large enough)
        score_window = tk.Toplevel(root)
        score_window.title("Score History")
        
        history_label = tk.Label(score_window, text="Score History:")
        history_label.pack()
        
        score_text = tk.Text(score_window, height=10, width=50)
        score_text.insert(tk.END, score_history)
        score_text.pack()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to retrieve score history: {e}")
        
# Animation: Change button color temporarily when clicked
def animate_button_click(button):
    original_color = button.cget("bg")
    button.config(bg="yellow")  # Change to yellow on click
    button.after(200, lambda: button.config(bg=original_color))  # Change back after 200ms

# GUI setup
root = tk.Tk()
root.title("Game 24 Client")
root.geometry("1000x650")  # Increased height for better layout

# Create a frame for the image on the left
image_frame = tk.Frame(root)
image_frame.pack(side=tk.LEFT)

# Load an image (make sure the image is in the same directory or provide the full path)
image = tk.PhotoImage(file="moodeng.png")  # Replace with the correct image path
image_label = tk.Label(image_frame, image=image, bg="#ffffff")
image_label.pack()

root.configure(bg="#f0f0f5")  # Light gray background

main_frame = tk.Frame(root, bg="#ffffff", bd=5, relief="groove")  # Main frame with border
main_frame.pack()

play_music()

# Player name input section
name_label = tk.Label(main_frame, text="Enter your name:", font=("Helvetica", 12), bg="#ffffff")
name_label.pack(pady=5)
name_entry = tk.Entry(main_frame, font=("Helvetica", 12))
name_entry.pack(pady=5)

# Connect button
connect_button = tk.Button(main_frame, text="Connect", bg="#cceeff", font=("Helvetica", 12), command=lambda: animate_button_click(connect_button) or connect_to_server())
connect_button.pack(pady=5)

# Problem display section
problem_label = tk.Label(main_frame, text="You will see the numbers here once connected...", font=("Helvetica", 10), bg="#ffffe6", width=40, height=2)
problem_label.pack(pady=5)

# Solution input section
solution_label = tk.Label(main_frame, text="Enter your solution:", font=("Helvetica", 12), bg="#ffffff")
solution_label.pack(pady=5)
solution_entry = tk.Entry(main_frame, font=("Helvetica", 12))
solution_entry.pack(pady=5)

# Frame for calculator buttons
button_frame = tk.Frame(main_frame, bg="#ffffff")
button_frame.pack(pady=5)

buttons = [
    '1', '2', '3',
    '4', '5', '6',
    '7', '8', '9',
    '+', '-', '*', '/', '(', ')',
    'C'
]

button_colors = {
    '1': '#ffcccc', '2': '#ffb3b3', '3': '#ff9999',
    '4': '#ff8080', '5': '#ff6666', '6': '#ff4d4d',
    '7': '#ff3333', '8': '#ff1a1a', '9': '#ff0000',
    '+': '#e6ffe6', '-': '#ccffcc', '*': '#b3ffb3', '/': '#99ff99',
    '(': '#80ff80', ')': '#66ff66', 'C': '#ccf2ff'
}

for button in buttons:
    btn = tk.Button(button_frame, text=button, font=("Helvetica", 12), bg=button_colors[button], width=5, height=2)
    if button == '=':
        btn.config(command=lambda: animate_button_click(btn) or calculate_solution())
    elif button == 'C':
        btn.config(command=lambda: animate_button_click(btn) or solution_entry.delete(0, tk.END))
    else:
        btn.config(command=lambda b=button: animate_button_click(btn) or append_to_solution(b))
    
    btn.grid(row=buttons.index(button) // 4, column=buttons.index(button) % 4, padx=5, pady=5)

# Submit button
submit_button = tk.Button(main_frame, text="Submit Solution", bg="#ccff99", font=("Helvetica", 12), command=lambda: animate_button_click(submit_button) or send_solution())
submit_button.pack(pady=5)

# Score History button
score_history_button = tk.Button(main_frame, text="Score History", bg="#ccff99", font=("Helvetica", 12), command=lambda: animate_button_click(score_history_button) or show_score_history())
score_history_button.pack(pady=5)

# Help button
help_button = tk.Button(main_frame, text="Help", bg="#ccff99", font=("Helvetica", 12), command=lambda: animate_button_click(help_button) or show_help()) 
help_button.pack(pady=5)

# Start the GUI main loop
root.mainloop()
