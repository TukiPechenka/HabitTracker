FROM python:3.12

ENV PYTHONUNBUFFERED=1

COPY poetry.lock poetry.lock
COPY pyproject.toml pyproject.toml

RUN pip install --upgrade pip poetry
RUN poetry install --without alembic

WORKDIR /app

COPY src src