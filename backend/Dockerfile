FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for building python packages
RUN apt-get update && apt-get install -y build-essential libpq-dev

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .