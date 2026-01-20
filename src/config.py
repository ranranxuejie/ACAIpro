# 配置模块 - 处理配置读取和管理
import os

# 直接使用指定的token和base_url
DEFAULT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjEwMTI4LCJzaWduIjoiNGEwMTE3MmI3MjU3NzIxNDk3ODZiMTQ3N2Q2MmQ4ZjQiLCJyb2xlIjoidXNlciIsImV4cCI6MTc2OTQ3OTI2MCwibmJmIjoxNzY2ODAwODYwLCJpYXQiOjE3NjY4MDA4NjB9.bvYZUkuc_RBkJdyFEYQqRA7mw1Zlv3LeNnMz20ZJZCk"
BASE_URL = "https://achuanai.vip/api"

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
    
    return config

# 初始化配置
CONFIG = load_config()

# 兼容旧接口，返回空字符串

def load_token_from_secrets():
    """
    兼容旧接口，不再从Streamlit Secrets读取API Token
    """
    return ""
