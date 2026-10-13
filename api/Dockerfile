FROM python:3.12-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY pyproject.toml README.md ./
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./
COPY scripts ./scripts

RUN pip install --upgrade pip setuptools wheel && chmod +x /app/scripts/start_api.sh


FROM base AS development

COPY tests ./tests
RUN pip install -e ".[dev]"

EXPOSE 8000

CMD ["./scripts/start_api.sh"]


FROM base AS production

RUN pip install .

EXPOSE 8000

CMD ["./scripts/start_api.sh"]
