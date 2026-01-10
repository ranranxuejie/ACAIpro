# 样式模块 - 存储共享的CSS样式

# 共享的CSS样式
global_css = """
<style>
/* 设置代码块样式 */
.stMarkdown pre {
    max-height: 300px;
    overflow-y: auto;
}

/* 设置聊天输入框样式 */
[data-testid='stChatInput'] textarea {
    font-size: 1.2rem !important;
    border-radius: 0.5rem !important;
}

/* 尝试圆角化输入框容器 */
[data-testid='stChatInput'] > div:first-child {
    border-radius: 0.8rem !important;
    overflow: hidden !important;
    min-height: 8rem !important;
}

/* 用户消息样式：靠右显示 */
[data-testid="stChatMessage"]:has([aria-label="Chat message from user"]) {
    background-color: #2F2F2F !important;
    margin-left: auto !important;
    margin-right: 0 !important;
    max-width: 66.67% !important;
    text-align: left !important;
    display: flex !important;
    flex-direction: row-reverse !important;
    align-items: flex-start !important;
}

/* 调整头像和内容之间的间距 */
[data-testid="stChatMessage"]:has([aria-label="Chat message from user"]) > div:first-child {
    margin-left: 0.5rem !important;
    margin-right: 0 !important;
}
</style>
"""

# 应用共享样式
def apply_global_styles():
    """
    应用共享的CSS样式
    """
    import streamlit as st
    st.markdown(global_css, unsafe_allow_html=True)
