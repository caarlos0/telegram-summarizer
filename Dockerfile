FROM ghcr.io/astral-sh/uv:python3.12-trixie-slim
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*
ARG TARGETPLATFORM
COPY $TARGETPLATFORM/telegram_summarizer*.whl /tmp/
RUN ls /tmp/
RUN uv venv
ENV UV_HTTP_TIMEOUT=300
RUN uv pip install torch --index-url https://download.pytorch.org/whl/cpu
RUN uv pip install /tmp/*.whl
ENTRYPOINT [ "uv", "run", "-m", "telegram_summarizer" ]
