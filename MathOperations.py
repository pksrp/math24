import math

def calculate(expression):
    try:
        result = eval(expression, {"__builtins__": None}, math.__dict__)
        return result
    except Exception as e:
        return str(e)

# ตัวอย่างการทดสอบ
if __name__ == "__main__":
    print(calculate("math.log(100)"))
    print(calculate("math.sqrt(16)"))
    print(calculate("5 * 10"))
