# 侧边栏模块 - 处理侧边栏组件
import streamlit as st
import streamlit.components.v1 as components
from .core import AIClient
from .config import CONFIG
from datetime import datetime


# --- 1. 辅助逻辑函数 ---

def get_session_group(timestamp_str, is_pinned=False):
    if is_pinned: return "📌 已置顶"
    if not timestamp_str: return "未知时间"
    try:
        if isinstance(timestamp_str, int):
            dt = datetime.fromtimestamp(timestamp_str)
        else:
            clean_ts = str(timestamp_str).replace('Z', '')
            dt = datetime.fromisoformat(clean_ts) if 'T' in clean_ts else datetime.strptime(clean_ts, "%Y-%m-%d %H:%M:%S")

        now = datetime.now()
        diff_days = (now.date() - dt.date()).days
        if diff_days == 0: return "今天"
        if diff_days == 1: return "昨天"
        if diff_days <= 7: return "过去 7 天"
        if diff_days <= 30: return "过去 30 天"
        return "更早"
    except:
        return "未知时间"
def load_session_to_state(session_id, session_name, session_model, user_authorization):
    """加载会话数据到全局状态"""
    if not st.session_state.bot:
        st.session_state.bot = AIClient(user_authorization)

    # --- 修复点：同时更新 authorization 属性和 headers 字典 ---
    st.session_state.bot.authorization = user_authorization
    st.session_state.bot.headers["Authorization"] = user_authorization 
    # -----------------------------------------------

    st.session_state.bot.session_id = session_id

    # 确保模型状态同步
    curr_model = session_model or "gemini-3-pro-preview"
    st.session_state.selected_model = curr_model
    st.session_state.current_session_model = curr_model

    st.session_state.messages = [] 
    st.session_state.useFiles = [] 

    success, data = st.session_state.bot.get_chat_records(session_id)
    if success and data.get("records"):
        for record in reversed(data["records"]):
            use_files = record.get("useFiles", []) or []
            if record.get("userText"):
                st.session_state.messages.append({
                    "role": "user", 
                    "content": record.get("userText"),
                    "files": use_files, 
                    "file_name": record.get("fileName", "")
                })
            if record.get("aiText"):
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": record.get("aiText"),
                    "tokens": record.get("completionTokens", 0)
                })
            for file in use_files:
                if not any(f.get("name") == file.get("name") for f in st.session_state.useFiles):
                    st.session_state.useFiles.append(file)
        st.toast(f"已加载: {session_name}", icon="✅")
    else:
        st.toast(f"已切换 (无记录)", icon="✅")
    st.rerun()

# --- 2. 核心：使用 V1 组件注入高级样式 ---

