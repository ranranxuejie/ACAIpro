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
            # 从achuan_ai section读取token
            return st.secrets.get("achuan_ai", {}).get("token", "")
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
    if hasattr(st, 'secrets'):
        try:
            # 从achuan_ai section读取配置
            secrets_config = st.secrets.get("achuan_ai", {})
            secrets_token = secrets_config.get("token", "")
            secrets_base_url = secrets_config.get("base_url", "")
            
            # 更新token
            if secrets_token:
                config["token"] = secrets_token
            
            # 更新base_url
            if secrets_base_url:
                config["base_url"] = secrets_base_url
        except Exception:
            pass
    
    # 从环境变量读取，覆盖secrets配置
    env_token = os.getenv("AI_CLIENT_TOKEN")
    if env_token:
        config["token"] = env_token
    
    env_base_url = os.getenv("AI_CLIENT_BASE_URL")
    if env_base_url:
        config["base_url"] = env_base_url
    
    return config

# 初始化配置
CONFIG = load_config()
