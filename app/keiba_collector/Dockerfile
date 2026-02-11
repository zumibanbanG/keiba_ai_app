FROM python:3.14-slim

WORKDIR /app

COPY pyproject.toml poetry.lock README.md ./

RUN python -m pip install --upgrade pip && \
    pip install poetry --no-cache-dir && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root && \
    poetry cache clear --all pypi

COPY src /app/src

RUN poetry install --no-interaction --no-ansi

CMD [ "poetry", "run", "python", "src/keiba_collector/main.py"]