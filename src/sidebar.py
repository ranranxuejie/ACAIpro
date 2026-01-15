# 侧边栏模块 - 处理侧边栏组件
import streamlit as st
from .core import AIClient
from .config import CONFIG
from datetime import datetime

# --- 辅助逻辑函数 ---

def get_session_group(timestamp_str, is_pinned=False):
    """
    解析时间并返回分组名称
    如果 is_pinned 为 True，强制返回 '已置顶'
    """
    if is_pinned:
        return "📌 已置顶"

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

def load_session_to_state(session_id, session_name, session_model, user_token):
    """【封装】加载会话数据到全局状态"""
    if not st.session_state.bot:
        st.session_state.bot = AIClient(user_token)

    st.session_state.bot.token = user_token
    st.session_state.bot.session_id = session_id

    st.session_state.selected_model = session_model or "gemini-3-pro-preview"
    st.session_state.current_session_model = st.session_state.selected_model
    st.session_state.status = f"✅ 已连接: {session_name}"
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
                        "updated": record.get("created", ""),
                        "files": use_files, 
                        "file_name": record.get("fileName", "")
                    })
                if record.get("aiText"):
                    # 从API返回的数据中获取tokens，尝试多种可能的字段名
                    tokens_used = record.get("useTokens", 0) or record.get("completionTokens", 0) or record.get("tokens", 0)
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": record.get("aiText"),
                        "tokens": tokens_used,
                        "useTokens": tokens_used,  # 同时保存为useTokens，保持与handle_user_input一致
                        "updated": record.get("updated", ""),
                        "model": record.get("model", "")  # 添加模型信息
                    })
                for file in use_files:
                    if not any(f.get("name") == file.get("name") for f in st.session_state.useFiles):
                        st.session_state.useFiles.append(file)
        st.toast(f"已加载: {session_name}", icon="✅")
    else:
        st.toast(f"已切换 (无记录)", icon="✅")

# --- 子组件渲染函数 ---

