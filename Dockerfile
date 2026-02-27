# syntax=docker/dockerfile:1

# 基于 BettaFish 官方镜像构建，只叠加 EchoLens 品牌/前端改动
FROM ghcr.io/666ghj/bettafish:latest

# 覆盖 EchoLens 品牌前端页面
COPY templates/ /app/templates/

# 覆盖 EchoLens Logo
COPY static/image/echolens_logo.png /app/static/image/echolens_logo.png

# 生成 MindSpider config（上游镜像未包含此文件，从 example 生成）
RUN cp /app/MindSpider/config.py.example /app/MindSpider/config.py 2>/dev/null || true
