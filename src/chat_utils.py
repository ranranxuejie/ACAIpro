# 聊天工具模块 - 存放聊天相关的共享功能
import streamlit as st
import streamlit.components.v1 as components
import re
from st_copy import copy_button

# --- 1. SVG 图标资源 ---
# 使用 fill="currentColor" 让颜色由 CSS 控制
DELETE_SVG = """
<svg viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg">
    <path d="M256 333.872a28.8 28.8 0 0 1 28.8 28.8V768a56.528 56.528 0 0 0 56.544 56.528h341.328A56.528 56.528 0 0 0 739.2 768V362.672a28.8 28.8 0 0 1 57.6 0V768a114.128 114.128 0 0 1-114.128 114.128H341.328A114.128 114.128 0 0 1 227.2 768V362.672a28.8 28.8 0 0 1 28.8-28.8zM405.344 269.648a28.8 28.8 0 0 0 28.8-28.8 56.528 56.528 0 0 1 56.528-56.544h42.656a56.528 56.528 0 0 1 56.544 56.544 28.8 28.8 0 0 0 57.6 0 114.128 114.128 0 0 0-112.64-114.128h-45.648a114.144 114.144 0 0 0-112.64 114.128 28.8 28.8 0 0 0 28.8 28.8z"></path>
    <path d="M163.2 266.672a28.8 28.8 0 0 1 28.8-28.8h640a28.8 28.8 0 0 1 0 57.6H192a28.8 28.8 0 0 1-28.8-28.8zM426.672 371.2a28.8 28.8 0 0 1 28.8 28.8v320a28.8 28.8 0 0 1-57.6 0V400a28.8 28.8 0 0 1 28.8-28.8zM597.344 371.2a28.8 28.8 0 0 1 28.8 28.8v320a28.8 28.8 0 0 1-57.6 0V400a28.8 28.8 0 0 1 28.8-28.8z"></path>
</svg>
"""

# --- 2. 辅助函数 ---

def clean_ai_text(text):
    """清洗 AI 文本"""
    pattern = r""
    return re.sub(pattern, "", text, flags=re.DOTALL).strip()

def render_badges(tokens=0, time_str="", model_name=""):
    """生成底部的元数据徽章 HTML"""
    badges = []
    if tokens: badges.append(f"💳 {tokens} Tokens")
    if time_str: badges.append(f"⌚️ {time_str}")
    badges.append(f"📛 {model_name}")

    if not badges: return ""
    return f"""
    <div style="display: flex; flex-direction: row; align-items: center; gap: 8px; flex-wrap: wrap; margin-top: 4px;">
        {''.join([f"""
        <div style="background-color: rgba(128, 128, 128, 0.08); color: #888; border: 1px solid rgba(128, 128, 128, 0.1); padding: 2px 10px; border-radius: 12px; font-size: 11px; font-weight: 500; white-space: nowrap; display: flex; align-items: center;">
            {badge_text}
        </div>
        """ for badge_text in badges])}
    </div>
    """

# --- 3. 核心 V1 组件：删除按钮 ---

def render_v1_delete_button(cid, sid, task_id):
    """
    使用 components.html 构建纯 HTML 删除按钮。

    关键修改：
    1. 给 components.html 设置固定的 width=30，防止在窄列中塌陷。
    2. HTML body 设置为 flex 居中，确保图标位置正确。
    """
    html_code = f"""
    <!DOCTYPE html>
    <html style="overflow: hidden;">
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                margin: 0; padding: 0;
                background-color: transparent;
                display: flex; 
                align-items: center; 
                justify-content: center;
                height: 100vh; /* 撑满 iframe 高度 */
                width: 100vw;
                overflow: hidden;
            }}
            .del-btn {{
                border: none; 
                background: transparent; 
                padding: 4px;
                margin: 0;
                cursor: pointer;
                color: #999; /* 默认灰色 */
                transition: color 0.2s ease, transform 0.1s;
                display: flex; 
                align-items: center; 
                justify-content: center;
                width: 24px; 
                height: 24px;
                line-height: 0;
                outline: none;
            }}
            .del-btn:hover {{
                color: #FF4B4B; /* 悬停红色 */
            }}
            .del-btn:active {{
                transform: scale(0.9);
            }}
            svg {{
                width: 16px; 
                height: 16px;
                fill: currentColor;
                display: block;
            }}
        </style>
        <script>
            function handleDelete() {{
                if (confirm('⚠️ 确定要删除这条对话吗？\\n此操作无法撤销。')) {{
                    try {{
                        const params = new URLSearchParams(window.parent.location.search);
                        params.set('del_cid', '{cid}');
                        params.set('del_sid', '{sid}');
                        params.set('del_tid', '{task_id}');
                        window.parent.location.search = params.toString();
                    }} catch(e) {{
                        console.error(e);
                    }}
                }}
            }}
        </script>
    </head>
    <body>
        <button class="del-btn" onclick="handleDelete()" title="删除对话">
            {DELETE_SVG}
        </button>
    </body>
    </html>
    """
    # 【关键】强制设置 width=30 和 height=34，确保它占据物理空间
    components.html(html_code, height=34, width=30, scrolling=False)

