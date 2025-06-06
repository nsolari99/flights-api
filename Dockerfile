FROM python:3.12-slim AS base
WORKDIR /code
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY pyproject.toml poetry.lock* /code/
RUN pip install poetry && poetry config virtualenvs.create false \
  && poetry install --only main --no-root

COPY app /code/app
COPY README.md /code/
COPY tests /code/tests
COPY passengers_20.json /code/
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
