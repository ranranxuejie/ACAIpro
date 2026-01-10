# 输入区域模块 - 处理聊天输入和用户输入处理
import streamlit as st
import re
from .core import AIClient
from .utils import process_ai_content
from .file_utils import format_file_attachments
from .styles import apply_global_styles
from st_copy import copy_button

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
    
    # 检查是否连接
    if not st.session_state.bot:
        st.error("请先连接会话！")
    else:
        # --- 用户消息处理 ---
        file_name_record = uploaded_file.name if uploaded_file else None

        # 显示用户消息，将文件信息集成到对话内容中
        with st.chat_message("user"):
            # 使用file_utils模块格式化文件附件
            file_html = format_file_attachments(
                [], 
                file_name_record, 
                f"{file_name_record}" if file_name_record else ""
            )
            
            # 如果有文件附件，使用HTML显示
            if file_html:
                st.markdown(file_html, unsafe_allow_html=True)
                # 添加换行
                st.markdown("\n\n")
            
            # 直接显示完整消息，使用st.text避免markdown渲染
            st.text(prompt)
            
            # 操作按钮组
            # 调整列宽：给 action_col2 更多空间 (0.9)，因为它要放三个标签
            action_col1, action_col2 = st.columns([0.1, 0.9], vertical_alignment="center")
            
            # 1. 复制按钮
            with action_col1:
                # 使用copy_button组件
                copy_button(prompt)
            
            # 2. 信息标签组 (Tokens | 时间 | 模型)
            with action_col2:
                # 获取数据
                use_tokens = 0
                updated_time = ""
                model = ""
                
                # 创建标签HTML
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
            
            # 操作按钮组 - 只在最终回复时显示
            # 调整列宽：给 action_col2 更多空间 (0.9)，因为它要放三个标签
            action_col1, action_col2 = st.columns([0.1, 0.9], vertical_alignment="center")
            
            # 1. 复制按钮
            with action_col1:
                # 准备要复制的纯净文本
                text_to_copy = clean_ai_text(full_response)
                # 使用copy_button组件
                copy_button(text_to_copy)
            
            # 2. 信息标签组 (Tokens | 时间 | 模型)
            with action_col2:
                # 获取数据
                tokens_used = getattr(st.session_state.bot, 'last_tokens_used', 0)
                updated_time = ""
                model = ""
                
                # 创建标签HTML
                badges_html = f"""
                <div style="display: flex; flex-direction: row; align-items: center; gap: 8px; flex-wrap: wrap;">
                    <!-- Token 标签 (红色风格) -->
                    <div style="background-color: rgba(255, 75, 75, 0.15); color: #ff4b4b; border: 0px solid rgba(255, 75, 75, 0.3); padding: 2px 8px; border-radius: 4px; font-size: 12px; white-space: nowrap;">
                        💡 {tokens_used} Tokens
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

        # 获取tokens使用信息
        tokens_used = getattr(st.session_state.bot, 'last_tokens_used', 0)
        
        # 保存 AI 回复到历史 - 添加tokens属性，不包含文件信息
        st.session_state.messages.append({
            "role": "assistant", 
            "content": full_response,
            "tokens": tokens_used,  # 使用实际获取的tokens值
            "useTokens": tokens_used  # 保持与API返回格式一致
        })
        
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
