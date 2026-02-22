FROM python:3.14-slim

WORKDIR /app

COPY pyproject.toml poetry.lock README.md ./

RUN apt-get update && apt-get install -y libgomp1 && \
    python -m pip install --upgrade pip && \
    pip install poetry --no-cache-dir && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root && \
    poetry cache clear --all pypi

COPY src /app/src

RUN poetry install --no-interaction --no-ansi

RUN poetry run playwright install

EXPOSE 8501

ENTRYPOINT [ "poetry", "run", "streamlit", "run", "src/keiba_ai/main.py", "--server.port=8501", "--server.enableCORS=false"]