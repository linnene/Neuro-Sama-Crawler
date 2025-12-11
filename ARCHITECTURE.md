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

## 数据流
(在此处描述数据如何流动)
