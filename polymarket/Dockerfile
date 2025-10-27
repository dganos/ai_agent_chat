# Polymarket Auto Flows - Gradio app container
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps for scientific libs (pandas/numpy) and TLS
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first for better caching
COPY polymarket/requirements.txt /app/polymarket/requirements.txt
RUN pip install --upgrade pip && pip install -r /app/polymarket/requirements.txt

# Copy app code
COPY polymarket/ /app/polymarket/

WORKDIR /app/polymarket
EXPOSE 7860

CMD ["python", "app.py"]
