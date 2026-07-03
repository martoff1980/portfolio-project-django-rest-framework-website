FROM python:3.11-slim
LABEL maintainer="admin@station.api"

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies for building some packages (like psycopg2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt first to leverage Docker cache
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Open port for Django
EXPOSE 8000