def check_and_execute_deletion():
    """
    检查 URL 参数是否有删除指令，如果有则执行删除并清理 URL
    """
    try:
        # 兼容不同版本的 query_params 获取方式
        qp = st.query_params

        # 将 query_params 转换为字典以方便检查
        params_dict = dict(qp)

        if "del_cid" in params_dict:
            del_cid = params_dict["del_cid"]
            del_sid = params_dict.get("del_sid")
            del_tid = params_dict.get("del_tid")

            # 执行删除
            if st.session_state.get("bot"):
                success, msg = st.session_state.bot.delete_chat_record(del_cid, del_sid, del_tid)
                if success:
                    st.toast("删除成功", icon="🗑️")

                    # 刷新数据逻辑：重新加载会话
                    bot = st.session_state.bot
                    # 重新拉取数据
                    ok, _ = bot.get_chat_records(bot.session_id)
                    if ok:
                        from .sidebar import load_session_to_state
                        load_session_to_state(bot.session_id, "", st.session_state.get("current_session_model"), bot.token)
                else:
                    st.toast(f"删除失败: {msg}", icon="❌")

            # 清理 URL 参数，防止刷新时重复触发
            qp.clear()
            # 立即重新运行以清除 URL 并刷新界面
            st.rerun()

    except Exception as e:
        # print(f"Deletion check error: {e}")
        pass

# --- 4. 主渲染函数 ---

def render_chat_message(msg_obj, message_index, model_name="Unknown"):
    # 每次渲染前检查是否有挂起的删除操作
    check_and_execute_deletion()

    role = msg_obj["role"]
    content = msg_obj["content"]

    with st.chat_message(role):
        if role == "user":
            from .file_utils import format_file_attachments
            file_html = format_file_attachments(
                msg_obj.get("files", []),
                msg_obj.get("file_name"),
                msg_obj.get("file_url")
            )
            if file_html:
                st.markdown(file_html, unsafe_allow_html=True)
                st.markdown("\n\n")
            st.text(content)
        else:
            from .utils import process_ai_content
            main_content, think_content, _ = process_ai_content(content)
            if think_content:
                with st.expander("查看思考过程"):
                    st.markdown(think_content)
            if main_content:
                st.markdown(main_content)

        # --- 底部工具栏 ---
        if role == "assistant":
            # 布局：[复制 | 删除] [徽章......]
            buttons_col, badges_col = st.columns([0.15, 0.85], vertical_alignment="center")

            with buttons_col:
                # 左侧复制，右侧删除
                c_copy, c_del = st.columns([0.6, 0.4], gap="small", vertical_alignment="center")

                with c_copy:
                    text_to_copy = clean_ai_text(content)
                    copy_button(text_to_copy)

                with c_del:
                    # 强制渲染删除按钮，不进行 if cid 判断 (假设数据存在)
                    cid = msg_obj.get("cid") or msg_obj.get("id")
                    sid = msg_obj.get("sid") or msg_obj.get("sessionId") or msg_obj.get("session_id")
                    task_id = msg_obj.get("taskId") or msg_obj.get("task_id")

                    # 直接渲染，数据缺失时按钮可能点击无效但会显示
                    render_v1_delete_button(cid or "", sid or "", task_id or "")

        else:
            # 用户消息工具栏
            buttons_col, badges_col = st.columns([0.05, 0.95], vertical_alignment="center")
            with buttons_col:
                copy_button(content)

        # 渲染徽章
        with badges_col:
            use_tokens = msg_obj.get("useTokens", msg_obj.get("tokens", 0))
            updated_time = msg_obj.get("updated", msg_obj.get("timestamp", ""))
            st.html(render_badges(tokens=use_tokens, time_str=updated_time, model_name=model_name))