# Use Python 3.11 instead of 3.13
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essential \
      libpq-dev \
 && pip install --no-cache-dir -r requirements.txt \
 && apt-get purge -y build-essential \
 && rm -rf /var/lib/apt/lists/*

COPY . .

ENV PORT 10000
EXPOSE 10000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
