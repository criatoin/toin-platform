FROM python:3.12-slim
WORKDIR /app

# Instala dependencias do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl && \
    rm -rf /var/lib/apt/lists/*

# Instala dependencias de producao diretamente (sem buildar o pacote)
COPY pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
      "fastapi>=0.115.0" \
      "uvicorn[standard]>=0.30.0" \
      "pydantic-settings>=2.0.0" \
      "supabase>=2.0.0" \
      "langchain>=0.3.0" \
      "langgraph>=0.2.0" \
      "langchain-openai>=0.2.0" \
      "langfuse>=2.0.0" \
      "httpx>=0.27.0" \
      "python-dotenv>=1.0.0" \
      "google-api-python-client>=2.0.0" \
      "google-auth>=2.0.0" \
      "google-auth-oauthlib>=1.0.0"

# Copia codigo apos instalar deps (aproveita cache de camadas Docker)
COPY . .

EXPOSE 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
