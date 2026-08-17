FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir \
    --default-timeout=1000 \
    --retries 5 \
    --index-url https://pypi.org/simple/ \
    -r requirements.txt

COPY . .

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Use shell form so $PORT can be expanded at runtime by platforms like Render
CMD ["sh", "-c", "gunicorn main:app -k uvicorn.workers.UvicornWorker --workers 1 --bind 0.0.0.0:$PORT --access-logfile=- --error-logfile=- --log-level=info --timeout=120 --keep-alive=5"]
