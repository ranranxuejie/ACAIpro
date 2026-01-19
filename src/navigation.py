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
    
    # 创建简洁的导航栏容器
    with st.container():
        # 添加样式
        st.markdown("""
        <style>
        .navigation-container {
            position: fixed;
            right: 20px;
            top: 50%;
            transform: translateY(-50%);
            z-index: 999;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            padding: 8px;
            max-height: 60vh;
            overflow-y: auto;
            width: 200px;
        }
        
        .navigation-item {
            display: flex;
            align-items: center;
            padding: 8px 12px;
            cursor: pointer;
            border-radius: 6px;
            transition: all 0.2s ease;
            margin-bottom: 4px;
            font-size: 13px;
            color: #333;
        }
        
        .navigation-item:hover {
            background-color: rgba(0, 0, 0, 0.05);
        }
        
        .navigation-icon {
            width: 24px;
            height: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 8px;
            font-size: 16px;
        }
        
        .navigation-text {
            flex: 1;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        
        .navigation-count {
            background-color: #666;
            color: white;
            border-radius: 10px;
            padding: 2px 8px;
            font-size: 11px;
            font-weight: 500;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # 创建导航容器
        st.markdown('<div class="navigation-container" id="navigation-bar">', unsafe_allow_html=True)
        
        # 为每条消息创建一个导航项
        for idx, msg in enumerate(messages):
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            
            # 根据角色选择图标
            if role == "user":
                icon = "👤"
                icon_bg = "#e3f2fd"
            else:
                icon = "🤖"
                icon_bg = "#4285f4"
            
            # 提取消息摘要（前20个字符）
            summary = content[:20] + "..." if len(content) > 20 else content
            
            # 创建导航项HTML
            nav_item = f"""
            <div class="navigation-item" onclick="scrollToMessage({idx})">
                <div class="navigation-icon" style="background-color: {icon_bg}; border-radius: 50%;">
                    {icon}
                </div>
                <div class="navigation-text">
                    {summary}
                </div>
                <div class="navigation-count">
                    {idx + 1}
                </div>
            </div>
            """
            st.markdown(nav_item, unsafe_allow_html=True)
        
        # 关闭导航容器
        st.markdown('</div>', unsafe_allow_html=True)

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
        function scrollToMessage(index) {{
            const messages = document.querySelectorAll('[data-testid="stChatMessage"]');
            if (messages[index]) {{
                messages[index].scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                // 高亮显示该消息
                messages[index].style.boxShadow = '0 0 0 20px rgba(66, 133, 244, 0.5)';
                messages[index].style.transform = 'scale(1.02)';
                setTimeout(() => {{
                    messages[index].style.boxShadow = 'none';
                    messages[index].style.transform = 'scale(1)';
                }}, 1500);
            }}
        }}
    </script>
    """
    st.markdown(scroll_script, unsafe_allow_html=True)