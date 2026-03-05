FROM python:3.12-slim
WORKDIR /app

# Copia apenas o pyproject.toml para instalar dependências (aproveita cache de camadas)
COPY pyproject.toml ./
# Cria um pacote instalável mínimo para que o pip consiga ler as deps do pyproject.toml
RUN mkdir -p api && touch api/__init__.py && \
    pip install --no-cache-dir ".[dev]"

# Copia o restante do código após instalar dependências
COPY . .

EXPOSE 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
