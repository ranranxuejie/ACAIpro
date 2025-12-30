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
        "base_url": BASE_URL,
        # 对话参数配置
        "contextCount": 25,
        "frequencyPenalty": 0,
        "maxToken": 0,
        "presencePenalty": 0,
        "prompt": "请使用用户交互的语言进行回复",
        "temperature": 0,
        "topSort": 0
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
            
            # 读取对话参数配置
            for key in ["contextCount", "frequencyPenalty", "maxToken", "presencePenalty", "prompt", "temperature", "topSort"]:
                if key in secrets_config:
                    config[key] = secrets_config[key]
        except Exception:
            pass
    
    # 从环境变量读取，覆盖secrets配置
    env_token = os.getenv("AI_CLIENT_TOKEN")
    if env_token:
        config["token"] = env_token
    
    env_base_url = os.getenv("AI_CLIENT_BASE_URL")
    if env_base_url:
        config["base_url"] = env_base_url
    
    # 读取对话参数环境变量
    env_params = {
        "contextCount": "AI_CONTEXT_COUNT",
        "frequencyPenalty": "AI_FREQUENCY_PENALTY",
        "maxToken": "AI_MAX_TOKEN",
        "presencePenalty": "AI_PRESENCE_PENALTY",
        "prompt": "AI_PROMPT",
        "temperature": "AI_TEMPERATURE",
        "topSort": "AI_TOP_SORT"
    }
    
    for key, env_var in env_params.items():
        env_value = os.getenv(env_var)
        if env_value:
            # 尝试转换为数值类型
            try:
                if key in ["contextCount", "maxToken", "topSort"]:
                    config[key] = int(env_value)
                elif key in ["frequencyPenalty", "presencePenalty", "temperature"]:
                    config[key] = float(env_value)
                else:
                    config[key] = env_value
            except ValueError:
                config[key] = env_value
    
    return config

# 初始化配置
CONFIG = load_config()
