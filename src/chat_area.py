# 聊天区域模块 - 处理聊天界面组件
import streamlit as st
import re
from .utils import process_ai_content
from .file_utils import format_file_attachments
from .styles import apply_global_styles
from st_copy import copy_button

# 渲染聊天区域
def render_chat_area():
    """
    渲染聊天区域组件
    """
    # 应用共享样式
    apply_global_styles()
    
    # 清洗 AI 文本的辅助函数
    def clean_ai_text(text):
        """
        清洗 AI 文本：移除 <think> 及其内容，re.DOTALL 让 . 能匹配换行符
        """
        pattern = r"<think>[\s\S]*?</think>"
        # 替换为空字符串
        cleaned_text = re.sub(pattern, "", text, flags=re.DOTALL)
        # 去除首尾多余空格
        return cleaned_text.strip()

    # --- 2. 渲染聊天记录 ---
    chat_container = st.container()
    with chat_container:
        # 检查 session_state 是否有消息
        if "messages" in st.session_state and st.session_state.messages:
            # 遍历存储的消息对象
            for msg_obj in st.session_state.messages:
                message_index = st.session_state.messages.index(msg_obj)

                with st.chat_message(msg_obj["role"]):
                    if msg_obj["role"] == "user":
                        # 用户消息实现：直接显示完整消息
                        main_content = msg_obj["content"]

                        # 使用file_utils模块格式化文件附件
                        file_html = format_file_attachments(
                            msg_obj.get("files", []),
                            msg_obj.get("file_name"),
                            msg_obj.get("file_url")
                        )

                        # 如果有文件附件，使用HTML显示
                        if file_html:
                            st.markdown(file_html, unsafe_allow_html=True)
                            # 添加换行
                            st.markdown("\n\n")

                        # 直接显示完整消息，使用st.text避免markdown渲染
                        st.text(main_content)
                    else:
                        # AI消息使用默认样式
                        raw_ai_text = msg_obj["content"]

                        # 1. 正常显示内容（可能包含折叠的思考过程）
                        main_content, think_content, _ = process_ai_content(raw_ai_text)

                        # 如果有思考内容，使用折叠面板显示
                        if think_content:
                            with st.expander("查看思考过程"):
                                st.markdown(think_content)

                        # 显示主要内容 - 不限制高度
                        if main_content:
                            st.markdown(main_content)
                    
                    # 操作按钮组
                    # 调整列宽：给 action_col2 更多空间 (0.8)，因为它要放三个标签
                    action_col1, action_col2 = st.columns([0.1, 0.9], vertical_alignment="center")

                    # 1. 复制按钮
                    with action_col1:
                        # 假设 copy_button 是你引入的自定义组件
                        copy_button(main_content)

                    # 2. 信息标签组 (Tokens | 时间 | 模型)
                    with action_col2:
                        # 获取数据
                        use_tokens = msg_obj.get("useTokens", msg_obj.get("tokens", 0))
                        updated_time = msg_obj.get("updated", "")
                        model = msg_obj.get("model", "")

                        # --- 使用 HTML/CSS 实现自适应左对齐 Flex 布局 ---
                        # display: flex; -> 让子元素横向排列
                        # gap: 10px; -> 元素之间的间距
                        # flex-wrap: wrap; -> 屏幕太窄时自动换行

                        badges_html = f"""
                        <div style="display: flex; flex-direction: row; align-items: center; gap: 8px; flex-wrap: wrap;">
                            <!-- Token 标签 (红色风格) -->
                            <div style="background-color: rgba(255, 75, 75, 0.15); color: #ff4b4b; border: 0px solid rgba(255, 75, 75, 0.3); padding: 2px 8px; border-radius: 4px; font-size: 12px; white-space: nowrap;">
                                💡 {use_tokens} Tokens
                            </div>

                            <!-- 时间 标签 (绿色风格) -->
                            <div style="background-color: rgba(33, 195, 84, 0.15); color: #21c354; border: 0px solid rgba(33, 195, 84, 0.3); padding: 2px 8px; border-radius: 4px; font-size: 12px; white-space: nowrap;">
                                ⏰ {updated_time}
                            </div>

                            <!-- 模型 标签 (蓝色风格) -->
                            <div style="background-color: rgba(0, 104, 201, 0.15); color: #0068c9; border: 0px solid rgba(0, 104, 201, 0.3); padding: 2px 8px; border-radius: 4px; font-size: 12px; white-space: nowrap;">
                                🤖 {model}
                            </div>
                        </div>
                        """

                        st.html(badges_html)