def inject_custom_css():
    """注入侧边栏专用的 CSS"""
    st.markdown("""
    <style>
    /* 全局紧凑调整 */
    div[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] > div { margin-bottom: 0.5rem; }
    div[data-testid="stTextInput"] { margin-bottom: 5px !important; }
    div[data-testid="stTextInput"] input { padding: 8px 10px; font-size: 13px; border-radius: 8px; }

    /* =================================================================================
       【关键修改】响应式网格布局逻辑
       ================================================================================= */

    /* 1. 将 Expand Details 内部的容器转为 CSS Grid */
    div[data-testid="stExpanderDetails"] > div[data-testid="stVerticalBlock"] {
        display: grid !important;
        /* 核心：自动填充，最小宽度 135px。侧边栏拉宽时会自动一行排两个，窄时排一个 */
        grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)) !important;
        gap: 8px !important;
        padding-right: 2px;
    }

    /* 2. 让直接子元素填满网格单元 */
    div[data-testid="stExpanderDetails"] > div[data-testid="stVerticalBlock"] > div {
        width: 100% !important;
    }

    /* 3. 【特殊处理】让包含"标题"和"分割线"的元素跨越整行（不被分栏） */
    /* 使用 :has() 选择器检查是否包含特定类名或 HR 标签 */
    div[data-testid="stExpanderDetails"] > div[data-testid="stVerticalBlock"] > div:has(.session-group-header),
    div[data-testid="stExpanderDetails"] > div[data-testid="stVerticalBlock"] > div:has(hr) {
        grid-column: 1 / -1 !important; /* 强制跨越所有列 */
        margin-top: 5px !important;
    }

    /* 4. 卡片化样式：为每个会话项增加背景和边框，使其像一个小磁贴 */
    div[data-testid="stExpanderDetails"] div[data-testid="stHorizontalBlock"] {
        background-color: rgba(128, 128, 128, 0.04);
        border: 1px solid rgba(128, 128, 128, 0.08);
        border-radius: 6px;
        padding: 4px;
        align-items: center;
        transition: all 0.2s ease;
        height: 100% !important; /* 确保高度一致 */
    }

    /* 悬停卡片效果 */
    div[data-testid="stExpanderDetails"] div[data-testid="stHorizontalBlock"]:hover {
        background-color: rgba(128, 128, 128, 0.08);
        border-color: rgba(128, 128, 128, 0.2);
        transform: translateY(-1px);
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }

    /* ================================================================================= */

    /* --- 1. 左侧会话按钮 (75%) --- */
    div[data-testid="stExpanderDetails"] div[data-testid="column"]:first-child button {
        text-align: left !important; 
        padding: 4px 6px !important; /* 稍微减小内边距以适应小卡片 */
        margin: 0 !important; 
        width: 100% !important; 
        display: block !important; 
        white-space: nowrap !important; 
        overflow: hidden !important; 
        text-overflow: ellipsis !important;
        font-size: 13px !important; 
        line-height: 1.5 !important; 
        min-height: 28px !important;
        transition: background-color 0.2s ease !important;
    }

    /* 未选中状态 (secondary) - 透明 */
    div[data-testid="stExpanderDetails"] div[data-testid="column"]:first-child button[kind="secondary"] {
        background-color: transparent !important; 
        border: none !important;
        box-shadow: none !important;
        color: inherit !important;
    }

    /* 选中状态 (primary) - 明显的左边框和背景 */
    div[data-testid="stExpanderDetails"] div[data-testid="column"]:first-child button[kind="primary"] {
        background-color: rgba(128, 128, 128, 0.15) !important; 
        font-weight: 600 !important;
        border: none !important;
        border-left: 3px solid #FF4B4B !important; 
        border-radius: 2px 4px 4px 2px !important;
    }

    /* --- 2. 右侧菜单按钮 (25%) --- */
    div[data-testid="stExpanderDetails"] div[data-testid="column"]:last-child button {
        background-color: transparent !important; 
        border: none !important; 
        box-shadow: none !important;
        padding: 0 !important; 
        margin: 0 !important; 
        width: 100% !important; 
        height: 28px !important;
        display: flex !important; 
        align-items: center !important; 
        justify-content: center !important;
        opacity: 0; 
        transition: opacity 0.2s !important;
    }

    /* 卡片悬停时，显示右侧按钮 */
    div[data-testid="stHorizontalBlock"]:hover div[data-testid="column"]:last-child button { 
        opacity: 0.5; 
    }

    /* 按钮自身悬停时高亮 */
    div[data-testid="stHorizontalBlock"] div[data-testid="column"]:last-child button:hover {
        opacity: 1 !important; 
        background-color: rgba(128, 128, 128, 0.15) !important;
        border-radius: 4px !important;
        position: relative;
    }

    /* Hover 显示三点图标 */
    div[data-testid="stHorizontalBlock"] div[data-testid="column"]:last-child button:hover::after {
        content: "⋮";
        position: absolute;
        color: #666;
        font-weight: bold;
    }

    div[data-testid="stExpanderDetails"] div[data-testid="column"]:last-child button svg { display: none !important; }

    /* 分组标题 */
    .session-group-header {
        font-size: 12px; color: #888; font-weight: 600;
        padding-top: 10px !important; padding-bottom: 2px !important;
        display: flex !important; align-items: flex-end !important; margin: 0 !important;
    }
    hr { margin-top: 0.2rem !important; margin-bottom: 0.5rem !important; border-color: rgba(128, 128, 128, 0.2) !important; }

    div[data-testid="stPopoverBody"] { padding: 10px !important; }
    div[data-testid="stPopoverBody"] button { margin-bottom: 5px !important; }
    </style>
    """, unsafe_allow_html=True)

