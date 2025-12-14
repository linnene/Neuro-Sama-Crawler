# Neuro-sama Crawler

## 项目简介
这是一个针对 Neuro-sama 直播数据的爬虫项目。

## 功能
- **直播监控**: 实时监控 Bilibili 直播间开播状态。
- **弹幕采集**: 使用 Selenium 自动化采集直播间弹幕。
- **数据处理**: (开发中) 弹幕数据清洗与格式化。
- **数据传输**: (开发中) 将数据推送至后端 API。

## 快速开始

### 依赖
- Python 3.14+
- Docker (推荐用于部署)
- [uv](https://github.com/astral-sh/uv) (推荐用于包管理)
- Chrome & ChromeDriver (本地运行时需要)

### 配置
本项目使用环境变量进行配置。
1. 复制 `.env.example` 为 `.env`。
2. 填入后端接口信息 (`BACKEND_API_URL`, `BACKEND_API_TOKEN`)。
3. 配置直播间 ID (`BILIBILI_ROOM_IDS`)。

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

### Docker 运行
```bash
# 构建镜像
docker build -t neuro-sama-crawler .

# 运行容器
docker run --rm -it neuro-sama-crawler
```

## 新增功能与今日进展

- **弹幕本地存储**：弹幕数据采集后，先本地存储为 jsonl 文件，直播结束后可统一整理、归档或上传。
- **Pipeline 管理**：APIClient 支持爬虫注册，自动为每个房间分配独立数据文件，生命周期内自动管理文件句柄。
- **弹幕爬虫**：DanmakuCrawler 初始化时自动检查/创建 output 目录，并以 room_id+时间戳命名 json 文件，采集数据实时写入。
- **Docker 构建**：可直接使用 `docker build -t neuro-sama-crawler:latest .` 构建镜像。

## 文档
- [项目架构](ARCHITECTURE.md)
- [扩展说明](EXTENSIONS.md)
- [测试说明](TESTING.md)
- [开发日志](CHANGELOG.md)
- [项目路线图](ROADMAP.md)
