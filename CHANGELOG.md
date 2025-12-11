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
