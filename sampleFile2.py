def greet(name):
    return f"Hello, {name}!"

def calculate_sum(a, b):
    return a + b

def print_message():
    message = "This is a test message"
    print(message)

def nested_function_example():
    def inner_function(x):
        return x * x
    return inner_function(5)

if __name__ == "__main__":
    print(greet("Alice"))
    print("Sum of 3 and 4 is:", calculate_sum(3, 4))
    print_message()
    print("Result from nested function:", nested_function_example())