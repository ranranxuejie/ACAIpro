# 聊天区域模块 - 处理聊天界面组件
import streamlit as st
from .utils import process_ai_content
from .file_utils import format_file_attachments
from .styles import apply_global_styles
from .chat_utils import render_chat_message
from .navigation import render_right_sidebar_nav

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
            
            # 核心修改：将扁平的消息列表视为"对话组"
            # 每遇到一个User消息，就算开启了一组新的对话
            qa_count = 0  # 记录总共有多少组对话
            
            # 遍历存储的消息对象
            for message_index, msg_obj in enumerate(st.session_state.messages):
                role = msg_obj["role"]
                
                # 如果是用户消息，这代表一组新对话的开始
                if role == "user":
                    qa_count += 1
                    current_pair_index = qa_count - 1
                    
                    # 【埋点】插入看不见的锚点DIV，偏移一点距离以免被顶部遮挡
                    st.markdown(f"""
                    <div id='msg-anchor-{current_pair_index}' style='position:relative; top: -60px; visibility: hidden;'></div>
                    """, unsafe_allow_html=True)
                
                # 使用共享的渲染函数渲染聊天消息
                render_chat_message(msg_obj, message_index, current_model)
            
            # 渲染完成后，生成右侧导航栏
            render_right_sidebar_nav(qa_count)
        else:
            # 没有消息时，生成空导航栏
            render_right_sidebar_nav(0)
