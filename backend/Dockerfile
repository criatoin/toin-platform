FROM python:3.12-slim
WORKDIR /app

# Instala dependências primeiro (aproveita cache de camadas)
COPY pyproject.toml ./
RUN pip install --no-cache-dir pip setuptools wheel && \
    pip install --no-cache-dir fastapi "uvicorn[standard]" pydantic-settings supabase \
    langchain langgraph langchain-groq langfuse httpx python-dotenv \
    google-api-python-client google-auth

# Copia o código após instalar dependências
COPY . .

EXPOSE 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