def render_model_selector(user_token):
    """渲染模型选择和新建会话区域"""
    if not (st.session_state.models and st.session_state.bot):
        return

    model_values = [m.get("value") for m in st.session_state.models if m.get("value")]
    current_model = st.session_state.current_session_model

    current_session_data = next((s for s in st.session_state.sessions if s.get("id") == st.session_state.bot.session_id), None)
    if current_session_data:
        current_model = current_session_data.get("model", current_model)
        st.session_state.selected_model = current_model

    fixed_cats = ["GPT", "GEMINI", "CLAUDE", "DEEPSEEK", "SORA", "GLM", "QWEN3", "DOUBAO", "其他"]
    model_cats = {c: [] for c in fixed_cats}
    for m in model_values:
        found = False
        for c in fixed_cats[:-1]:
            if c.lower() in m.lower():
                model_cats[c].append(m)
                found = True
                break
        if not found: model_cats["其他"].append(m)

    if "selected_category" not in st.session_state:
        st.session_state.selected_category = "其他"
        for c, ms in model_cats.items():
            if current_model in ms:
                st.session_state.selected_category = c
                break

    with st.container():
        cat_idx = fixed_cats.index(st.session_state.selected_category) if st.session_state.selected_category in fixed_cats else 0
        sel_cat = st.selectbox("模型分类", fixed_cats, index=cat_idx, key="cat_sel", label_visibility="collapsed")
        st.session_state.selected_category = sel_cat

        cat_models = model_cats[sel_cat]
        mod_idx = cat_models.index(current_model) if current_model in cat_models else 0
        sel_model = st.selectbox("具体模型", cat_models, index=mod_idx, key="mod_sel", label_visibility="collapsed")

        if st.button("🆕 新建会话", use_container_width=True, type="primary"):
            if not user_token:
                st.error("需 Token")
            else:
                bot = AIClient(user_token)
                ok, msg = bot.create_session(model=st.session_state.selected_model)
                if ok:
                    load_session_to_state(msg, "新会话", st.session_state.selected_model, user_token)
                    ok_s, data_s = bot.get_sessions()
                    if ok_s: st.session_state.sessions = data_s
                    st.rerun()
                else:
                    st.toast(f"创建失败: {msg}", icon="❌")

    if sel_model != current_model and current_session_data:
        bot = AIClient(user_token)
        if bot.update_session(current_session_data["id"], {"model": sel_model}, current_session_data)[0]:
            for s in st.session_state.sessions:
                if s["id"] == current_session_data["id"]: s["model"] = sel_model
            st.session_state.selected_model = sel_model
            st.session_state.current_session_model = sel_model
            st.toast(f"已切换: {sel_model}", icon="✅")

