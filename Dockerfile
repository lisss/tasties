FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y bash && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY client.py system.py ./
COPY scripts/ ./scripts/
COPY tests/ ./tests/
RUN chmod +x scripts/client.sh scripts/run_tests.sh

CMD ["/bin/bash", "scripts/client.sh"]
