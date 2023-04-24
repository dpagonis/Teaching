import random

def generate_random_values(value):
    random_values = []

    lower_limit = max(0, value * 0.33)
    upper_limit = value * 2

    for _ in range(3):
        while True:
            random_value = random.uniform(lower_limit, upper_limit)
            if random_value < value * 0.8 or random_value > value * 1.2:
                random_values.append(random_value)
                break

    return random_values

def main():
    value = float(input("Enter a value: "))
    random_values = generate_random_values(value)
    formatted_random_values = [f"{random_value:.4f}" for random_value in random_values]
    print("Three random values generated are: ")
    for rv in formatted_random_values:
        print(rv)

if __name__ == "__main__":
    main()
