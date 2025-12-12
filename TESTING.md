# 测试说明

本项目使用 `pytest` 进行测试。

## 测试结构
所有测试文件位于 `tests/` 目录下。

## 运行测试

### 本地运行
推荐使用 `uv` 运行测试：
```bash
uv run pytest
```

或者在激活虚拟环境后运行：
```bash
pytest
```

### CI 环境
本项目配置了 GitHub Actions，每次提交会自动运行测试。详情请见 `.github/workflows/ci.yml`。

## 测试覆盖范围
- **Crawler**: 爬虫生命周期管理。
- **Monitor**: Bilibili API 状态检查。
- **Notifier**: Webhook 通知发送逻辑（Mock 测试）。
- **Pipeline**: 数据发送逻辑。
