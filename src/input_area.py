# 输入区域模块 - 处理聊天输入和用户输入处理
import streamlit as st
from .core import AIClient
from .utils import process_ai_content
from .file_utils import format_file_attachments

# 渲染输入区域
def render_input_area():
    """
    渲染输入区域组件
    """
    
    # 聊天输入框 - 支持文件上传，使用st.chat_input的accept_file参数
    chat_input = st.chat_input(
        placeholder="询问任何问题",
        key="chat_input",
        accept_file=True,  # 支持上传文件
        max_chars=None,     # 无字符限制
        accept_audio=True,  # 支持上传音频
    )

    # 处理用户输入
    if chat_input:
        # 获取文本内容
        prompt = chat_input.get("text", "")
        
        # 获取上传的文件
        uploaded_files = chat_input.get("files", [])
        uploaded_file = uploaded_files[0] if uploaded_files else None
        
        # 显示上传文件信息
        if uploaded_file:
            st.toast(f"已上传文件: {uploaded_file.name}", icon="✅")
        
        # 调用处理函数
        handle_user_input(prompt, uploaded_file)

# 处理用户输入
def handle_user_input(prompt, uploaded_file):
    """
    处理用户输入
    
    Args:
        prompt (str): 用户输入的文本
        uploaded_file: 用户上传的文件对象
    """
    # 检查是否连接
    if not st.session_state.bot:
        st.error("请先连接会话！")
    else:
        # --- 用户消息处理 ---
        file_name_record = uploaded_file.name if uploaded_file else None

        # 显示用户消息，将文件信息集成到对话内容中
        with st.chat_message("user"):
            # 使用file_utils模块格式化文件附件
            file_html = format_file_attachments([], file_name_record, f"{file_name_record}")
            
            # 如果有文件附件，使用HTML显示
            if file_html:
                st.markdown(file_html, unsafe_allow_html=True)
                # 添加换行
                st.markdown("\n\n")
            
            # 显示用户文本，使用st.text避免markdown渲染
            st.text(prompt)

        # 保存到历史 - 添加tokens属性
        user_message = {
            "role": "user",
            "content": prompt,
            "file_name": file_name_record,
            "tokens": 0,  # 默认值，实际值将从API获取
            "files": []  # 存储当前消息相关的文件
        }
        
        # 将文件信息添加到当前消息的files属性中
        if file_name_record:
            file_info = {
                "name": file_name_record,
                "url": "xxx"  # 实际应用中应该是文件的真实URL
            }
            user_message["files"].append(file_info)
            
            # 同时添加到全局useFiles列表，避免重复
            file_exists = any(file.get("name") == file_name_record for file in st.session_state.useFiles)
            if not file_exists:
                st.session_state.useFiles.append(file_info)
        
        st.session_state.messages.append(user_message)

        # --- AI 消息处理 (流式) ---
        with st.chat_message("assistant"):
            # 使用单个占位符来容纳整个AI回答
            response_placeholder = st.empty()
            full_response = ""
            
            # 迭代流式响应
            for chunk in st.session_state.bot.chat_stream(prompt, uploaded_file):
                full_response += chunk
                
                # 处理AI回复，折叠<think>内容
                main_content, think_content, is_thinking = process_ai_content(full_response)
                
                # 清除之前的内容
                response_placeholder.empty()
                
                # 在占位符中创建一个容器，用于显示当前的AI回答
                with response_placeholder.container():
                    # 如果有思考内容，使用st.expander显示
                    if think_content or is_thinking:
                        with st.expander("查看思考过程"):
                            st.markdown(f"{think_content}{'...' if is_thinking else ''}")
                    
                    # 显示主要内容
                    if main_content:
                        st.markdown(main_content)

        # 获取tokens使用信息
        tokens_used = getattr(st.session_state.bot, 'last_tokens_used', 0)
        
        # 保存 AI 回复到历史 - 添加tokens属性，不包含文件信息
        st.session_state.messages.append({
            "role": "assistant", 
            "content": full_response,
            "tokens": tokens_used  # 使用实际获取的tokens值
        })
        
        # 显示tokens使用信息
        st.caption(f"💡 Use Tokens : {tokens_used}")
        
        # 自动滚动到聊天区域底部
        # 修改逻辑：直接滚动整个窗口到最底部，并添加延迟以确保内容渲染完毕
        st.markdown("""
        <script>
            function scrollToBottom() {
                // 获取文档的高度
                const scrollHeight = document.documentElement.scrollHeight || document.body.scrollHeight;
                // 滚动到最底部
                window.scrollTo({
                    top: scrollHeight,
                    behavior: "smooth"
                });
            }

            // 立即执行一次
            scrollToBottom();

            // 延迟执行，确保 Streamlit 重新渲染 DOM（如 Markdown 解析、代码块高亮）完成后再次滚动
            // 设置多个时间点以应对不同长度内容的渲染耗时
            setTimeout(scrollToBottom, 100);
            setTimeout(scrollToBottom, 300);
            setTimeout(scrollToBottom, 500);
        </script>
        """, unsafe_allow_html=True)
