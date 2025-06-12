FROM python:3.9-slim
WORKDIR /app

# Instalar netcat para healthchecks
RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*

COPY *.py .
CMD ["sh", "-c", "python -u worker.py ${WORKER_ID} ${PORT} ${MONITOR_PORT}"]