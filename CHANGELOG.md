# 开发日志 (Changelog)

所有对本项目的显著更改都将记录在此文件中。

## [0.1.0] - 2025-12-11

### Added
- 项目初始化
- Dockerfile (Python 3.14)
- CI Workflow (GitHub Actions)
- 基础文档结构 (README, ARCHITECTURE, etc.)
- `src` 目录结构重构
- 配置管理模块 (`src/config.py`) 支持 `.env` 加载
- 后端接口配置 (`BACKEND_API_URL`, `BACKEND_API_TOKEN`)
- 引入 `uv` 进行依赖管理

### Changed
- 升级项目 Python 版本至 3.14
- 迁移代码至 `src/` 目录布局
- 移除数据库相关配置，专注于后端接口集成

## [0.2.0] - 2025-12-12

### Added
- **监控模块 (Monitor)**:
    - 定义 `BaseMonitor` 抽象基类，规范监控接口。
    - 实现 `BilibiliMonitor`，支持通过 API 检查直播状态 (`check_status`) 和获取直播间信息 (`get_room_info`)。
    - 集成 `httpx` 进行异步 HTTP 请求。
- **配置增强**:
    - `src/config.py` 新增 `BILIBILI_LIVE_API_URL` 和 `BILIBILI_ROOM_IDS` 配置。
    - 支持从环境变量解析多个直播间 ID。
- **测试体系**:
    - 添加 `pytest-asyncio` 支持异步测试。
    - 实现 `tests/test_monitor.py`，包含 Mock 测试和真实 API 集成测试。
    - 完善日志系统 (`src/utils/logger.py`)。

### Changed
- 优化 `get_room_info` 返回字段，移除冗余的 `user_cover`。
- 重构 `main.py` 引入 `asyncio` 和模块初始化逻辑。

## [0.3.0] - 2025-12-12

### Added
- **弹幕爬虫 (Crawler)**:
    - 实现 `DanmakuCrawler`，基于 Selenium 和 Headless Chrome。
    - 适配 Bilibili 直播间弹幕 DOM 结构，支持提取用户名和内容。
    - **性能优化**: 引入 JavaScript 注入 (`execute_script`) 批量提取弹幕，替代低效的 Python 循环查找。
    - **内存优化**: 实现基于 DOM 状态的自动内存管理，利用 `data-ct` 唯一标识符进行智能去重和过期清理。
    - 支持 Docker 环境下的无头模式运行。
- **Docker 支持**:
    - 切换基础镜像为 `selenium/standalone-chrome`，内置 Chrome 和 WebDriver。
    - 优化 Dockerfile，支持 `uv` 依赖安装和构建时测试。
    - 新增 `.dockerignore` 减少构建上下文。
- **测试工具**:
    - 新增 `docker_test.py` 用于 Docker 环境下的冒烟测试。
    - 移除 `httpx`、`websockets` 等不再使用的依赖，引入 `selenium`、`webdriver-manager`。

### Changed
- 爬虫策略从 WebSocket 协议分析转向 Selenium 页面自动化，以应对 API 限制。
- 更新 CI 流程，修复权限问题，确保测试在 Docker 容器中正确运行。

## [0.4.1] - 2025-12-13

### Removed
- **通知模块 (Notifier)**: 移除 `AudioServiceNotifier` 及相关配置。决定放弃微服务架构，转而采用本地录制方案。
- **微服务规划**: 取消 `Neuro-Audio-Worker` 独立服务计划。

### Changed
- **主流程**: 移除 Webhook 通知逻辑，保留多房间监控和弹幕爬虫自动启停功能。

## [0.4.0] - 2025-12-12

### Added
- **通知模块 (Notifier)**:
    - 新增 `AudioServiceNotifier`，用于向外部音频服务发送 Webhook 通知。
    - 支持 `start` 和 `stop` 动作，实现直播状态与录音服务的联动。
- **主流程重构**:
    - 重构 `main.py`，实现完整的监控循环。
    - 支持多房间状态管理，自动处理开播/下播事件。
    - 集成 `Notifier`，在开播时自动通知音频服务，下播时自动停止。
- **配置更新**:
    - 新增 `AUDIO_SERVICE_URL` 配置项。
- **测试**:
    - 新增 `tests/test_notifier.py`，覆盖通知模块的各种场景。

### Planned
- **Neuro-Audio-Worker**: 计划开发独立的音频微服务，负责拉流、提取音频和语音转文字 (Whisper)。

## [0.5.0] - 2025-12-14

### Added
- **Pipeline 管理**:
    - APIClient 支持 register_crawler(crawler: DanmakuCrawler)，注册后自动分配文件句柄并挂载到爬虫对象。
    - 支持 on_crawler_stop 自动关闭文件，防止资源泄漏。
- **弹幕本地存储**:
    - DanmakuCrawler 启动时自动检查/创建 output 目录，并以 room_id+时间戳命名 json 文件。
    - 采集数据实时写入本地，便于后续归档和批量上传。

### Changed
- **数据流**: 采集-本地存储-后处理-归档/上传，替代原有实时推送方案。
