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
    
    # 直接输出HTML，不使用st.container，确保固定定位正常工作
    st.markdown("""
    <style>
    /* 导航栏容器样式 - 固定在右侧 */
    .navigation-dot-container {
        position: fixed !important;
        right: 15px !important;
        top: 50% !important;
        transform: translateY(-50%) !important;
        z-index: 9999 !important;
        display: flex !important;
        flex-direction: column !important;
        gap: 10px !important;
        background: rgba(255, 255, 255, 0.95) !important;
        border-radius: 20px !important;
        padding: 12px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15) !important;
        backdrop-filter: blur(10px) !important;
    }
    
    /* 导航点样式 */
    .navigation-dot {
        width: 36px !important;
        height: 36px !important;
        border-radius: 50% !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        cursor: pointer !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2) !important;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3) !important;
        user-select: none !important;
    }
    
    /* 悬停效果 */
    .navigation-dot:hover {
        transform: translateX(-8px) scale(1.1) !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4) !important;
    }
    
    /* 点击效果 */
    .navigation-dot:active {
        transform: translateX(-8px) scale(0.95) !important;
    }
    </style>
    
    <!-- 导航栏容器 -->
    <div class="navigation-dot-container">
    """, unsafe_allow_html=True)
    
    # 为每条消息创建一个简洁的导航点
    for idx, msg in enumerate(messages):
        # 只显示序号，不显示消息内容和图标
        st.markdown(f"""
        <div class="navigation-dot" onclick="javascript:scrollToMessage({idx});">
            {idx + 1}
        </div>
        """, unsafe_allow_html=True)
    
    # 关闭导航栏容器
    st.markdown("""
    </div>
    
    <!-- 滚动到消息的JavaScript函数 -->
    <script>
    // 全局定义滚动函数，确保点击时可用
    window.scrollToMessage = function(index) {
        console.log('点击了导航点 ' + index);
        
        // 获取所有聊天消息元素
        const messages = document.querySelectorAll('[data-testid="stChatMessage"]');
        console.log('找到 ' + messages.length + ' 条消息');
        
        if (messages.length > index && messages[index]) {
            console.log('定位到消息 ' + index);
            
            // 滚动到消息，使用更平滑的动画
            messages[index].scrollIntoView({
                behavior: 'smooth',
                block: 'center',
                inline: 'nearest'
            });
            
            // 高亮显示该消息
            messages[index].style.boxShadow = '0 0 0 2px #667eea, 0 0 20px rgba(102, 126, 234, 0.3)';
            messages[index].style.borderRadius = '8px';
            messages[index].style.transition = 'all 0.3s ease';
            
            // 1.5秒后恢复原状
            setTimeout(() => {
                messages[index].style.boxShadow = 'none';
                messages[index].style.borderRadius = '';
            }, 1500);
        }
    };
    </script>
    """, unsafe_allow_html=True)