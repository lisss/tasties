import os
import psycopg2  # type: ignore
from typing import List

MAX_QUANTITY = 1000000


class Order:
    def __init__(
        self, order_type: str, sku: str, quantity: int, remaining: int = None, db_id: int = None
    ):
        self.order_type = order_type
        self.sku = sku
        self.quantity = quantity
        self.remaining = (
            remaining if remaining is not None else (quantity if order_type == "sell" else 0)
        )
        self.db_id = db_id

    def get_status(self) -> str:
        return f"remaining:{self.remaining}" if self.remaining > 0 else "closed"

    def __str__(self) -> str:
        return f"{self.order_type} {self.sku} {self.quantity} {self.get_status()}"


class System:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            database=os.getenv("DB_NAME", "inventory"),
            user=os.getenv("DB_USER", "ferovinum"),
            password=os.getenv("DB_PASSWORD", "ferovinum"),
        )
        self.orders: List[Order] = []
        self._load_orders()

    def _load_orders(self) -> None:
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, order_type, sku, quantity, remaining FROM orders ORDER BY id")
        for row in cursor.fetchall():
            self.orders.append(Order(row[1], row[2], row[3], row[4], row[0]))

    def _save_order(self, order: Order) -> None:
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO orders (order_type, sku, quantity, remaining) VALUES (%s, %s, %s, %s) RETURNING id",
            (order.order_type, order.sku, order.quantity, order.remaining),
        )
        order.db_id = cursor.fetchone()[0]
        self.conn.commit()

    def _update_order(self, order: Order) -> None:
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE orders SET remaining = %s WHERE id = %s",
            (order.remaining, order.db_id),
        )
        self.conn.commit()

    def _print_all_orders(self) -> None:
        for order in self.orders:
            print(f"system:< {order}")

    def sell(self, sku: str, quantity: int) -> None:
        if quantity <= 0 or quantity > MAX_QUANTITY:
            self._print_all_orders()
            return

        order = Order("sell", sku, quantity)
        self.orders.append(order)
        self._save_order(order)
        self._print_all_orders()

    def buy(self, sku: str, quantity: int) -> None:
        if quantity <= 0 or quantity > MAX_QUANTITY:
            self._print_all_orders()
            return

        fulfilled = 0
        for order in self.orders:
            if order.order_type == "sell" and order.sku == sku and order.remaining > 0:
                take = min(order.remaining, quantity - fulfilled)
                fulfilled += take
                if fulfilled >= quantity:
                    break

        if fulfilled > 0:
            remaining = fulfilled
            for order in self.orders:
                if order.order_type == "sell" and order.sku == sku and order.remaining > 0:
                    take = min(order.remaining, remaining)
                    order.remaining -= take
                    self._update_order(order)
                    remaining -= take
                    if remaining == 0:
                        break

            buy_order = Order("buy", sku, fulfilled)
            self.orders.append(buy_order)
            self._save_order(buy_order)

        self._print_all_orders()

    def clear_all(self) -> None:
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM orders")
        self.conn.commit()
        self.orders = []
        print("system:< All orders cleared")

    def close(self) -> None:
        self.conn.close()
