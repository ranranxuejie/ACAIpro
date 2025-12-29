# 工具函数模块 - 提供各种辅助功能

# 处理AI回复，折叠<think>标签内容
def process_ai_content(content):
    """
    处理AI回复内容，将<think>...</think>标签内的内容折叠
    
    Args:
        content (str): AI回复的原始内容
        
    Returns:
        tuple: (处理后的主要内容, 思考内容)
    """
    import re
    
    # 使用正则表达式匹配<think>标签内容
    pattern = r'<think>(.*?)</think>'
    matches = re.findall(pattern, content, re.DOTALL)
    
    if matches:
        # 提取<think>标签内容
        think_content = matches[0]
        # 提取主要内容（去除<think>标签）
        main_content = re.sub(pattern, '', content, flags=re.DOTALL)
        
        # 返回处理后的内容和思考内容
        return main_content.strip(), think_content.strip()
    else:
        # 没有<think>标签，返回原内容
        return content, None

# 确保当前会话模型正确设置
def ensure_current_model():
    """
    确保当前会话使用正确的模型
    """
    import streamlit as st
    
    if st.session_state.bot and st.session_state.bot.session_id and st.session_state.sessions:
        # 查找当前会话信息
        for session in st.session_state.sessions:
            if session.get("id") == st.session_state.bot.session_id:
                # 更新当前会话模型
                session_model = session.get("model", st.session_state.selected_model)
                st.session_state.current_session_model = session_model
                st.session_state.selected_model = session_model
                break
