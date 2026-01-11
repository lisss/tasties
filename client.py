import sys
from enum import Enum
from system import System


class Command(Enum):
    SELL = "sell"
    BUY = "buy"
    CLEAR = "clear"


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

            if command == Command.CLEAR.value:
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

            if command == Command.SELL.value:
                system.sell(sku, quantity)
            elif command == Command.BUY.value:
                system.buy(sku, quantity)

    except KeyboardInterrupt:
        pass
    finally:
        system.close()


if __name__ == "__main__":
    main()
