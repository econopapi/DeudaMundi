FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy metadata first (for caching)
COPY pyproject.toml README.md ./

# Install build tools
RUN pip install --upgrade pip setuptools wheel

# Copy the actual source code and scripts
COPY app ./app
COPY scripts ./scripts
COPY tests ./tests

# Install your package
RUN pip install .

# Make the production start script executable
RUN chmod +x /app/scripts/start_api.sh

EXPOSE 8000

# Use production start script which runs migrations and uvicorn
CMD ["./scripts/start_api.sh"]
