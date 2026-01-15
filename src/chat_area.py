# 聊天区域模块 - 处理聊天界面组件
import streamlit as st
from .utils import process_ai_content
from .file_utils import format_file_attachments
from .styles import apply_global_styles
from .chat_utils import render_chat_message

# 渲染聊天区域
def render_chat_area():
    """
    渲染聊天区域组件
    """
    # 应用共享样式
    apply_global_styles()

    # --- 2. 渲染聊天记录 ---
    chat_container = st.container()
    with chat_container:
        # 检查 session_state 是否有消息
        if "messages" in st.session_state and st.session_state.messages:
            # 获取当前模型名称
            current_model = st.session_state.get("current_session_model", "Unknown")
            
            # 遍历存储的消息对象
            for message_index, msg_obj in enumerate(st.session_state.messages):
                # 使用共享的渲染函数渲染聊天消息
                render_chat_message(msg_obj, message_index, current_model)
