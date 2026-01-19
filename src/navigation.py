import streamlit as st

def render_right_sidebar_nav(message_pairs):
    """
    渲染右侧悬浮导航栏 (点-线 样式)

    Args:
        message_pairs (int): 对话组的数量 (用户+AI算一组)
    """
    if message_pairs <= 0:
        return

    # 生成每个点的 HTML
    # 我们假设每组对话对应一个锚点 id 为 'msg-anchor-0', 'msg-anchor-1'...
    steps_html = ""
    for i in range(message_pairs):
        steps_html += f"""
        <div class="nav-step" onclick="scrollToMessage({i})" title="跳转到第 {i+1} 组对话">
            <div class="nav-dot"></div>
            {'<div class="nav-line"></div>' if i < message_pairs - 1 else ''}
        </div>
        """

    # 注入完整的 HTML/CSS/JS
    st.markdown(f"""
    <style>
    /* 1. 悬浮容器样式 */
    #right-nav-container {{
        position: fixed;
        right: 20px;
        top: 50%;
        transform: translateY(-50%); /* 垂直居中 */
        z-index: 9999;
        display: flex;
        flex-direction: column;
        align-items: center;
        background: rgba(255, 255, 255, 0.8); /* 浅色背景 */
        backdrop-filter: blur(5px);
        padding: 15px 10px;
        border-radius: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        max-height: 80vh;
        overflow-y: auto;
        /* 隐藏滚动条但保留功能 */
        scrollbar-width: none; 
    }}

    /* 深色模式适配 (可选，利用 Streamlit 的 data-theme 属性大概判断，或者直接用半透明) */
    @media (prefers-color-scheme: dark) {{
        #right-nav-container {{
            background: rgba(40, 40, 40, 0.8);
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        }}
    }}

    /* 2. 单个步骤容器 */
    .nav-step {{
        display: flex;
        flex-direction: column;
        align-items: center;
        cursor: pointer;
        position: relative;
        transition: transform 0.2s;
    }}

    .nav-step:hover {{
        transform: scale(1.2);
    }}

    /* 3. 点的样式 */
    .nav-dot {{
        width: 12px;
        height: 12px;
        background-color: #ddd;
        border: 2px solid #aaa;
        border-radius: 50%;
        transition: all 0.3s;
        z-index: 2; /* 保证点在线的上面 */
    }}

    .nav-step:hover .nav-dot {{
        background-color: #FF4B4B; /* Streamlit 主题红 */
        border-color: #FF4B4B;
    }}

    /* 4. 线的样式 */
    .nav-line {{
        width: 2px;
        height: 25px; /* 点之间的距离 */
        background-color: #eee;
        margin: 2px 0;
    }}

    @media (prefers-color-scheme: dark) {{
        .nav-dot {{ background-color: #555; border-color: #777; }}
        .nav-line {{ background-color: #444; }}
    }}

    </style>

    <div id="right-nav-container">
        {steps_html}
    </div>

    <script>
    function scrollToMessage(index) {{
        // 寻找对应的锚点 ID
        const element = document.getElementById('msg-anchor-' + index);
        if (element) {{
            // 平滑滚动，block: 'start' 让元素滚到视口顶部附近
            element.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
        }} else {{
            console.log('Anchor not found: msg-anchor-' + index);
        }}
    }}
    </script>
    """, unsafe_allow_html=True)