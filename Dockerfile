# Use the exact Python version you want
FROM python:3.13-slim

WORKDIR /app

# Copy only requirements first for better caching
COPY requirements.txt .

# Install OS packages needed to build psycopg2‑binary and other C‑exts
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       libpq-dev \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get purge -y build-essential \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# Copy the rest of your code
COPY . .

# Expose the port your app uses
ENV PORT 10000
EXPOSE 10000

# Start your app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
