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

- **弹幕本地存储**：弹幕数据采集后首先写入本地 jsonl 文件，便于后续统一整理、归档或批量上传。
- **Pipeline 管理**：`APIClient.register_crawler(crawler)` 会为每个爬虫分配文件句柄并挂载到爬虫对象，`on_crawler_stop` 会关闭句柄，防止资源泄漏。
- **弹幕写盘字段**：在写入时自动过滤内部使用的 `ct`（弹幕出现时间标识），同时在每条记录中加入 `now` 字段（格式 `%y-%m-%d-%H%M`，例如 `25-12-07-1450`）以标注写盘时间。
- **上传脚本与批量发送**：新增 `scripts/scp.sh`（支持 `--dry-run`、`--output-dir`、SSH key、重试），并在 `APIClient` 中实现 `send_data` 用于异步触发该脚本并捕获日志/返回码。
- **Audio 请求鲁棒性**：`AudioCrawler` 的网络请求已切换为带浏览器头的 `_fetch_json`，包含重试和超时设置，以降低被 412/反爬拦截的概率，并修复了协程未 await 的 bug。
- **Docker 构建与测试**：Dockerfile 能在构建阶段运行测试，镜像命名为 `neuro-sama-crawler:latest`。


## 文档
- [项目架构](ARCHITECTURE.md)
- [扩展说明](EXTENSIONS.md)
- [测试说明](TESTING.md)
- [开发日志](CHANGELOG.md)
- [项目路线图](ROADMAP.md)
