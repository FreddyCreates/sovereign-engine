# Sovereign Books API server
FROM python:3.11-slim AS builder

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends gcc \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.11-slim AS runner

WORKDIR /app
RUN useradd -m -u 1000 appuser
COPY --from=builder /root/.local /home/appuser/.local
COPY . /app
RUN mkdir -p /app/data && chown -R appuser:appuser /app
USER appuser

ENV PATH=/home/appuser/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    SOVEREIGN_BOOKS_DB=/app/data/sovereign_books.db

EXPOSE 8090

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8090/health')" || exit 1

CMD ["python", "sovereign_dashboard_server.py"]
