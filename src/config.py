import os
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件
# 默认加载项目根目录下的 .env
# 假设 main.py 在 src/ 目录下，根目录在上一级
ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

class Config:
    """
    配置管理类
    从环境变量中获取配置，如果不存在则使用默认值或抛出错误
    """
    
    # 数据库配置
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", 5432))
    DB_USER = os.getenv("DB_USER", "admin")
    DB_PASSWORD = os.getenv("DB_PASSWORD")

    # API 密钥
    TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
    TWITCH_CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")

    @classmethod
    def validate(cls):
        """验证必要的配置是否存在"""
        required_vars = [
            "DB_PASSWORD", 
            "TWITCH_CLIENT_ID", 
            "TWITCH_CLIENT_SECRET"
        ]
        missing = [var for var in required_vars if not getattr(cls, var)]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

# 实例化配置对象（可选，或者直接使用类）
config = Config()
