# 项目架构

## 概述
本文档描述了 Neuro-sama Crawler 的高层架构。

## 目录结构
- `src/`: 源代码目录
  - `main.py`: 程序入口
  - `config.py`: 配置管理模块
- `tests/`: 测试文件夹
- `.github/workflows/`: CI/CD 配置
- `pyproject.toml`: 项目依赖与构建配置

## 模块设计
### 配置模块 (`src/config.py`)
负责加载环境变量（`.env`）并提供类型安全的配置对象。目前主要管理后端接口的连接信息。

### 爬虫模块 (`src/crawler`)
负责具体的直播间数据采集。
- **技术栈**: Selenium + Headless Chrome。
- **采集策略**:
    - **页面加载**: 使用无头浏览器加载直播间页面。
    - **数据提取**: 通过 `execute_script` 注入 JavaScript 代码，直接从 DOM 中批量提取弹幕数据（`data-uname`, `data-danmaku`, `data-ct`）。相比传统的 Python `find_elements` 循环，这种方式性能提升显著且更稳定。
    - **去重机制**: 利用 Bilibili 弹幕元素的 `data-ct` 属性作为唯一标识符 (UUID)。
    - **内存管理**: 维护一个 `seen_cts` 集合，仅存储当前 DOM 树中存在的弹幕 ID。随着 B 站前端自动移除旧弹幕 DOM，爬虫也会自动释放对应的 ID 内存，无需手动设置固定大小的缓存队列，完美避免内存泄漏。

## 数据流
1. **Monitor** 轮询 Bilibili API 检查开播状态。
2. 一旦开播，启动 **Crawler** 实例。
3. **Crawler** 持续从浏览器 DOM 中提取新弹幕。
4. 提取的数据经过去重和简单清洗。
5. (待实现) 数据推送到 **Pipeline** 发送至后端。
