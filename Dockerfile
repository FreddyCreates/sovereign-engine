# Corporate Enterprise Multi-Stage Dockerfile for Sovereign Substrate
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt || true

# Production Runner Stage
FROM python:3.11-slim as runner

WORKDIR /app

# Create non-root security user
RUN useradd -m -u 1000 appuser

COPY --from=builder /root/.local /home/appuser/.local
COPY . /app

RUN chown -R appuser:appuser /app
USER appuser

ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

EXPOSE 8089

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8089/health')" || exit 1

CMD ["python", "sovereign_revenuecat_protocols/real_world_ecosystem_pipeline.py"]
