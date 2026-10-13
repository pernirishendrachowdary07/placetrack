# Use official lightweight Python runtime
FROM python:3.11-slim

# Prevent Python from writing .pyc bytecode and unbuffer logging output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies (compiler tools and PostgreSQL client library)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code into container
COPY . /app/

# Expose Django port
EXPOSE 8000

# Start production server using Gunicorn WSGI
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "placetrack.wsgi:application"]