def inject_sidebar_styles_via_js():
    """
    CSS 修复版：实现【整行高亮】效果。
    策略：
    1. 识别包含 'primary' 按钮的行容器 (stHorizontalBlock)。
    2. 将红色背景和左边框应用在‘行容器’上，而不是按钮上。
    3. 将行内的按钮背景设为透明，以便透出行容器的颜色。
    """
    js = """
    <script>
    (function() {
        var parentDoc = window.parent.document;
        var oldStyle = parentDoc.getElementById('ac-pro-sidebar-style');
        if (oldStyle) oldStyle.remove();

        var style = parentDoc.createElement('style');
        style.id = 'ac-pro-sidebar-style';
        style.innerHTML = `
            /* 1. 布局重置 */
            [data-testid="stSidebar"] [data-testid="stVerticalBlock"] { 
                gap: 0rem !important; 
            }

            /* =================================================================================
               2. 行容器样式 (stHorizontalBlock)
               ================================================================================= */

            /* 默认状态：透明，带过渡动画 */
            [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] {
                min-height: 36px !important;
                margin-bottom: 2px !important;
                border-radius: 6px;
                padding: 0 !important;
                background-color: transparent !important;
                border: 1px solid transparent !important; /* 预留边框位置 */
                border-left: 3px solid transparent !important; /* 左侧指示条预留 */
                transition: background-color 0.15s ease, border-color 0.15s ease;
                align-items: center !important;
            }

            /* 悬停状态：显示极淡的背景 */
            [data-testid="stSidebar"] [data-testid="stHorizontalBlock"]:hover {
                background-color: rgba(128, 128, 128, 0.08) !important;
            }

            /* 【核心】选中状态：整行高亮 */
            /* 逻辑：如果这个行容器的第一列里有一个 primary 按钮，那么这个行就是被选中的 */
            [data-testid="stSidebar"] [data-testid="stHorizontalBlock"]:has([data-testid="column"]:first-child button[kind="primary"]) {
                background-color: rgba(255, 75, 75, 0.1) !important; /* 红色背景 */
                border-left: 3px solid #FF4B4B !important; /* 左侧红条 */
            }

            /* =================================================================================
               3. 按钮样式 (作用于行内)
               ================================================================================= */

            /* 强制将行内的所有按钮背景设为透明，否则会挡住行的红色背景 */
            [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] button {
                background: transparent !important;
                background-color: transparent !important;
                border: none !important;
                box-shadow: none !important;
                width: 100% !important;
                text-align: left !important;
                height: 100% !important;
                min-height: 36px !important;
                padding: 0 8px !important;
                margin: 0 !important;
            }

            /* 选中按钮的文字颜色 (Primary) */
            [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] [data-testid="column"]:first-child button[kind="primary"] {
                color: #FF4B4B !important;
                font-weight: 600 !important;
            }

            /* 未选中按钮的文字颜色 (Secondary) */
            [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] [data-testid="column"]:first-child button[kind="secondary"] {
                color: rgba(140, 140, 140, 0.9) !important;
                font-weight: 400 !important;
            }
            /* 深色模式适配 */
            @media (prefers-color-scheme: dark) {
                [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] [data-testid="column"]:first-child button[kind="secondary"] {
                    color: rgba(200, 200, 200, 0.8) !important;
                }
            }

            /* =================================================================================
               4. 右侧菜单按钮 (...)
               ================================================================================= */
            [data-testid="stSidebar"] [data-testid="column"]:last-child button {
                color: transparent !important;
                justify-content: center !important;
                width: 32px !important;
            }

            [data-testid="stSidebar"] [data-testid="column"]:last-child button::after {
                content: "•••";
                color: #999;
                font-size: 12px;
                opacity: 0;
                transition: opacity 0.2s;
            }

            /* 只要行被悬停，就显示菜单按钮 */
            [data-testid="stSidebar"] [data-testid="stHorizontalBlock"]:hover [data-testid="column"]:last-child button::after {
                opacity: 1;
            }

            [data-testid="stSidebar"] [data-testid="column"]:last-child button:hover::after {
                color: #FF4B4B; /* 悬停变红 */
            }

            [data-testid="stSidebar"] [data-testid="column"]:last-child button svg { display: none !important; }

            /* =================================================================================
               5. 标题样式
               ================================================================================= */
            .session-header {
                font-size: 11px;
                font-weight: 700;
                color: #888;
                text-transform: uppercase;
                margin-top: 5px !important;
                margin-bottom: 5px !important;
                padding-left: 4px;
                letter-spacing: 0.5px;
            }

            /* 压缩容器内边距 */
            [data-testid="stSidebar"] [data-testid="column"] { padding: 0 !important; min-width: 0 !important; }
        `;
        parentDoc.head.appendChild(style);
    })();
    </script>
    """
    components.html(js, height=0, width=0)

# --- 3. 组件渲染函数 ---
def render_model_selector(user_authorization):
    """
    渲染模型选择器，保持双重逻辑
    """
    
    if not (st.session_state.models and st.session_state.bot): return

    active_session_id = st.session_state.bot.session_id
    current_session_model = st.session_state.get("current_session_model")

    # 逻辑：正在聊天 ? 显示当前聊天模型 : 显示全局默认模型
    display_model = current_session_model if active_session_id else st.session_state.get("selected_model")

    if not display_model and st.session_state.models:
        display_model = st.session_state.models[0]["value"]

    with st.container():
        
        # 注意：这里的“新建对话”按钮在 stHorizontalBlock 之外
        if st.button("✨ 新建对话", use_container_width=True, type="primary"):
            if not user_authorization: 
                st.error("缺 Authorization")
            else:
                bot = AIClient(user_authorization)
                ok, msg = bot.create_session(model=selected_val)
                if ok: 
                    # --- 修复点：新建成功后，立即同步一次会话列表 ---
                    # 这样 rerun 后，侧边栏列表中就包含了这个新会话，状态才是一致的
                    success_list, sessions_data = bot.get_sessions()
                    if success_list:
                        st.session_state.sessions = sessions_data
                    # ---------------------------------------------

                    load_session_to_state(msg, "New Chat", selected_val, user_authorization)
                else: 
                    st.toast(msg, icon="❌")

        all_models = [m["value"] for m in st.session_state.models]
        if display_model not in all_models: all_models.insert(0, display_model)
        st.html('<div style="height: 15px;"></div>')
        selected_val = st.selectbox(
            "选择模型", 
            all_models, 
            index=all_models.index(display_model) if display_model in all_models else 0,
            label_visibility="collapsed",
            key="sidebar_model_select"
        )

        if selected_val != display_model:
            st.session_state.selected_model = selected_val
            if active_session_id:
                curr_s = next((s for s in st.session_state.sessions if s["id"] == active_session_id), None)
                if curr_s:
                    bot = AIClient(user_authorization)
                    ok, _ = bot.update_session(active_session_id, {"model": selected_val}, curr_s)
                    if ok:
                        curr_s["model"] = selected_val
                        st.session_state.current_session_model = selected_val
                        st.toast(f"已切换模型至 {selected_val}", icon="🔄")
                        st.rerun()
            else:
                st.rerun()