def render_session_list(user_token):
    """渲染历史会话列表"""
    st.markdown("<div style='margin-top: 5px;'></div>", unsafe_allow_html=True)

    # --- 会话改名区域 ---
    curr_s = next((s for s in st.session_state.sessions if st.session_state.bot and s["id"] == st.session_state.bot.session_id), None)
    if curr_s:
        c1, c2 = st.columns([3, 1])
        new_name = c1.text_input("改名", value=curr_s.get("name", "未命名"), key="name_edit", label_visibility="collapsed")
        if c2.button("💾", key="save_name", use_container_width=True):
            if new_name != curr_s.get("name"):
                if st.session_state.bot.update_session(curr_s["id"], {"name": new_name}, curr_s)[0]:
                    curr_s["name"] = new_name
                    st.toast("已改名", icon="✅")
                    st.rerun()

    # --- 历史列表 ---
    with st.expander("📜 历史会话", expanded=True):
        if not st.session_state.sessions:
            st.info("暂无历史会话")
            return

        query = st.text_input("搜历史", placeholder="搜索...", label_visibility="collapsed")

        # 1. 过滤
        sessions = [s for s in st.session_state.sessions if not query or query.lower() in (s.get("name") or "").lower()]

        # 2. 排序
        sessions.sort(key=lambda x: (x.get('topSort', 0), x.get('created', '')), reverse=True)

        if not sessions:
            st.caption("无匹配会话")
            return

        # 3. 分组
        groups = {}
        group_order = ["📌 已置顶", "今天", "昨天", "过去 7 天", "过去 30 天", "更早", "未知时间"]

        for s in sessions:
            is_pinned = s.get('topSort') == 1
            g = get_session_group(s.get('created'), is_pinned=is_pinned)
            groups.setdefault(g, []).append(s)

        # 4. 渲染
        for g_name in group_order:
            if g_name in groups:
                if not query:
                    # 标题和分割线 (CSS会自动让它们跨整行)
                    st.markdown(f'<div class="session-group-header">{g_name}</div>', unsafe_allow_html=True)
                    st.markdown("---")

                for s in groups[g_name]:
                    s_id = s.get("id")
                    s_name = s.get("name", "未命名")
                    is_active = (st.session_state.bot and str(s_id) == str(st.session_state.bot.session_id))
                    is_pinned = s.get("topSort") == 1

                    with st.container():
                        # 比例 0.75 : 0.25
                        c1, c2 = st.columns([0.75, 0.25], gap="small")

                        # A. 切换按钮
                        if c1.button(s_name, key=f"s_{s_id}", type="primary" if is_active else "secondary", use_container_width=True, help=f"模型: {s.get('model')}"):
                            if user_token:
                                load_session_to_state(s_id, s_name, s.get("model"), user_token)
                                st.rerun()

                        # B. 操作菜单 (空格占位)
                        with c2.popover(" ", use_container_width=True):
                            # 1. 置顶/取消置顶按钮
                            pin_text = "🚫 取消置顶" if is_pinned else "📌 置顶会话"
                            if st.button(pin_text, key=f"pin_{s_id}", use_container_width=True):
                                if user_token:
                                    bot = AIClient(user_token)
                                    ok, msg = bot.toggle_session_pin(s)
                                    if ok:
                                        ok_s, data_s = bot.get_sessions()
                                        if ok_s: st.session_state.sessions = data_s
                                        st.toast("置顶状态已更新", icon="📌")
                                        st.rerun()

                            # 2. 删除按钮
                            if st.button("🔴 删除会话", key=f"d_{s_id}", use_container_width=True):
                                bot = AIClient(user_token)
                                if bot.delete_session(s_id)[0]:
                                    st.session_state.sessions = bot.get_sessions()[1]
                                    if is_active:
                                        st.session_state.bot = None
                                        st.session_state.messages = []
                                    st.toast("已删除", icon="✅")
                                    st.rerun()

def render_config_area(user_token):
    """渲染配置区域"""
    with st.expander("⚙️ 配置", expanded=False):
        saved = st.session_state.get("saved_api_token", CONFIG["token"])
        new_token = st.text_input("API Token", value=saved, type="password", key="token_in")
        if st.checkbox("记住 Token", value=st.session_state.get("remember_token", False)):
            if st.session_state.get("saved_api_token") != new_token:
                st.session_state["saved_api_token"] = new_token
                st.session_state["remember_token"] = True
                st.rerun()
        else:
            if "saved_api_token" in st.session_state:
                del st.session_state["saved_api_token"]
                st.session_state["remember_token"] = False
                st.rerun()

        if "chat_params" not in st.session_state:
            st.session_state.chat_params = {k: CONFIG[k] for k in ["contextCount", "prompt", "temperature"]}

        p = st.session_state.chat_params
        p["contextCount"] = st.slider("上下文", 1, 100, int(p["contextCount"]))
        p["prompt"] = st.text_area("提示词", value=p["prompt"], height=100)
        p["temperature"] = st.slider("温度", 0.0, 1.0, float(p["temperature"]), step=0.1)

        if st.button("保存参数", use_container_width=True):
            CONFIG.update(p)
            st.toast("参数已保存", icon="✅")

# --- 主渲染入口 ---

def render_sidebar():
    """主函数：组合各部分"""
    with st.sidebar:
        inject_custom_css()

        user_token = st.session_state.get("saved_api_token", CONFIG["token"])

        render_model_selector(user_token)
        render_session_list(user_token)
        render_config_area(user_token)