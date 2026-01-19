# 导航模块 - 处理消息导航和跳转功能
import streamlit as st

# 渲染侧边导航栏
def render_navigation_bar():
    """
    渲染侧边导航栏，提供快速跳转到不同消息的功能
    参考Gemini的简洁设计风格
    """
    if "messages" not in st.session_state or not st.session_state.messages:
        return
    
    messages = st.session_state.messages
    if not messages:
        return
    
    # 使用streamlit的sidebar，更可靠
    with st.sidebar:
        st.markdown("### 📋 消息导航")
        
        # 为每条消息创建一个简单的按钮
        for idx, msg in enumerate(messages):
            role = msg.get("role", "unknown")
            role_icon = "👤" if role == "user" else "🤖"
            
            # 创建一个简单的按钮，使用streamlit的内置功能
            if st.button(f"{role_icon} 消息 {idx + 1}", key=f"nav_{idx}", use_container_width=True):
                # 使用streamlit的会话状态来存储要滚动到的消息索引
                st.session_state["scroll_to_message"] = idx
                
                # 使用st.rerun()来重新渲染页面，触发滚动
                st.rerun()
    
    # 检查是否需要滚动到特定消息
    if "scroll_to_message" in st.session_state:
        scroll_index = st.session_state["scroll_to_message"]
        
        # 修复f-string语法错误，转义JavaScript的花括号
        scroll_script = f"""
        <script>
        document.addEventListener('DOMContentLoaded', function() {{
            console.log('滚动到消息索引:', {scroll_index});
            
            // 获取所有聊天消息元素
            const chatMessages = document.querySelectorAll('[data-testid="stChatMessage"]');
            console.log('找到的消息数量:', chatMessages.length);
            
            if (chatMessages.length > {scroll_index}) {{
                const targetMessage = chatMessages[{scroll_index}];
                console.log('目标消息:', targetMessage);
                
                // 滚动到目标消息
                targetMessage.scrollIntoView({{
                    behavior: 'smooth',
                    block: 'center'
                }});
                
                // 高亮显示目标消息
                targetMessage.style.boxShadow = '0 0 20px rgba(66, 133, 244, 0.5)';
                setTimeout(() => {{
                    targetMessage.style.boxShadow = 'none';
                }}, 2000);
            }}
        }});
        </script>
        """
        
        st.markdown(scroll_script, unsafe_allow_html=True)