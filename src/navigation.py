# 导航模块 - 处理消息导航和跳转功能
import streamlit as st
import streamlit.components.v1 as components

def render_right_sidebar_nav(qa_count):
    """
    渲染右侧固定的导航栏，提供快速跳转到不同消息的功能。
    使用 JS 注入父级 DOM 的方式，确保点击事件 100% 触发。

    Args:
        qa_count (int): 对话组数量
    """
    if qa_count == 0:
        return

    # 这里的 JS 逻辑是：
    # 1. 找到父窗口 (Streamlit 主页面) 的 document
    # 2. 清除旧的导航栏 (防止 Streamlit 重新运行时重复添加)
    # 3. 创建新的导航栏 HTML 结构
    # 4. 将其直接 append 到父窗口的 body 中
    # 5. 绑定点击事件，调用父窗口的 scrollIntoView

    js_code = f"""
    <script>
    (function() {{
        // === 1. 获取父窗口对象 (核心) ===
        // Streamlit 组件运行在 iframe 中，我们需要操作 parent
        var parentDoc = window.parent.document;

        // === 2. 清理旧元素 ===
        // 每次 Streamlit 重新渲染时，先删除上一次生成的导航栏
        var oldNav = parentDoc.getElementById('ac-pro-right-nav');
        if (oldNav) {{
            oldNav.remove();
        }}

        var oldStyle = parentDoc.getElementById('ac-pro-nav-style');
        if (oldStyle) {{
            oldStyle.remove();
        }}

        // === 3. 注入 CSS 样式 ===
        var style = parentDoc.createElement('style');
        style.id = 'ac-pro-nav-style';
        style.innerHTML = `
            /* 导航容器 */
            #ac-pro-right-nav {{
                position: fixed;
                right: 20px;
                top: 50%;
                transform: translateY(-50%);
                z-index: 999999; /* 确保在最上层 */
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 0px; /* 线条和点紧密连接 */
                padding: 10px;
            }}

            /* 单个导航项容器 (点+线) */
            .nav-item-container {{
                display: flex;
                flex-direction: column;
                align-items: center;
                cursor: pointer;
                position: relative;
            }}

            /* 导航点 */
            .nav-dot {{
                width: 14px;
                height: 14px;
                border-radius: 50%;
                background-color: #ddd; /* 默认灰色 */
                border: 2px solid #bbb;
                transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 0px; /* 隐藏数字，悬浮显示 */
                z-index: 2;
            }}

            /* 悬停时的点 */
            .nav-item-container:hover .nav-dot {{
                transform: scale(1.6);
                background-color: #FF4B4B; /* Streamlit 红 */
                border-color: #FF4B4B;
                box-shadow: 0 0 8px rgba(255, 75, 75, 0.6);
            }}

            /* 悬停时的提示气泡 (Tooltip) */
            .nav-item-container::after {{
                content: attr(data-tooltip);
                position: absolute;
                right: 30px; /* 在点的左边显示 */
                top: 50%;
                transform: translateY(-50%) translateX(10px);
                background: rgba(0,0,0,0.7);
                color: white;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 12px;
                white-space: nowrap;
                opacity: 0;
                pointer-events: none;
                transition: all 0.2s ease;
            }}

            .nav-item-container:hover::after {{
                opacity: 1;
                transform: translateY(-50%) translateX(0);
            }}

            /* 连接线 */
            .nav-line {{
                width: 2px;
                height: 25px; /* 点之间的间距 */
                background-color: #e0e0e0;
                transition: background-color 0.3s;
                z-index: 1;
            }}

            .nav-item-container:hover + .nav-item-container .nav-line {{
                /* background-color: #ffcccc; 可选：连线变色 */
            }}
        `;
        parentDoc.head.appendChild(style);

        // === 4. 创建 DOM 结构 ===
        var navContainer = parentDoc.createElement('div');
        navContainer.id = 'ac-pro-right-nav';

        var count = {qa_count};

        for (let i = 0; i < count; i++) {{
            // 容器
            let item = parentDoc.createElement('div');
            item.className = 'nav-item-container';
            item.setAttribute('data-tooltip', '跳转到对话 ' + (i + 1));

            // 点击事件
            item.onclick = function() {{
                // 在父窗口查找锚点
                let anchor = parentDoc.getElementById('msg-anchor-' + i);
                if (anchor) {{
                    // 【关键修改】使用 block: 'start' 让锚点对齐到可视区域顶部
                    anchor.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
                }} else {{
                    console.log('Anchor not found: msg-anchor-' + i);
                }}
            }};

            // 点
            let dot = parentDoc.createElement('div');
            dot.className = 'nav-dot';
            item.appendChild(dot);

            // 线 (除了最后一个)
            if (i < count - 1) {{
                let line = parentDoc.createElement('div');
                line.className = 'nav-line';
                item.appendChild(line);
            }}

            navContainer.appendChild(item);
        }}

        // === 5. 插入到父窗口 Body ===
        parentDoc.body.appendChild(navContainer);

    }})();
    </script>
    """

    # 使用 components.html 执行 JS，高度设为0使其不可见，只负责运行逻辑
    components.html(js_code, height=0, width=0)