import os
import sys
import pytest
import psycopg2

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from system import System, Order


@pytest.fixture
def test_system():
    os.environ["DB_NAME"] = "inventory_test"

    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database="postgres",
        user=os.getenv("DB_USER", "ferovinum"),
        password=os.getenv("DB_PASSWORD", "ferovinum"),
    )
    conn.autocommit = True
    cursor = conn.cursor()

    cursor.execute("DROP DATABASE IF EXISTS inventory_test")
    cursor.execute("CREATE DATABASE inventory_test")
    cursor.close()
    conn.close()

    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database="inventory_test",
        user=os.getenv("DB_USER", "ferovinum"),
        password=os.getenv("DB_PASSWORD", "ferovinum"),
    )
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE orders (
            id SERIAL PRIMARY KEY,
            order_type TEXT NOT NULL,
            sku TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            remaining INTEGER NOT NULL
        )
    """
    )
    conn.commit()
    cursor.close()
    conn.close()

    system = System()
    yield system
    system.close()


def test_fifo_logic(test_system):
    test_system.sell("wine", 1000)
    test_system.sell("wine", 500)
    test_system.buy("wine", 1200)

    assert test_system.orders[0].remaining == 0
    assert test_system.orders[1].remaining == 300
    assert test_system.orders[2].quantity == 1200


def test_partial_fulfillment(test_system):
    test_system.sell("wine", 300)
    test_system.buy("wine", 500)

    assert test_system.orders[0].remaining == 0
    assert test_system.orders[1].quantity == 300


def test_spec_example(test_system):
    test_system.sell("wine", 1000)
    test_system.sell("whisky", 100)
    test_system.buy("wine", 500)
    test_system.buy("wine", 1000)
    test_system.sell("whisky", 100)
    test_system.buy("whisky", 120)

    assert test_system.orders[0].remaining == 0
    assert test_system.orders[1].remaining == 0
    assert test_system.orders[4].remaining == 80


def test_persistence(test_system):
    test_system.sell("wine", 1000)
    test_system.buy("wine", 300)
    test_system.close()

    new_system = System()

    assert len(new_system.orders) == 2
    assert new_system.orders[0].remaining == 700

    new_system.close()
