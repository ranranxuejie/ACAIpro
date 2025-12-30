# 工具函数模块 - 提供各种辅助功能

# 处理AI回复，折叠<think>标签内容
def process_ai_content(content):
    """
    处理AI回复内容，将<think>标签开始后的内容折叠
    
    Args:
        content (str): AI回复的原始内容
        
    Returns:
        tuple: (处理后的主要内容, 思考内容, 是否正在思考状态)
    """
    # 检查是否包含<think>标签
    if '<think>' in content:
        main_content = content
        think_content = ""
        is_thinking = False
        
        # 处理所有完整的<think>...</think>标签
        while '<think>' in main_content and '</think>' in main_content:
            think_start = main_content.find('<think>')
            think_end = main_content.find('</think>')
            
            if think_end > think_start:
                # 提取思考内容
                think_content += main_content[think_start + 7:think_end] + "\n\n"
                # 移除当前的<think>...</think>标签
                main_content = main_content[:think_start] + main_content[think_end + 8:]
            else:
                break
        
        # 检查是否还有未结束的<think>标签
        if '<think>' in main_content:
            think_start = main_content.find('<think>')
            # 提取未结束的思考内容
            think_content += main_content[think_start + 7:]
            # 移除未结束的<think>标签
            main_content = main_content[:think_start]
            is_thinking = True
        
        # 返回处理后的内容、思考内容和思考状态
        return main_content.strip(), think_content.strip(), is_thinking
    else:
        # 没有<think>标签，返回原内容
        return content, None, False

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
