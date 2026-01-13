# 🍷 Selling & buying spirits
_(I believe Shiraz & Talisker would be the very choice 😊)_

## Let's get started on what we're doing here

In the wine and spirits business, clients need capital. They sell us their inventory, and later they buy it back when they need it

## Business logic

We store and consume the stuff chronologically (FIFO, `queue` data structure approach): first that was sold is the first that would be bought

## Architecture
(btw, it was drawn manually with charcoal and pencil)

![Diagram](./public/arch_diagram.jpg)

### Order (the receipt)
Every time you sell or buy something, we create a receipt according to our inventory schema (order type, sku, quantity, remaining)

E.g.:
- `sell` creates a new order
- `buy` consumes from the earliest `sell` orders
- After every command, status is either `remaining:<count>` or `closed`

### Examples:
```bash
Day 1: You sell us 1000 bottles of wine (Order #1)
Day 2: You sell us 500 more bottles (Order #2)
Day 3: You want to buy back 1200 bottles

# ℹ️ examples of the input and output

# >>> sell
client:> sell wine 1000
system:< sell wine 1000 remaining:1000

client:> sell whisky 100
system:< sell wine 1000 remaining:1000
system:< sell whisky 100 remaining:100

# >>> buy
client:> buy wine 500
system:< sell wine 1000 remaining:500
system:< sell whisky 100 remaining:100
system:< buy wine 500 closed
```

## Tech details

### How to run it locally

The service uses Docker

```bash
# start the services
docker-compose build
docker-compose up -d

# the docker also inits the DB for the sake of some persistence,the SQL script it stored at scripts/init_db.sql

# connect to the client
docker-compose exec inventory ./scripts/client.sh
```

### What's inside

**`client.py` - The input handler**
- Reads commands from stdin and parses them to be processed further (e.g. inserted into the DB)

**`system.py` - The main logic of the system**
- Manages orders (buy, sell, clear)
- Manages data persistence: talks to the DB, loads data on startup, saves after each transaction

### A few tips

#### Check DB
```bash
docker-compose exec db psql -U ferovinum -d inventory -c "SELECT * FROM orders;"
```
The sample output would be solmething like

```bash
 id | order_type |  sku   | quantity | remaining
----+------------+--------+----------+-----------
 41 | sell       | wine   |     1000 |         0
 44 | buy        | wine   |      500 |         0
 42 | sell       | whisky |      100 |         0
 45 | sell       | whisky |      100 |        80
 46 | buy        | whisky |      120 |         0
 43 | buy        | wine   |      500 |         0
(6 rows)
```

#### Clear DB
```bash
client:> clear
```

## Design decisions & tradeoffs

### Why SQL DB instead of NoSQL?

Our storage is definitely an OLTP one, hence I used the most typical (and familiar to me) DB solution. I could use MySQL or SQLite instead, just feel more comfortable with Postgres

A few considerations on this choice anyway:

- **Relational data:** orders have a clear structure, and we can extend the DB schema easily, should we need to
- **ACID:** When you buy 500 bottles, we need that transaction to either fully happen or not happen at all. No in-between states. I know that for such tiny DB it's not super critical, but I would imagine that I work with real production
- **Simpler for straightforward use cases:** NoSQL shines with unstructured data or massive scale. We have structured transactions and straightforward queries, so I didn't see a reason why not to use typical SQL solution

### Why Two-Pass Buy Algorithm?

The buy logic does two passes through the orders:
1. **First pass:** Calculate if we can fulfill (and how much)
2. **Second pass:** Actually modify the data

*Why not just do it in one pass?*

Because we don't want to modify the database unless we're committed to the transaction. It's like checking your bank balance before transferring money - you want to know if you CAN do it before you DO it.
Plus, it keeps the code cleaner: calculation logic separate from execution logic.

### Why silent error handling?

Because the task description says so 😊 Almost kidding. My personal opinion is that we must at least notify developers that something went wrong in the system (observability), this is why I never liked the 'silent errors' approach. We definitely do not need to crash the system, but we need to report. Maybe I misread the requirement, sorry for that 😶. But, anyways, I would like to extend it to alert in case of problems, not silently swallow them

## Testing

```bash
docker-compose exec inventory bash scripts/run_tests.sh
```

The idea is to automate testing of the very basic operations, because we can never be sure that thing wouldn't break one day. The ideal solution is CI, but I don't have time for that right now :(