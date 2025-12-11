# 测试说明

本项目使用 `pytest` 进行测试。

## 测试结构
所有测试文件位于 `tests/` 目录下。

## 运行测试

### 本地运行
确保已安装 `pytest`：
```bash
pip install pytest
```

运行所有测试：
```bash
pytest
```

### CI 环境
本项目配置了 GitHub Actions，每次提交会自动运行测试。详情请见 `.github/workflows/ci.yml`。
