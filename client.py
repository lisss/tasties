import sys
from enum import Enum
from system import System


class Command(Enum):
    SELL = "sell"
    BUY = "buy"
    CLEAR = "clear"


def main():
    system = System()

    # i honestly asked the Internet about how to implement accepting input and providing an output,
    # since i never did that before
    try:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue

            cli_input_string = line.split()
            if len(cli_input_string) < 1:
                continue

            command = cli_input_string[0]

            if command == Command.CLEAR.value:
                system.clear_all()
                continue

            if len(cli_input_string) != 3:
                continue

            sku = cli_input_string[1]
            quantity_str = cli_input_string[2]

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
        # we need to stop it anyway, even if we failed to do other things
        system.close()


if __name__ == "__main__":
    main()
