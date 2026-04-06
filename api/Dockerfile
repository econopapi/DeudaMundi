FROM python:3.12-slim

WORKDIR /app

# Copy metadata first (for caching)
COPY pyproject.toml README.md ./

# Install build tools
RUN pip install --upgrade pip setuptools wheel

# Copy the actual source code
COPY app ./app
COPY scripts ./scripts
COPY tests ./tests

# Install your package
RUN pip install .

# Default command (adjust to your entrypoint)
CMD ["python", "-m", "app"]
