FROM python:3.12-slim
WORKDIR /app

# Instala dependencias do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl && \
    rm -rf /var/lib/apt/lists/*

# Copia codigo e instala dependencias
COPY . .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

EXPOSE 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
