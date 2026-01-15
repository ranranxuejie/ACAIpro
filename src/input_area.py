# 输入区域模块 - 处理聊天输入和用户输入处理
import streamlit as st
import re
from datetime import datetime
from .core import AIClient
from .utils import process_ai_content
from .file_utils import format_file_attachments
from .styles import apply_global_styles
from .chat_utils import clean_ai_text, render_badges
from st_copy import copy_button

# 渲染输入区域
def render_input_area():
    """
    渲染输入区域组件
    """
    
    chat_input = st.chat_input(
        placeholder="询问任何问题...",
        key="chat_input",
        accept_file=True,
        max_chars=None,
        accept_audio=True,
    )

    if chat_input:
        prompt = chat_input.get("text", "")
        uploaded_files = chat_input.get("files", [])
        uploaded_file = uploaded_files[0] if uploaded_files else None
        
        if uploaded_file:
            st.toast(f"已上传文件: {uploaded_file.name}", icon="✅")
        
        handle_user_input(prompt, uploaded_file)
# 处理用户输入
def handle_user_input(prompt, uploaded_file):
    """
    处理用户输入
    """
    apply_global_styles()
    
    if not st.session_state.bot:
        st.error("请先连接会话！")
        return

    # 获取当前模型名称
    current_model = st.session_state.get("current_session_model", "Unknown")
    # 临时本地时间（在API返回前显示）
    temp_time = datetime.now().strftime("%H:%M:%S")

    # --- 用户消息处理 ---
    file_name_record = uploaded_file.name if uploaded_file else None

    with st.chat_message("user"):
        # 文件显示逻辑
        file_html = format_file_attachments([], file_name_record, f"{file_name_record}" if file_name_record else "")
        if file_html:
            st.markdown(file_html, unsafe_allow_html=True)
            st.markdown("\n\n")
        
        st.text(prompt)
        
        # 操作按钮和信息标签
        action_col1, action_col2 = st.columns([0.08, 0.92], vertical_alignment="center")
        
        with action_col1:
            copy_button(prompt)
        
        with action_col2:
            # 1. 创建用户徽章的占位符
            user_badges_placeholder = st.empty()
            # 2. 初始渲染（使用本地时间，Tokens=0）
            user_badges_placeholder.html(render_badges(tokens=0, time_str=temp_time, model_name=current_model))

    # --- AI 消息处理 (流式) ---
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        # 3. 创建 AI 徽章的占位符
        ai_badges_placeholder = st.empty()
        
        # 迭代流式响应
        try:
            for chunk in st.session_state.bot.chat_stream(prompt, uploaded_file):
                full_response += chunk
                main_content, think_content, is_thinking = process_ai_content(full_response)
                
                response_placeholder.empty()
                with response_placeholder.container():
                    if think_content or is_thinking:
                        status_label = "🤔 思考中..." if is_thinking else "💡 思考过程"
                        with st.expander(status_label, expanded=is_thinking):
                            st.markdown(f"{think_content}{'...' if is_thinking else ''}")
                    if main_content:
                        st.markdown(main_content)
            
            # --- 流式结束后的数据更新逻辑 ---
            
            # 1. 获取 Core 中保存的完整元数据
            metadata = getattr(st.session_state.bot, 'last_chat_metadata', {})
            
            # 2. 提取 Tokens
            final_tokens = metadata.get("completionTokens", 0)
            
            # 3. 提取并格式化时间 (使用 'updated' 字段，格式如 "2026-01-13 17:19:50")
            api_time_str = metadata.get("updated", "")
            final_time = temp_time # 默认回退
            if api_time_str and " " in api_time_str:
                try:
                    # 截取 HH:MM:SS 部分
                    final_time = api_time_str.split(" ")[1]
                except:
                    pass
            
            # 4. 更新 AI 的操作栏和徽章
            # 显示复制按钮
            action_col1, action_col2 = st.columns([0.08, 0.92], vertical_alignment="center")
            with action_col1:
                text_to_copy = clean_ai_text(full_response)
                copy_button(text_to_copy)
            
            with action_col2:
                # 渲染最终的 AI 徽章（包含真实Tokens和API时间）
                # 注意：这里我们覆盖之前的占位符，其实可以直接在这里显示，
                # 但为了布局一致，还是把 badges 放在 col2 里，
                # 上面定义的 ai_badges_placeholder 其实可以用作加载中的占位，或者直接不使用占位符，在最后渲染。
                # 考虑到 columns 的作用域，这里直接在 col2 渲染是最好的。
                st.html(render_badges(tokens=final_tokens, time_str=final_time, model_name=current_model))

            # 5. 回填更新 用户 的徽章 (关键步骤)
            # 使用真实的时间戳更新用户消息的徽章
            user_badges_placeholder.html(render_badges(tokens=0, time_str=final_time, model_name=current_model))

        except Exception as e:
            st.error(f"生成回复时出错: {str(e)}")
            final_tokens = 0
            final_time = temp_time

    # --- 保存历史记录 ---
    
    # 从 bot 对象获取元数据和会话信息
    bot = st.session_state.bot
    last_metadata = getattr(bot, 'last_chat_metadata', {})
    session_id = getattr(bot, 'session_id', '')
    
    # 保存用户消息 (包含文件信息)
    user_message = {
        "role": "user",
        "content": prompt,
        "file_name": file_name_record,
        "tokens": 0,
        "files": [],
        "timestamp": final_time, # 保存时间
        "cid": last_metadata.get("id", ""),  # 保存删除所需的参数
        "sid": session_id,
        "taskId": last_metadata.get("taskId", "")
    }
    
    if file_name_record:
        file_info = {"name": file_name_record, "url": ""}
        user_message["files"].append(file_info)
        if "useFiles" not in st.session_state:
            st.session_state.useFiles = []
        file_exists = any(file.get("name") == file_name_record for file in st.session_state.useFiles)
        if not file_exists:
            st.session_state.useFiles.append(file_info)
    
    st.session_state.messages.append(user_message)

    # 保存 AI 消息 (包含真实的 tokens)
    st.session_state.messages.append({
        "role": "assistant", 
        "content": full_response,
        "tokens": final_tokens,
        "useTokens": final_tokens,
        "timestamp": final_time, # 保存时间
        "cid": last_metadata.get("id", ""),  # 保存删除所需的参数
        "sid": session_id,
        "taskId": last_metadata.get("taskId", "")
    })
    
    # 自动滚动脚本
    st.markdown("""
    <script>
        function scrollToBottom() {
            const scrollHeight = document.documentElement.scrollHeight || document.body.scrollHeight;
            window.scrollTo({top: scrollHeight, behavior: "smooth"});
        }
        scrollToBottom();
        setTimeout(scrollToBottom, 100);
        setTimeout(scrollToBottom, 300);
    </script>
    """, unsafe_allow_html=True)