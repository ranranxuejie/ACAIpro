# Session管理模块 - 处理Streamlit Session State
import streamlit as st
from .config import CONFIG

# 初始化Session State
def init_session_state():
    """
    初始化所有Session State变量
    """
    if "messages" not in st.session_state:
        st.session_state.messages = []  # 存储聊天记录
    if "bot" not in st.session_state:
        st.session_state.bot = None  # 存储机器人实例
    if "status" not in st.session_state:
        st.session_state.status = "未连接"
    if "sessions" not in st.session_state:
        st.session_state.sessions = []  # 存储会话列表
    if "models" not in st.session_state:
        st.session_state.models = []  # 存储模型列表
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = "gemini-3-pro-preview"  # 默认模型
    if "current_session_model" not in st.session_state:
        st.session_state.current_session_model = "gemini-3-pro-preview"  # 当前会话使用的模型
    if "saved_api_authorization" not in st.session_state:
        st.session_state.saved_api_authorization = CONFIG["authorization"]
    if "remember_authorization" not in st.session_state:
        # 如果从CONFIG加载了authorization，默认记住authorization
        st.session_state.remember_authorization = bool(CONFIG["authorization"])
    if "useFiles" not in st.session_state:
        st.session_state.useFiles = []  # 存储对话中涉及的所有文件
