# 导航模块 - 处理消息导航和跳转功能
import streamlit as st

# 渲染侧边导航栏
def render_navigation_bar():
    """
    渲染侧边导航栏，提供快速跳转到不同消息的功能
    """
    if "messages" not in st.session_state or not st.session_state.messages:
        return
    
    messages = st.session_state.messages
    if not messages:
        return
    
    # 创建导航栏容器
    with st.container():
        st.markdown("### 📋 消息导航")
        
        # 为每条消息创建一个跳转按钮
        for idx, msg in enumerate(messages):
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            
            # 提取消息摘要（前30个字符）
            summary = content[:30] + "..." if len(content) > 30 else content
            role_icon = "👤" if role == "user" else "🤖"
            
            # 创建跳转按钮
            button_label = f"{role_icon} 消息 {idx + 1}"
            if st.button(button_label, key=f"nav_{idx}", help=summary, use_container_width=True):
                # 使用JavaScript滚动到对应的消息
                scroll_to_message(idx)

# 滚动到指定消息
def scroll_to_message(message_index):
    """
    滚动到指定消息
    
    Args:
        message_index (int): 消息索引
    """
    # 使用JavaScript滚动到对应的消息元素
    scroll_script = f"""
    <script>
        function scrollToMessage() {{
            const messages = document.querySelectorAll('[data-testid="stChatMessage"]');
            if (messages[{message_index}]) {{
                messages[{message_index}].scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                // 高亮显示该消息
                messages[{message_index}].style.border = '2px solid #FF4B4B';
                messages[{message_index}].style.borderRadius = '8px';
                setTimeout(() => {{
                    messages[{message_index}].style.border = 'none';
                    messages[{message_index}].style.borderRadius = '0';
                }}, 2000);
            }}
        }}
        scrollToMessage();
    </script>
    """
    st.markdown(scroll_script, unsafe_allow_html=True)