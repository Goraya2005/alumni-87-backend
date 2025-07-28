# FROM python:3.10.13‐slim
FROM python:3.13-slim

WORKDIR /app

# Install build‑tools and your Python deps
COPY requirements.txt .
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get purge -y build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy in your code
COPY . .

# Use a fixed container port
ENV PORT 10000
EXPOSE 10000

# Launch Uvicorn (or whatever your start command is)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
