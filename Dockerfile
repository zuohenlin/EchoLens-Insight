# syntax=docker/dockerfile:1
FROM python:3.11-slim

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Prevent Python from writing .pyc files, buffer stdout/stderr, and pin common tooling paths
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PATH="/root/.local/bin:${PATH}" \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright \
    # 使用清华 PyPI 镜像加速 pip 下载
    UV_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple \
    UV_EXTRA_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/

# 切换 apt 到阿里云镜像，大幅提升 apt 速度
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    sed -i 's|http://deb.debian.org|https://mirrors.aliyun.com|g' /etc/apt/sources.list.d/debian.sources 2>/dev/null || \
    sed -i 's|http://deb.debian.org|https://mirrors.aliyun.com|g' /etc/apt/sources.list 2>/dev/null || true; \
    apt-get update

# Install system dependencies
# 使用 BuildKit 缓存挂载：apt 包缓存跨构建复用，改代码不会重新下载系统包
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    set -euo pipefail; \
    if apt-cache show libgdk-pixbuf-2.0-0 >/dev/null 2>&1; then \
    GDK_PIXBUF_PKG=libgdk-pixbuf-2.0-0; \
    else \
    GDK_PIXBUF_PKG=libgdk-pixbuf2.0-0; \
    fi; \
    if apt-cache show libasound2t64 >/dev/null 2>&1; then \
    ALSA_PKG=libasound2t64; \
    else \
    ALSA_PKG=libasound2; \
    fi; \
    if apt-cache show libgtk-3-0t64 >/dev/null 2>&1; then \
    GTK_PKG=libgtk-3-0t64; \
    else \
    GTK_PKG=libgtk-3-0; \
    fi; \
    apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    libgl1 \
    libglib2.0-0 \
    "${GTK_PKG}" \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libpangoft2-1.0-0 \
    "${GDK_PIXBUF_PKG}" \
    libffi-dev \
    libcairo2 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libxcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxtst6 \
    libnss3 \
    libxrandr2 \
    libxkbcommon0 \
    "${ALSA_PKG}" \
    libx11-xcb1 \
    libxshmfence1 \
    libgbm1 \
    ffmpeg

# Install uv
RUN curl -LsSf --retry 3 --retry-delay 2 --proto '=https' --proto-redir '=https' --tlsv1.2 https://astral.sh/uv/install.sh | sh

WORKDIR /app

# 拆分 requirements：重量级依赖（torch 等）单独一层，改业务代码不会重装 torch
COPY requirements.txt ./
# BuildKit pip 缓存：pip 包跨构建缓存，不重新下载已有 wheel
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system -r requirements.txt \
    --index-url https://pypi.tuna.tsinghua.edu.cn/simple \
    --extra-index-url https://mirrors.aliyun.com/pypi/simple/

# Install Playwright browser binaries
RUN python -m playwright install chromium

# Copy .env
COPY .env.example .env

# Copy application source
COPY . .

# Ensure runtime directories exist even if ignored in build context
RUN mkdir -p /ms-playwright logs final_reports insight_engine_streamlit_reports media_engine_streamlit_reports query_engine_streamlit_reports

EXPOSE 5000 8501 8502 8503

# Default command launches the Flask orchestrator which starts Streamlit agents
CMD ["python", "app.py"]
