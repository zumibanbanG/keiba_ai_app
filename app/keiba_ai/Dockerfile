FROM python:3.14-slim

WORKDIR /app

# システム依存関係のインストール (libgomp1 に加え、playwrightの依存関係を追加)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock README.md ./

RUN python -m pip install --upgrade pip && \
    pip install poetry --no-cache-dir && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root && \
    poetry cache clear --all pypi

COPY src /app/src

RUN poetry install --no-interaction --no-ansi

# --- ここを修正 ---
# ブラウザ本体のインストール
RUN poetry run playwright install chromium
# ブラウザの実行に必要なOSライブラリをインストール（root権限で実行される）
RUN poetry run playwright install-deps chromium
# ------------------

EXPOSE 8501

ENTRYPOINT [ "poetry", "run", "streamlit", "run", "src/keiba_ai/main.py", "--server.port=8501", "--server.enableCORS=false"]