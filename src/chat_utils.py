# 聊天工具模块 - 存放聊天相关的共享功能
import streamlit as st
import re
from .file_utils import format_file_attachments
from st_copy import copy_button

# 清洗 AI 文本的辅助函数
def clean_ai_text(text):
    """
    清洗 AI 文本：移除 <think> 及其内容，re.DOTALL 让 . 能匹配换行符
    """
    pattern = r"<think>[\s\S]*?</think>"
    # 替换为空字符串
    cleaned_text = re.sub(pattern, "", text, flags=re.DOTALL)
    # 去除首尾多余空格
    return cleaned_text.strip()

# 生成徽章 HTML
def render_badges(tokens=0, time_str="", model_name=""):
    """
    生成底部的元数据徽章 HTML
    
    Args:
        tokens (int): Tokens 使用量
        time_str (str): 时间字符串
        model_name (str): 模型名称
        
    Returns:
        str: 生成的 HTML 字符串
    """
    # 如果 tokens 为 0 或 None，不显示 Token 徽章
    token_html = ""
    if tokens:
        token_html = f"""
        <div style="background-color: rgba(255, 75, 75, 0.15); color: #ff4b4b; border: 0px solid rgba(255, 75, 75, 0.3); padding: 2px 8px; border-radius: 4px; font-size: 12px; white-space: nowrap; display: flex; align-items: center;">
            <span style="margin-right: 4px;">💡</span> {tokens}
        </div>
        """
    
    # 如果时间为空，也不显示时间徽章
    time_html = ""
    if time_str:
         time_html = f"""
        <div style="background-color: rgba(33, 195, 84, 0.15); color: #21c354; border: 0px solid rgba(33, 195, 84, 0.3); padding: 2px 8px; border-radius: 4px; font-size: 12px; white-space: nowrap; display: flex; align-items: center;">
            <span style="margin-right: 4px;">⏰</span> {time_str}
        </div>
        """

    return f"""
    <div style="display: flex; flex-direction: row; align-items: center; gap: 8px; flex-wrap: wrap; margin-top: 4px;">
        {token_html}
        {time_html}
        <!-- 模型 标签 (蓝色风格) -->
        <div style="background-color: rgba(0, 104, 201, 0.15); color: #0068c9; border: 0px solid rgba(0, 104, 201, 0.3); padding: 2px 8px; border-radius: 4px; font-size: 12px; white-space: nowrap; display: flex; align-items: center;">
            <span style="margin-right: 4px;">🤖</span> {model_name}
        </div>
    </div>
    """

# 渲染聊天消息的共享逻辑
def render_chat_message(msg_obj, message_index, model_name="Unknown"):
    """
    渲染聊天消息的核心逻辑
    
    Args:
        msg_obj (dict): 消息对象
        message_index (int): 消息索引，用于生成唯一key
        model_name (str): 模型名称
    """
    role = msg_obj["role"]
    content = msg_obj["content"]
    
    with st.chat_message(role):
        if role == "user":
            # 用户消息处理
            # 使用file_utils模块格式化文件附件
            file_html = format_file_attachments(
                msg_obj.get("files", []),
                msg_obj.get("file_name"),
                msg_obj.get("file_url")
            )

            # 如果有文件附件，使用HTML显示
            if file_html:
                st.markdown(file_html, unsafe_allow_html=True)
                # 添加换行
                st.markdown("\n\n")

            # 直接显示完整消息，使用st.text避免markdown渲染
            st.text(content)
        else:
            # AI消息处理
            from .utils import process_ai_content
            
            # 正常显示内容（可能包含折叠的思考过程）
            main_content, think_content, _ = process_ai_content(content)

            # 如果有思考内容，使用折叠面板显示
            if think_content:
                with st.expander("查看思考过程"):
                    st.markdown(think_content)

            # 显示主要内容 - 不限制高度
            if main_content:
                st.markdown(main_content)
        
        # 操作按钮组
        if role == "assistant":
            # AI消息：显示复制和删除按钮
            # 调整列宽：给 action_col3 更多空间 (0.8)，因为它要放三个标签
            action_col1, action_col2, action_col3 = st.columns([0.1, 0.1, 0.8], vertical_alignment="center")
        else:
            # 用户消息：只显示复制按钮
            action_col1, action_col3 = st.columns([0.1, 0.9], vertical_alignment="center")

        # 1. 复制按钮
        with action_col1:
            # 准备要复制的文本
            if role == "assistant":
                text_to_copy = clean_ai_text(content)
            else:
                text_to_copy = content
            
            copy_button(text_to_copy)
        
        # 2. 删除按钮（仅AI消息显示）
        if role == "assistant":
            with action_col2:
                # 从消息对象中获取必要的删除参数
                cid = msg_obj.get("cid") or msg_obj.get("id")
                sid = msg_obj.get("sid") or msg_obj.get("sessionId") or msg_obj.get("session_id")
                task_id = msg_obj.get("taskId") or msg_obj.get("task_id")
                
                # 检查是否有删除所需的参数
                if cid and sid:
                    # 使用popover实现确认弹窗
                    with st.popover(":wastebasket:", help="删除本组回答"):
                        st.warning("确定要删除本组回答吗？此操作不可恢复。")
                        
                        # 确认删除按钮
                        if st.button("确认删除", key=f"confirm_delete_{message_index}", type="primary", help="确认删除本组回答"):
                            # 调用core.py中的delete_chat_record方法
                            from .core import AIClient
                            if st.session_state.bot:
                                # 使用现有的bot实例
                                success, message = st.session_state.bot.delete_chat_record(cid, sid, task_id)
                                if success:
                                    st.toast(message, icon="✅")
                                    
                                    # 刷新session：重新获取会话记录并更新session_state
                                    bot = st.session_state.bot
                                    session_id = bot.session_id
                                    
                                    # 重新获取会话记录
                                    success_records, data_records = bot.get_chat_records(session_id)
                                    if success_records and data_records.get("records"):
                                        # 清空当前消息
                                        st.session_state.messages = []
                                        st.session_state.useFiles = []
                                        
                                        # 重新加载会话记录
                                        from .sidebar import load_session_to_state
                                        
                                        # 获取当前模型名称
                                        current_model = st.session_state.get("current_session_model", "Unknown")
                                        
                                        # 重新加载会话到状态
                                        load_session_to_state(
                                            session_id,
                                            "",  # 会话名称，这里不需要
                                            current_model,
                                            bot.token
                                        )
                                    
                                    # 重新渲染页面以更新聊天记录
                                    st.rerun()
                                else:
                                    st.toast(f"删除失败: {message}", icon="❌")
                            else:
                                st.toast("请先连接会话！", icon="⚠️")
                        
                        # 取消按钮
                        if st.button("取消", key=f"cancel_delete_{message_index}", help="取消删除操作"):
                            # 关闭popover
                            pass
                else:
                    # 如果缺少参数，显示禁用的删除按钮
                    st.button(":wastebasket:", key=f"delete_{message_index}", disabled=True, help="缺少删除所需的参数")

        # 3. 信息标签组 (Tokens | 时间 | 模型)
        with action_col3:
            # 获取数据
            use_tokens = msg_obj.get("useTokens", msg_obj.get("tokens", 0))
            updated_time = msg_obj.get("updated", msg_obj.get("timestamp", ""))
            
            # 渲染徽章
            badges_html = render_badges(tokens=use_tokens, time_str=updated_time, model_name=model_name)
            st.html(badges_html)
