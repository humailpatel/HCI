def initialize():
    value = 10
    print("Initialized value to", value)
    return value

def increment(value):
    value += 1
    print("Incremented value to", value)
    return value

def double(value):
    value *= 2
    print("Doubled value to", value)
    return value

def display(value):
    print("The current value is", value)

def main():
    value = initialize()
    value = increment(value)
    value = double(value)
    display(value)

if __name__ == "__main__":
    main()