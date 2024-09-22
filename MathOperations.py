def check_solution(numbers, solution):
    try:
        # Replace 'numbers' in solution string
        for i in range(4):
            solution = solution.replace(f"n{i+1}", str(numbers[i]))
        
        # Evaluate the solution safely
        result = eval(solution)
        return result == 24
    except Exception as e:
        print(f"Error in solution: {e}")
        return False