# Use Python 3.11 instead of 3.13
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential libpq-dev && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get purge -y build-essential && \
    rm -rf /var/lib/apt/lists/*

COPY . .

# Make initialization script executable
RUN chmod +x init_production_db.py

# Set environment variables for production
ENV ENVIRONMENT=production
ENV PORT 10000

EXPOSE 10000

# Run initialization script and then start the app
CMD ["sh", "-c", "python init_production_db.py && uvicorn main:app --host 0.0.0.0 --port 10000"]
