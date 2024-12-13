# Use the official Python 3.12 slim image
FROM python:3.12-slim

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies and add necessary GPG keys
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    libc-dev \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt --no-cache-dir

# Copy the entire project into the Docker container
COPY . .

# Download GeoLite2-Country.mmdb
RUN wget -O GeoLite2-Country.mmdb https://github.com/P3TERX/GeoLite.mmdb/raw/download/GeoLite2-Country.mmdb -q


# Generate SSL certificates (key.pem and cert.pem)
RUN openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout key.pem \
    -out cert.pem \
    -subj "/C=US/ST=State/L=City/O=Bitads/CN=localhost"

# Install the application in editable mode
RUN pip install -e .

# Build the application
RUN python setup.py install_lib
RUN python setup.py build
