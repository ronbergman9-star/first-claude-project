import random


def main():
    symbol = input("Enter a stock symbol: ").strip().upper()
    change = random.choice(["up", "down"])
    print(f"The stock {symbol} went {change} today!")


if __name__ == "__main__":
    main()
