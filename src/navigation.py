# 导航模块 - 处理消息导航和跳转功能
import streamlit as st

# 渲染右侧侧边栏导航
def render_right_sidebar_nav(qa_count):
    """
    渲染右侧固定的导航栏，提供快速跳转到不同消息的功能
    参考Gemini的设计风格
    
    Args:
        qa_count (int): 对话组数量
    """
    if qa_count == 0:
        return
    
    # 输出CSS和HTML，实现右侧固定导航栏
    html_content = """
    <style>
    /* 右侧导航栏容器 */
    .right-sidebar-nav {
        position: fixed !important;
        right: 20px !important;
        top: 50% !important;
        transform: translateY(-50%) !important;
        z-index: 9999 !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        gap: 8px !important;
        background: rgba(255, 255, 255, 0.95) !important;
        border-radius: 20px !important;
        padding: 12px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15) !important;
        backdrop-filter: blur(10px) !important;
    }
    
    /* 导航点样式 */
    .nav-dot {
        width: 16px !important;
        height: 16px !important;
        border-radius: 50% !important;
        background-color: #e0e0e0 !important;
        cursor: pointer !important;
        transition: all 0.3s ease !important;
        position: relative !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        color: #666 !important;
    }
    
    /* 导航点悬停效果 */
    .nav-dot:hover {
        transform: scale(1.3) !important;
        background-color: #ff4b4b !important;
        color: white !important;
        box-shadow: 0 0 10px rgba(255, 75, 75, 0.5) !important;
    }
    
    /* 连接线样式 */
    .nav-line {
        width: 2px !important;
        height: 20px !important;
        background-color: #e0e0e0 !important;
    }
    </style>
    
    <!-- 右侧导航栏HTML -->
    <div class="right-sidebar-nav">
    """
    
    # 生成导航点和连接线
    for i in range(qa_count):
        # 导航点
        html_content += f"""
        <div class="nav-dot" onclick="scrollToMessage({i})" title="跳转到第 {i + 1} 组对话">
            {i + 1}
        </div>
        """
        
        # 添加连接线（除了最后一个点）
        if i < qa_count - 1:
            html_content += "<div class='nav-line'></div>"
    
    # 关闭导航栏容器
    html_content += "</div>"
    
    # 添加JavaScript
    html_content += """
    <script>
    // 滚动到指定消息
    function scrollToMessage(index) {
        console.log('滚动到消息:', index);
        
        // 获取锚点元素
        const anchor = document.getElementById('msg-anchor-' + index);
        if (anchor) {
            console.log('找到锚点:', anchor);
            
            // 平滑滚动到锚点
            anchor.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        } else {
            console.error('未找到锚点:', 'msg-anchor-' + index);
        }
    }
    </script>
    """
    
    # 渲染HTML内容
    st.markdown(html_content, unsafe_allow_html=True)