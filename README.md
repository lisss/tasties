# Selling & buying spirits (I believe Shiraz & Talisker would be the choice :))
We do store and consume the stuff cronologically (FIFO): first that was sold is the first that would be bought

## How to run it locally

We use Docker

**Start the services:**
```bash
docker-compose build
docker-compose up -d
```

**Connect to the client:**
```bash
docker-compose exec inventory ./test.sh
```

## Examples of the input and output

### Sell
```
client:> sell wine 1000
system:< sell wine 1000 remaining:1000

client:> sell whisky 100
system:< sell wine 1000 remaining:1000
system:< sell whisky 100 remaining:100
```

### Buy
```
client:> buy wine 500
system:< sell wine 1000 remaining:500
system:< sell whisky 100 remaining:100
system:< buy wine 500 closed
```

### Check DB
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

### Clear Database
```bash
client:> clear
```

## How It Works

- Each `sell` creates a new order with inventory
- Each `buy` consumes from the earliest `sell` orders
- After every command, status is either `remaining:<count>` or `closed`

## Architecture

- **PostgreSQL** - DB
- **client.py** - input shell
- **system.py** - output
- **scripts/test.sh** - a test script to check the behaviour
