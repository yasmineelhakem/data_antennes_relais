FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for psycopg2 and build tools
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --default-timeout=200 -r requirements.txt

COPY . .

# Expose port for the dashboard
EXPOSE 8050

CMD ["python", "dashboard/app.py"]
