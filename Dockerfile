FROM python:3.10-slim-bookworm

# Avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt update && apt install -y \
    git \
    && apt clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /VJ-Post-Search-Bot

# Copy requirements first (better caching)
COPY requirements.txt .

# Upgrade pip & install python deps
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy full project
COPY . .

# Start bot (single main process – correct for Docker)
CMD ["python3", "main.py"]
