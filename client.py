import sys
from system import System


def main():
    system = System()

    try:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue

            parts = line.split()
            if len(parts) < 1:
                continue

            command = parts[0]

            if command == "clear":
                system.clear_all()
                continue

            if len(parts) != 3:
                continue

            sku = parts[1]
            quantity_str = parts[2]

            try:
                quantity = int(quantity_str)
            except ValueError:
                continue

            if command == "sell":
                system.sell(sku, quantity)
            elif command == "buy":
                system.buy(sku, quantity)

    except KeyboardInterrupt:
        pass
    finally:
        system.close()


if __name__ == "__main__":
    main()
