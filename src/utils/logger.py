import logging
import sys

from typing import Optional

def setup_logger(name: Optional[str] = None, level: int = logging.INFO):
    """
    配置全局日志。
    如果不指定 name (None)，则配置根日志记录器 (Root Logger)，
    这样项目中所有使用 logging.getLogger(__name__) 的模块都会继承此配置。
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 防止重复添加 Handler (例如在多次调用 setup_logger 时)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger
