# AI 助手 Pro 主程序
import streamlit as st
from src import (
    init_session_state,
    render_sidebar,
    render_chat_area,
    render_input_area,
    auto_load_data,
    ensure_current_model
)

# 1. 页面基础设置
st.set_page_config(
    page_title="Secret", 
    page_icon="🔞", 
    layout="wide",
    initial_sidebar_state="auto"
)

# 2. 初始化会话状态
init_session_state()

# 3. 确保当前会话模型正确设置
ensure_current_model()

# 4. 自动加载模型列表和会话
auto_load_data()

# 5. 渲染侧边栏
render_sidebar()

# 6. 渲染聊天区域
render_chat_area()

# 7. 渲染输入区域
render_input_area()