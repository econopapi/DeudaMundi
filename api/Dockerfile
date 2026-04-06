FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

COPY pyproject.toml README.md ./
RUN pip install --upgrade pip && \
    pip install .

COPY . .
RUN chmod +x /app/scripts/start_api.sh

EXPOSE 8000

CMD ["./scripts/start_api.sh"]
