FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y bash && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY client.py system.py ./
COPY scripts/test.sh ./test.sh
RUN chmod +x test.sh

CMD ["/bin/bash", "test.sh"]
