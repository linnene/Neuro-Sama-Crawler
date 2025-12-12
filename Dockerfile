
# 使用官方 Python 镜像
FROM selenium/standalone-chrome:latest

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY . /app

USER root
# 安装 uv
RUN pip install --no-cache-dir uv

# 安装所有依赖（包括 dev 依赖）
RUN uv sync --all-extras --dev

# 构建时运行测试，失败则中断构建
RUN uv run pytest

# 生产环境启动主程序
CMD ["uv", "run", "python", "src/main.py"]
