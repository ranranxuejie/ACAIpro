# 自动加载模块 - 处理模型列表和会话的自动加载
import streamlit as st
from .core import AIClient
from .config import CONFIG

# 自动加载模型列表和会话
def auto_load_data():
    """
    自动加载模型列表和会话
    """
    # 检查并处理初始authorization
    def process_initial_authorization():
        """
        检查并处理初始authorization
        """
        # 检查是否有初始authorization（从配置中）但尚未保存到session_state
        has_initial_authorization = CONFIG["authorization"] and not st.session_state.get("saved_api_authorization")
        
        if has_initial_authorization:
            # 保存初始authorization到session_state
            st.session_state["saved_api_authorization"] = CONFIG["authorization"]
            st.session_state["remember_authorization"] = True
            return True
        return False
    
    # 处理初始authorization
    authorization_processed = process_initial_authorization()
    
    # 自动加载模型列表
    if not st.session_state.models:
        bot_instance = AIClient(st.session_state.get("saved_api_authorization", CONFIG["authorization"]))
        success, data = bot_instance.get_model_list()
        if success:
            st.session_state.models = data.get("models", [])
            # 始终默认使用gemini的preview模型
            st.session_state.selected_model = "gemini-3-pro-preview"
            st.session_state.current_session_model = "gemini-3-pro-preview"

    # 自动加载会话列表并打开最近一次对话
    # 只有在会话列表为空时才加载，避免无限循环
    if not st.session_state.sessions or authorization_processed:  # 当authorization被处理时，强制加载会话列表
        bot_instance = AIClient(st.session_state.get("saved_api_authorization", CONFIG["authorization"]))
        success, data = bot_instance.get_sessions()
        if success:
            # 始终更新会话列表
            st.session_state.sessions = data
            if data:
                st.toast(f"已加载 {len(data)} 个会话", icon="✅")
                
                # 只有在没有bot实例时，才初始化bot和会话
                if not st.session_state.bot:
                    # 根据创建时间排序，取最新的会话
                    recent_session = max(data, key=lambda x: x.get('created', ''))
                    session_id = recent_session.get('id')
                    session_name = recent_session.get('name', '未命名会话')
                    
                    # 设置当前会话ID
                    bot_instance.session_id = session_id
                    st.session_state.bot = bot_instance
                    
                    # 自动选择当前会话的模型
                    session_model = recent_session.get("model", "gemini-3-pro-preview")
                    st.session_state.selected_model = session_model
                    st.session_state.current_session_model = session_model
                    
                    st.session_state.status = f"✅ 已连接到会话: {session_name}"
                    
                    # 只有在消息列表为空时，才加载历史聊天记录
                    if not st.session_state.messages:
                        # 加载该会话的历史聊天记录
                        success, records_data = st.session_state.bot.get_chat_records(session_id)
                        if success and records_data.get("records"):
                            # 将历史记录转换为消息格式
                            for record in reversed(records_data["records"]):
                                user_text = record.get("userText")
                                ai_text = record.get("aiText")
                                
                                if user_text:
                                    st.session_state.messages.append({
                                        "role": "user",
                                        "content": user_text,
                                        "tokens": record.get("promptTokens", 0),
                                        "updated": record.get("created", ""),
                                        "model": record.get("model", "")

                                    })
                                if ai_text:
                                    st.session_state.messages.append({
                                        "role": "assistant",
                                        "content": ai_text,
                                        "tokens": record.get("completionTokens", 0),
                                        "updated": record.get("updated", ""),
                                        "model" : record.get("model", "")
                                    })
            else:
                # 会话列表为空时，初始化bot
                if not st.session_state.bot:
                    st.session_state.bot = bot_instance
        # 移除自动加载时的st.rerun()，避免无限循环
