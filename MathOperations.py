import re

def strict_validate_solution(solution, numbers):
    '''
    Validates if the given solution:
    1. Uses all the numbers from the input exactly once.
    2. Does not use any additional numbers.
    3. Results in 24.

    Args:
    solution (str): The mathematical expression provided by the user.
    numbers (list of int): The set of numbers that must be used in the solution.

    Returns:
    bool: True if the solution is valid, False otherwise.
    '''

    # Extract all numbers from the solution
    used_numbers = list(map(int, re.findall(r'\d+', solution)))

    # Ensure no additional numbers are used
    if sorted(used_numbers) != sorted(numbers):
        return False

    try:
        # Check if the result of the solution is 24
        result = eval(solution)
        return result == 24
    except:
        return False

def check_solution(numbers, solution):
    try:
        # Replace 'n1', 'n2', 'n3', 'n4' in solution string with the actual numbers
        for i in range(4):
            solution = solution.replace(f"n{i+1}", str(numbers[i]))
        
        # Use strict validation for the solution
        return strict_validate_solution(solution, numbers)
    except Exception as e:
        print(f"Error in solution: {e}")
        return False