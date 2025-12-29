# 配置模块 - 处理配置读取和管理
import os
import streamlit as st

# 优先从streamlit secrets读取，然后是环境变量，最后是默认值
# Streamlit Secrets配置示例（.streamlit/secrets.toml）：
# [ai_client]
# token = "your-api-token"

DEFAULT_TOKEN = ""
BASE_URL = "https://achuanai.vip/api"

# 尝试从streamlit secrets读取
def load_token_from_secrets():
    """
    从Streamlit Secrets读取API Token
    """
    if hasattr(st, 'secrets'):
        try:
            return st.secrets.get("ai_client", {}).get("token", "")
        except Exception:
            pass
    return ""

# 加载配置
def load_config():
    """
    加载所有配置项
    """
    config = {
        "token": DEFAULT_TOKEN,
        "base_url": BASE_URL
    }
    
    # 优先从streamlit secrets读取
    secrets_token = load_token_from_secrets()
    if secrets_token:
        config["token"] = secrets_token
    
    # 从环境变量读取，覆盖secrets配置
    env_token = os.getenv("AI_CLIENT_TOKEN")
    if env_token:
        config["token"] = env_token
    
    return config

# 初始化配置
CONFIG = load_config()