def render_session_list(user_authorization):
    st.html('<div style="height: 15px;"></div>')
    st.text_input("搜索", placeholder="🔍 搜索...", key="search_query", label_visibility="collapsed")
    query = st.session_state.get("search_query", "").lower()
    st.html('<div style="height: 15px;"></div>')
    if not st.session_state.sessions:
        st.info("暂无历史", icon="📭")
        return

    sessions = st.session_state.sessions
    if query: sessions = [s for s in sessions if query in (s.get("name") or "").lower()]
    sessions.sort(key=lambda x: (x.get('topSort', 0), x.get('updated', '')), reverse=True)

    groups = {}
    group_order = ["📌 已置顶", "今天", "昨天", "过去 7 天", "更早", "未知时间"]
    for s in sessions:
        g = get_session_group(s.get('updated'), is_pinned=s.get('topSort')==1)
        groups.setdefault(g, []).append(s)

    first_group = True
    for g_name in group_order:
        if g_name in groups:
            # 物理空行
            st.html('<div style="height: 5px;"></div>')

            # 显示标题
            if not query:
                st.markdown(f'<div class="session-header">{g_name}</div>', unsafe_allow_html=True)

            # 再加一点小间距
            st.html('<div style="height: 15px;"></div>')


            first_group = False

            for s in groups[g_name]:
                s_id = s["id"]
                s_name = s.get("name", "未命名")

                is_active = (st.session_state.bot and str(s_id) == str(st.session_state.bot.session_id))
                is_pinned = s.get("topSort") == 1

                # 这种 columns 结构会被 CSS 捕获为 stHorizontalBlock
                c1, c2 = st.columns([0.85, 0.15])

                with c1:
                    # is_active 决定了 primary/secondary
                    # CSS 监控这一行：如果有 primary 按钮，整行变红
                    if st.button(s_name, key=f"sess_{s_id}", type="primary" if is_active else "secondary"):
                        load_session_to_state(s_id, s_name, s.get("model"), user_authorization)

                with c2:
                    with st.popover(" ", use_container_width=True):
                        st.markdown(f"**{s_name}**")

                        pin_label = "🚫 取消置顶" if is_pinned else "📌 置顶"
                        if st.button(pin_label, key=f"pin_{s_id}", use_container_width=True):
                            bot = AIClient(user_authorization)
                            if bot.toggle_session_pin(s)[0]:
                                st.session_state.sessions = bot.get_sessions()[1]
                                st.rerun()

                        new_name = st.text_input("重命名", value=s_name, key=f"ren_{s_id}")
                        if new_name != s_name and st.button("确认修改", key=f"ren_btn_{s_id}"):
                             bot = AIClient(user_authorization)
                             bot.update_session(s_id, {"name": new_name}, s)
                             s["name"] = new_name 
                             st.rerun()

                        st.divider()
                        if st.button("🗑️ 删除", key=f"del_{s_id}", type="primary", use_container_width=True):
                            bot = AIClient(user_authorization)
                            if bot.delete_session(s_id)[0]:
                                st.session_state.sessions = bot.get_sessions()[1]
                                if is_active: 
                                    st.session_state.bot = None
                                    st.session_state.messages = []
                                st.rerun()

def render_config_area():
    with st.expander("⚙️ 设置", expanded=False):
        saved = st.session_state.get("saved_api_authorization", CONFIG["authorization"])
        new_authorization = st.text_input("API Authorization", value=saved, type="password", key="authorization_in")
        
        col_c1, col_c2 = st.columns([0.6, 0.4])
        if col_c1.checkbox("记住 Authorization", value=st.session_state.get("remember_authorization", False)):
            if st.session_state.get("saved_api_authorization") != new_authorization:
                st.session_state["saved_api_authorization"] = new_authorization
                st.session_state["remember_authorization"] = True
                st.rerun()
        else:
            if "saved_api_authorization" in st.session_state:
                del st.session_state["saved_api_authorization"]
                st.session_state["remember_authorization"] = False
                st.rerun()

        st.divider()
        if "chat_params" not in st.session_state:
            st.session_state.chat_params = {k: CONFIG[k] for k in ["contextCount", "prompt", "temperature"]}

        p = st.session_state.chat_params
        p["contextCount"] = st.slider("Context (上下文)", 1, 100, int(p["contextCount"]))
        p["temperature"] = st.slider("Temperature (温度)", 0.0, 1.0, float(p["temperature"]), step=0.1)
        p["prompt"] = st.text_area("System Prompt", value=p["prompt"], height=80)

        if st.button("💾 保存参数", use_container_width=True):
            CONFIG.update(p)
            st.toast("配置已保存", icon="✅")

# --- 4. 主入口 ---

def render_sidebar():
    with st.sidebar:
        inject_sidebar_styles_via_js()
        user_authorization = st.session_state.get("saved_api_authorization", CONFIG["authorization"])
        render_model_selector(user_authorization)
        st.write("") 
        render_session_list(user_authorization)
        st.divider()
        render_config_area()