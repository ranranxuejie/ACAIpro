# UI组件模块 - 整合所有拆分后的UI组件
import streamlit as st

# 使用相对导入
from .session import init_session_state
from .sidebar import render_sidebar
from .chat_area import render_chat_area
from .input_area import render_input_area
from .auto_load import auto_load_data

# 主UI函数
def render_ui():
    """
    渲染完整的UI界面
    """
    # 初始化会话状态
    init_session_state()
    
    # 自动加载模型列表和会话
    auto_load_data()
    
    # 渲染侧边栏
    render_sidebar()
    
    # 渲染聊天区域
    render_chat_area()
    
    # 渲染输入区域
    render_input_area()

# 如果直接运行该文件，执行主UI函数
if __name__ == "__main__":
    render_ui()
