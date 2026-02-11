FROM python:3.14-slim

WORKDIR /app

COPY pyproject.toml poetry.lock README.md ./

ENV python -m pip install --upgrade pip && \
    pip install poetry --no-cache-dir && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root && \
    poetry cache clear --all pypi

COPY src /app/src

RUN poetry install --no-interaction --no-ansi

EXPOSE 8501

ENTRYPOINT [ "poetry", "run", "streamlit", "run", "src/keiba_ai/web_app.py", "--server.port=8501", "--server.enableCORS=false"]