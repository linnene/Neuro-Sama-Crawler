FROM selenium/standalone-chrome:latest

# set workdir and user
WORKDIR /app
USER root

# 1. install python
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ffmpeg \
    ca-certificates && \
    update-ca-certificates && \
    ln -sf /usr/bin/ffmpeg /usr/local/bin/ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# 2. install python dependencies
RUN pip install --no-cache-dir uv

# 3. setup non-root user
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --all-extras --dev

# 4. copy project files
COPY . .

# 5. 最后同步项目
RUN uv sync --frozen

CMD ["uv", "run", "python", "src/test.py"]