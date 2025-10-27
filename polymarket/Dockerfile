# Polymarket Auto Flows Gradio App Dockerfile
FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for better caching
COPY polymarket/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy app
COPY polymarket /app

# Expose Gradio default port
EXPOSE 7860

# Runtime envs (override at run time)
ENV PORT=7860 \
    DRY_RUN=1

CMD ["python", "app.py"]
