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
            
            # 直接使用HTML按钮，避免streamlit按钮的延迟问题
            button_html = f"""
            <button 
                onclick="scrollToMessage({idx})" 
                style="
                    width: 100%;
                    padding: 10px;
                    margin-bottom: 8px;
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                    background-color: white;
                    cursor: pointer;
                    font-size: 14px;
                    font-weight: 500;
                    transition: all 0.2s ease;
                "
                onmouseover="this.style.backgroundColor='#f0f0f0'"
                onmouseout="this.style.backgroundColor='white'"
            >
                {role_icon} 消息 {idx + 1}
            </button>
            """
            
            st.markdown(button_html, unsafe_allow_html=True)
    
    # 输出全局滚动函数，确保在页面加载时可用
    st.markdown("""
    <script>
    // 全局滚动函数
    function scrollToMessage(index) {
        console.log('点击了导航按钮，索引:', index);
        
        // 立即执行滚动，不等待
        setTimeout(function() {
            console.log('执行滚动，索引:', index);
            
            // 获取所有聊天消息元素
            const chatMessages = document.querySelectorAll('[data-testid="stChatMessage"]');
            console.log('找到的消息数量:', chatMessages.length);
            
            if (chatMessages.length > index) {
                const targetMessage = chatMessages[index];
                console.log('目标消息:', targetMessage);
                
                // 使用最基本的滚动方法
                targetMessage.scrollIntoView(true);
                
                // 高亮显示
                targetMessage.style.backgroundColor = '#f0f8ff';
                targetMessage.style.border = '2px solid #4a90e2';
                targetMessage.style.borderRadius = '8px';
                
                setTimeout(function() {
                    targetMessage.style.backgroundColor = '';
                    targetMessage.style.border = '';
                    targetMessage.style.borderRadius = '';
                }, 2000);
            }
        }, 100);
    }
    </script>
    """, unsafe_allow_html=True)