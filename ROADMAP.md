# 项目路线图 (Roadmap)

## 阶段 1: 初始化 (已完成)
- [x] 项目结构搭建 (src layout)
- [x] CI/CD 配置
- [x] 文档初始化
- [x] 环境配置 (Python 3.14, uv)
- [x] 基础配置模块 (Config)

## 阶段 2: 核心爬虫功能 (进行中)
- [x] 直播间监控模块 (Monitor)
    - [x] Bilibili API 对接
    - [x] 多直播间配置支持
- [x] 弹幕爬取模块 (Crawler)
    - [x] Selenium + Headless Chrome 基础架构
    - [x] Bilibili 弹幕 DOM 解析
    - [x] Docker 环境适配
- [ ] 数据前处理 (Preprocessor)
- [ ] 数据传输管道 (Pipeline)

## 阶段 3: 微服务扩展 (计划中)
- [x] 通知模块 (Notifier)
    - [x] Webhook 接口实现
    - [x] 联动控制逻辑
- [ ] 音频微服务 (Neuro-Audio-Worker)
    - [ ] 独立项目搭建
    - [ ] Streamlink 拉流
    - [ ] Faster-Whisper 集成
    - [ ] GPU 环境适配

## 阶段 4: 数据分析与展示
- [ ] 数据清洗
- [ ] 可视化报表

## 阶段 5: 维护与优化
- [ ] 性能优化
- [ ] 长期监控
