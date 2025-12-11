# Neuro-sama Crawler

## 项目简介
这是一个针对 Neuro-sama 直播数据的爬虫项目。

## 功能
- (待开发)

## 快速开始

### 依赖
- Python 3.14+
- Docker (可选)
- [uv](https://github.com/astral-sh/uv) (推荐用于包管理)

### 配置
本项目使用环境变量进行配置。
1. 复制 `.env.example` 为 `.env`。
2. 填入后端接口信息 (`BACKEND_API_URL`, `BACKEND_API_TOKEN`)。

### 安装
使用 uv (推荐):
```bash
uv sync
```
或者使用 pip:
```bash
pip install -e .
```

### 运行
```bash
# 使用 uv
uv run python src/main.py

# 或者直接运行 (需激活虚拟环境)
python src/main.py
```

## 文档
- [项目架构](ARCHITECTURE.md)
- [扩展说明](EXTENSIONS.md)
- [测试说明](TESTING.md)
- [开发日志](CHANGELOG.md)
- [项目路线图](ROADMAP.md)
