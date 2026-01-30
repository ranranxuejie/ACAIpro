import streamlit as st
import re
from datetime import datetime
from .core import AIClient
from .utils import process_ai_content
from .file_utils import format_file_attachments
from .styles import apply_global_styles
from .chat_utils import clean_ai_text, render_badges
from st_copy import copy_button
# --- 新增引用 ---
from .navigation import render_right_sidebar_nav 


# 渲染输入区域
def render_input_area():
    """
    渲染输入区域组件
    """
    # 恢复为原来的实现，不使用Streamlit Extras
    chat_input = st.chat_input(
        placeholder="询问任何问题...",
        key="chat_input",
        accept_file="multiple",
        max_chars=None,
        accept_audio=True,
    )

    if chat_input:
        prompt = chat_input.get("text", "")
        uploaded_files = chat_input.get("files", [])
        
        if uploaded_files:
            file_names = ", ".join([f.name for f in uploaded_files])
            st.toast(f"已上传文件: {file_names}", icon="✅")
        
        handle_user_input(prompt, uploaded_files)
        
        # 显示成功动画
        from .styles import show_success_animation
        show_success_animation()

# 处理用户输入
def handle_user_input(prompt, uploaded_files):
    """
    处理用户输入
    """
    apply_global_styles()

    if not st.session_state.bot:
        st.error("请先连接会话！")
        return

    # 获取当前模型名称
    current_model = st.session_state.get("current_session_model", "Unknown")
    temp_time = datetime.now().strftime("%H:%M:%S")

    # --- 1. 计算新的 QA 索引 (用于锚点和导航) ---
    # 统计历史消息中 user 的数量
    existing_user_msgs = [m for m in st.session_state.messages if m["role"] == "user"]
    current_pair_index = len(existing_user_msgs) # 如果已有0个，当前就是第0个；已有5个，当前就是第5个

    # --- 用户消息处理 ---
    file_names = [f.name for f in uploaded_files] if uploaded_files else []
    file_name_record = file_names[0] if file_names else None

    # 【关键修改 1】在此处手动注入锚点，否则导航栏点击后不知道跳到哪里
    st.markdown(f"""
    <div id='msg-anchor-{current_pair_index}' style='position:relative; top: -80px; visibility: hidden;'></div>
    """, unsafe_allow_html=True)

    with st.chat_message("user"):
        # 文件显示逻辑
        file_html = format_file_attachments([], file_name_record, f"{file_name_record}" if file_name_record else "")
        if file_html:
            st.markdown(file_html, unsafe_allow_html=True)
            st.markdown("\n\n")

        st.text(prompt)

        buttons_col, badges_col = st.columns([0.1, 0.9], vertical_alignment="center")
        with buttons_col:
            copy_button(prompt)
        with badges_col:
            user_badges_placeholder = st.empty()
            user_badges_placeholder.html(render_badges(tokens=0, time_str=temp_time, model_name=current_model))

    # 【关键修改 2】强制更新右侧导航栏
    # 在用户发完消息、AI 回复之前，立即更新导航栏为 (历史数量 + 1)
    # 这样用户就能立刻看到新的节点出现
    render_right_sidebar_nav(current_pair_index + 1)

    # --- AI 消息处理 (流式) ---
    with st.chat_message("assistant"):
        # ... 以下代码保持原样 ...
        response_placeholder = st.empty()
        full_response = ""

        
        # 3. 创建 AI 徽章的占位符
        ai_badges_placeholder = st.empty()
        
        # 迭代流式响应
        try:
            for chunk in st.session_state.bot.chat_stream(prompt, uploaded_files):
                full_response += chunk
                main_content, think_content, is_thinking = process_ai_content(full_response)
                
                response_placeholder.empty()
                with response_placeholder.container():
                    if think_content or is_thinking:
                        status_label = "🤔 Thinking..." if is_thinking else "💡 思考过程"
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
            
            # 4. 更新 AI 的操作栏和徽章 - 将操作按钮放在一个横向栏目中
            # 显示复制、删除按钮和评分
            buttons_col, badges_col = st.columns([0.2, 0.8], vertical_alignment="center")
            
            with buttons_col:
                # 在按钮栏目中创建两个子列，横向排列复制和删除按钮
                copy_col, delete_col, reserve_col = st.columns([1, 1, 1], gap="small", vertical_alignment="center")
                
                with copy_col:
                    text_to_copy = clean_ai_text(full_response)
                    copy_button(text_to_copy)
                
                with delete_col:
                    # 占位符，用于后续添加删除按钮
                    pass
                
                with reserve_col:
                    # 占位符，用于后续添加评分功能
                    pass
            
            with badges_col:
                # 渲染最终的 AI 徽章（包含真实Tokens和API时间）
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