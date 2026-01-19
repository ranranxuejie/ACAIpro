# AI 助手 Pro 主程序
from src import render_ui

# 1. 页面基础设置
st.set_page_config(
    page_title="Secret", 
    page_icon="🔞", 
    layout="wide",
    initial_sidebar_state="auto"
)

# 2. 渲染主UI
render_ui()