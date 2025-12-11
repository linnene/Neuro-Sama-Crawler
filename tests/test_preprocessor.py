import pytest
from preprocessor.cleaner import DataCleaner

def test_clean_danmaku_passthrough():
    # 目前是透传逻辑
    raw_data = {"user": "test", "content": "hello"}
    cleaned = DataCleaner.clean_danmaku(raw_data)
    assert cleaned == raw_data

def test_filter_spam_default():
    # 目前默认返回 False (不过滤)
    assert DataCleaner.filter_spam("some content") is False
