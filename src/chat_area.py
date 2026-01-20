# 聊天区域模块 - 处理聊天界面组件
import streamlit as st
import streamlit.components.v1 as components
from .core import AIClient
from .styles import apply_global_styles
from .chat_utils import render_chat_message
from .navigation import render_right_sidebar_nav
from .config import CONFIG

# --- 1. 后端逻辑：仅处理“新建对话” ---

def handle_header_actions():
    """
    检查 URL 参数，仅处理新建对话
    """
    try:
        qp = st.query_params
        action = qp.get("action")

        if not action:
            return

        # 仅处理新建对话
        if action == "new_chat":
            qp.clear()

            # 获取 Authorization
            user_authorization = st.session_state.get("saved_api_authorization", CONFIG.get("authorization"))
            if not user_authorization:
                st.error("未检测到 API Authorization")
                return

            # 获取当前选中的模型
            model = st.session_state.get("selected_model", "gemini-3-pro-preview")

            bot = AIClient(user_authorization)
            success, msg = bot.create_session(model=model)

            if success:
                # 1. 刷新会话列表
                ok, sessions_data = bot.get_sessions()
                if ok:
                    st.session_state.sessions = sessions_data

                # 2. 加载新会话
                from .sidebar import load_session_to_state
                load_session_to_state(msg, "New Chat", model, user_authorization)
            else:
                st.toast(f"新建失败: {msg}", icon="❌")

            st.rerun()

    except Exception as e:
        print(f"Header Action Error: {e}")
        st.query_params.clear()
        pass

# --- 2. 前端渲染：纯展示 Header ---

def render_fixed_header():
    """
    JS 注入 Header。
    简化版：只显示标题和新建按钮，无编辑功能。
    """
    session_name = ""

    if st.session_state.get("bot") and st.session_state.bot.session_id:
        current_id = str(st.session_state.bot.session_id)
        sessions = st.session_state.get("sessions", [])
        for s in sessions:
            if str(s.get("id")) == current_id:
                session_name = s.get("name", "")
                break

    if not session_name:
        session_name = "New Chat"

    # 防转义处理
    safe_session_name = session_name.replace('"', '&quot;')

    # SVG 图标
    PLUS_SVG = """<svg viewBox="0 0 24 24" width="18" height="18" stroke="currentColor" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>"""

    js = f"""
    <script>
    (function() {{
        var parentDoc = window.parent.document;

        // --- DOM 注入逻辑 ---
        var oldHeader = parentDoc.getElementById('ac-fixed-header');
        if (oldHeader) oldHeader.remove();

        var header = parentDoc.createElement('div');
        header.id = 'ac-fixed-header';

        // 简化的 HTML：只有 Title 和 New Chat 按钮
        header.innerHTML = `
            <div class="header-pill">
                <div class="title-container">
                    <span class="header-title" title="{safe_session_name}">{safe_session_name}</span>
                </div>

                <div class="header-actions">
                    <button class="header-action-btn" onclick="window.parent.location.search='?action=new_chat'" title="新建对话">
                        {PLUS_SVG}
                    </button>
                </div>
            </div>
        `;

        var styleId = 'ac-header-style';
        if (!parentDoc.getElementById(styleId)) {{
            var style = parentDoc.createElement('style');
            style.id = styleId;
            style.innerHTML = `
                #ac-fixed-header {{
                    position: fixed; top: 14px; left: 0; width: 100%; height: 40px; z-index: 999999;
                    display: flex; justify-content: center; align-items: flex-start; pointer-events: none;
                    transition: padding-left 0.3s cubic-bezier(0.2, 0.6, 0.3, 1); box-sizing: border-box;
                }}
                @media (min-width: 992px) {{
                    body:has([data-testid="stSidebar"][aria-expanded="true"]) #ac-fixed-header {{ padding-left: 336px; }}
                }}
                .header-pill {{
                    pointer-events: auto; display: flex; align-items: center; justify-content: space-between;
                    gap: 12px; padding: 6px 6px 6px 14px; border-radius: 20px; min-width: 120px; max-width: 60%;
                    background: rgba(255, 255, 255, 0.9); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
                    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
                    border: 1px solid rgba(0,0,0,0.05); transition: all 0.2s ease;
                }}
                .title-container {{
                    flex: 1; overflow: hidden; display: flex; align-items: center;
                }}
                .header-title {{
                    font-size: 14px; font-weight: 600; color: #31333F; white-space: nowrap;
                    overflow: hidden; text-overflow: ellipsis; cursor: default; margin-right: 4px; display: block;
                }}
                .header-actions {{ display: flex; align-items: center; gap: 2px; }}
                .header-action-btn {{
                    border: none; background: transparent; color: #888; cursor: pointer; padding: 6px;
                    border-radius: 50%; display: flex; align-items: center; justify-content: center;
                    transition: all 0.2s; margin: 0;
                }}
                .header-action-btn:hover {{ background-color: rgba(0,0,0,0.05); color: #FF4B4B; transform: scale(1.05); }}

                @media (prefers-color-scheme: dark) {{
                    .header-pill {{ background: rgba(14, 17, 23, 0.85); border: 1px solid rgba(255,255,255,0.15); }}
                    .header-title {{ color: #FAFAFA; }}
                    .header-action-btn:hover {{ background-color: rgba(255,255,255,0.1); }}
                }}
                @media (max-width: 640px) {{
                    #ac-fixed-header {{ justify-content: flex-end; padding-right: 60px; top: 10px; }}
                    .header-pill {{ padding: 4px 4px 4px 10px; }}
                    .header-title {{ max-width: 150px; }}
                }}
            `;
            parentDoc.head.appendChild(style);
        }}
        parentDoc.body.appendChild(header);
    }})();
    </script>
    """
    components.html(js, height=0, width=0)

# --- 3. 主入口 ---

def render_chat_area():
    """
    渲染聊天区域组件
    """
    # 1. 优先处理后端动作 (目前只有 new_chat)
    handle_header_actions()

    # 2. 渲染前端
    apply_global_styles()
    render_fixed_header()

    chat_container = st.container()
    with chat_container:
        if "messages" in st.session_state and st.session_state.messages:
            current_model = st.session_state.get("current_session_model", "Unknown")
            qa_count = 0 
            for message_index, msg_obj in enumerate(st.session_state.messages):
                role = msg_obj["role"]
                if role == "user":
                    qa_count += 1
                    current_pair_index = qa_count - 1
                    st.markdown(f"<div id='msg-anchor-{current_pair_index}' style='position:relative; top: -80px; visibility: hidden;'></div>", unsafe_allow_html=True)

                render_chat_message(msg_obj, message_index, current_model)

            render_right_sidebar_nav(qa_count)
        else:
            render_right_sidebar_nav(0)