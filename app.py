import streamlit as st
import requests
import json
import base64
import os

# ================= 配置区域 =================
# 从环境变量、streamlit secrets或文件读取配置，确保敏感信息不被硬编码

# 优先从streamlit secrets读取，然后是环境变量，最后是文件
# Streamlit Secrets配置示例（.streamlit/secrets.toml）：
# [ai_client]
# token = "your-api-token"

DEFAULT_TOKEN = ""
# API服务器地址配置
BASE_URL = "https://achuanai.vip/api"

# 尝试从streamlit secrets读取
if hasattr(st, 'secrets'):
    try:
        DEFAULT_TOKEN = st.secrets.get("ai_client", {}).get("token", "")
    except Exception:
        pass

# 从环境变量读取，覆盖secrets配置
if os.getenv("AI_CLIENT_TOKEN"):
    DEFAULT_TOKEN = os.getenv("AI_CLIENT_TOKEN")


# ================= 核心后端逻辑 (兼容原代码) =================
class AIClient:
    def __init__(self, token):
        self.token = token
        self.session_id = None
        self.headers = {
            "Authorization": token,
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0",
            "Origin": "https://achuanai.vip",
            "Referer": "https://achuanai.vip/chat",
            "x-app-version": "2.14.0",
            "priority": "u=1, i"
        }

    def create_session(self, model="gemini-3-pro-preview"):
        """
        创建会话
        """
        url = f"{BASE_URL}/chat/session"
        payload = {"model": model, "plugins": [], "mcp": []}
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            if response.status_code == 200:
                res_json = response.json()
                if res_json.get("code") == 0:
                    self.session_id = res_json['data']['id']
                    # 修复点：这里加上 str()，确保返回的是字符串
                    return True, str(self.session_id)
                else:
                    return False, res_json.get('msg')
            return False, f"HTTP {response.status_code}"
        except Exception as e:
            return False, str(e)

    def process_streamlit_file(self, uploaded_file):
        """
        专门处理 Streamlit 的上传文件对象
        无需保存到硬盘，直接在内存转换 Base64
        """
        if not uploaded_file:
            return None

        try:
            # 读取文件字节流
            bytes_data = uploaded_file.getvalue()
            encoded = base64.b64encode(bytes_data).decode('utf-8')

            # 获取文件名和扩展名
            filename = uploaded_file.name
            ext = filename.split('.')[-1]

            # 构造 API 需要的格式
            return {
                "name": filename,
                "data": f"data:application/{ext};base64,{encoded}"
            }
        except Exception as e:
            st.error(f"文件处理失败: {e}")
            return None

    def get_sessions(self):
        """
        获取历史会话列表
        """
        url = f"{BASE_URL}/chat/session"
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                res_json = response.json()
                if res_json.get("code") == 0:
                    return True, res_json.get('data', [])
                else:
                    return False, res_json.get('msg')
            return False, f"HTTP {response.status_code}"
        except Exception as e:
            return False, str(e)

    def get_chat_records(self, session_id, page=1):
        """
        获取指定会话的聊天记录
        """
        url = f"{BASE_URL}/chat/record/{session_id}?page={page}"
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                res_json = response.json()
                if res_json.get("code") == 0:
                    return True, res_json.get('data', {})
                else:
                    return False, res_json.get('msg')
            return False, f"HTTP {response.status_code}"
        except Exception as e:
            return False, str(e)

    def update_session(self, session_id, update_data, session_data):
        """
        更新会话信息（名称或模型）
        """
        url = f"{BASE_URL}/chat/session/{session_id}"
        try:
            # 创建更新的会话数据，保留原有数据，更新指定字段
            updated_data = session_data.copy()
            updated_data.update(update_data)
            
            response = requests.put(url, headers=self.headers, json=updated_data)
            if response.status_code == 200:
                res_json = response.json()
                if res_json.get("code") == 0:
                    return True, "会话信息更新成功"
                else:
                    return False, res_json.get('msg')
            return False, f"HTTP {response.status_code}"
        except Exception as e:
            return False, str(e)
    
    def get_model_list(self):
        """
        获取所有可选模型
        """
        url = f"{BASE_URL}/chat/tmpl"
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                res_json = response.json()
                if res_json.get("code") == 0:
                    return True, res_json.get('data', {})
                else:
                    return False, res_json.get('msg')
            return False, f"HTTP {response.status_code}"
        except Exception as e:
            return False, str(e)

    def chat_stream(self, user_text, file_obj=None):
        """
        流式生成器，适配 Streamlit
        """
        if not self.session_id:
            yield "⚠️ 会话未连接，请检查 Token 并重试。"
            return

        url = f"{BASE_URL}/chat/completions"

        files_data = []
        if file_obj:
            processed_file = self.process_streamlit_file(file_obj)
            if processed_file:
                files_data.append(processed_file)

        payload = {
            "sessionId": self.session_id,
            "text": user_text,
            "files": files_data
        }

        stream_headers = self.headers.copy()
        stream_headers["Accept"] = "text/event-stream"

        try:
            response = requests.post(url, headers=stream_headers, json=payload, stream=True)

            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    if decoded_line.startswith("data:"):
                        json_str = decoded_line[5:].strip()
                        if json_str == "[DONE]":
                            break
                        try:
                            data_obj = json.loads(json_str)
                            # 检查是否包含 "type":"string"，只保留 string 类型的内容
                            if isinstance(data_obj, dict) and data_obj.get("type") == "string":
                                content = data_obj.get("data", "")
                                yield content
                        except:
                            continue
        except Exception as e:
            yield f"❌ 网络请求错误: {e}"

# ================= Streamlit 界面逻辑 =================

# 1. 页面基础设置
st.set_page_config(page_title="AI 助手 Pro", page_icon="🤖", layout="wide")

# 2. 初始化 Session State (变量存储)
if "messages" not in st.session_state:
    st.session_state.messages = []  # 存储聊天记录
if "bot" not in st.session_state:
    st.session_state.bot = None  # 存储机器人实例
if "status" not in st.session_state:
    st.session_state.status = "未连接"
if "sessions" not in st.session_state:
    st.session_state.sessions = []  # 存储会话列表
if "models" not in st.session_state:
    st.session_state.models = []  # 存储模型列表
if "selected_model" not in st.session_state:
    st.session_state.selected_model = "gemini-3-pro-preview"  # 默认模型
if "current_session_model" not in st.session_state:
    st.session_state.current_session_model = "gemini-3-pro-preview"  # 当前会话使用的模型

# 自动加载模型列表
if not st.session_state.models:
    bot_instance = AIClient(DEFAULT_TOKEN)
    success, data = bot_instance.get_model_list()
    if success:
        st.session_state.models = data.get("models", [])
        # 设置默认模型为defModel
        if data.get("defModel"):
            st.session_state.selected_model = data.get("defModel")
            st.session_state.current_session_model = data.get("defModel")

# 自动加载会话列表并打开最近一次对话
if not st.session_state.sessions:
    bot_instance = AIClient(DEFAULT_TOKEN)
    success, data = bot_instance.get_sessions()
    if success:
        st.session_state.sessions = data
        if not st.session_state.bot:
            st.session_state.bot = bot_instance
        
        # 如果有会话，选择最近的一个
        if data:
            # 根据创建时间排序，取最新的会话
            recent_session = max(data, key=lambda x: x.get('created', ''))
            session_id = recent_session.get('id')
            session_name = recent_session.get('name', '未命名会话')
            
            # 设置当前会话ID
            st.session_state.bot.session_id = session_id
            
            # 自动选择当前会话的模型
            session_model = recent_session.get("model", "gemini-3-pro-preview")
            st.session_state.selected_model = session_model
            st.session_state.current_session_model = session_model
            
            st.session_state.status = f"✅ 已连接到会话: {session_name}"
            
            # 加载该会话的历史聊天记录
            success, records_data = st.session_state.bot.get_chat_records(session_id)
            if success and records_data.get("records"):
                # 清空当前消息列表
                st.session_state.messages = []
                # 将历史记录转换为消息格式
                # 确保按时间正序添加，先反转记录列表
                for record in reversed(records_data["records"]):
                    user_text = record.get("userText")
                    ai_text = record.get("aiText")
                    
                    if user_text:
                        st.session_state.messages.append({
                            "role": "user",
                            "content": user_text
                        })
                    if ai_text:
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": ai_text
                        })

# 确保当前会话模型正确设置
if st.session_state.bot and st.session_state.bot.session_id and st.session_state.sessions:
    # 查找当前会话信息
    for session in st.session_state.sessions:
        if session.get("id") == st.session_state.bot.session_id:
            # 更新当前会话模型
            session_model = session.get("model", st.session_state.selected_model)
            st.session_state.current_session_model = session_model
            st.session_state.selected_model = session_model
            break

# 3. 侧边栏：历史会话列表
with st.sidebar:
    # API密钥配置区
    st.subheader("配置")
    
    # 从session_state获取保存的token，默认使用DEFAULT_TOKEN
    saved_token = st.session_state.get("saved_api_token", DEFAULT_TOKEN)
    
    user_token = st.text_input(
        "API Token",
        value=saved_token,
        type="password",
        help="输入您的API令牌",
        key="api_token_input"  # 添加唯一key，避免重复ID错误
    )
    
    # 添加记住token选项
    remember_token = st.checkbox("记住API Token", value=st.session_state.get("remember_token", False))
    
    # 如果用户勾选了记住token，保存到session_state
    if remember_token:
        st.session_state["saved_api_token"] = user_token
        st.session_state["remember_token"] = True
    else:
        # 如果取消记住，清除保存的token
        if "saved_api_token" in st.session_state:
            del st.session_state["saved_api_token"]
        st.session_state["remember_token"] = False
    
    # 当用户输入token时，重新加载会话列表
    if user_token:
        # 创建bot实例使用用户输入的token
        bot_instance = AIClient(user_token)
        
        # 如果会话列表为空，加载会话列表
        if not st.session_state.sessions:
            success, data = bot_instance.get_sessions()
            if success:
                st.session_state.sessions = data
                # 如果有会话，设置当前会话
                if data:
                    # 根据创建时间排序，取最新的会话
                    recent_session = max(data, key=lambda x: x.get('created', ''))
                    session_id = recent_session.get('id')
                    session_name = recent_session.get('name', '未命名会话')
                    
                    # 设置当前会话ID
                    bot_instance.session_id = session_id
                    st.session_state.bot = bot_instance
                    
                    # 自动选择当前会话的模型
                    session_model = recent_session.get("model", "gemini-3-pro-preview")
                    st.session_state.selected_model = session_model
                    st.session_state.current_session_model = session_model
                    
                    st.session_state.status = f"✅ 已连接到会话: {session_name}"
                    
                    # 加载该会话的历史聊天记录
                    success, records_data = st.session_state.bot.get_chat_records(session_id)
                    if success and records_data.get("records"):
                        # 清空当前消息列表
                        st.session_state.messages = []
                        # 将历史记录转换为消息格式
                        for record in reversed(records_data["records"]):
                            user_text = record.get("userText")
                            ai_text = record.get("aiText")
                            
                            if user_text:
                                st.session_state.messages.append({
                                    "role": "user",
                                    "content": user_text
                                })
                            if ai_text:
                                st.session_state.messages.append({
                                    "role": "assistant",
                                    "content": ai_text
                                })
                else:
                    st.info("暂无历史会话")
    
    # 顶部功能区：新建会话和修改当前会话名称
    
    # 获取当前会话信息
    current_session_name = "未命名会话"
    current_session_id = None
    current_session_data = None
    
    if st.session_state.bot and st.session_state.bot.session_id:
        # 查找当前会话信息
        for session in st.session_state.sessions:
            if session.get("id") == st.session_state.bot.session_id:
                current_session_name = session.get("name", "未命名会话")
                current_session_id = session.get("id")
                current_session_data = session
                break
    
    # 新建会话按钮
    if st.button("🆕 新建会话", use_container_width=True):
        if not user_token:
            st.error("请先输入API Token！")
        else:
            bot_instance = AIClient(user_token)
            # 使用用户选择的模型创建会话
            success, msg = bot_instance.create_session(model=st.session_state.selected_model)
            if success:
                st.session_state.bot = bot_instance
                st.session_state.status = f"✅ 已创建新会话 (ID: {msg[-6:]})"
                st.session_state.messages = []
                # 刷新会话列表
                success, data = bot_instance.get_sessions()
                if success:
                    st.session_state.sessions = data
                # 更新当前会话使用的模型
                st.session_state.current_session_model = st.session_state.selected_model
                st.toast("新会话创建成功！", icon="✅")
            else:
                st.toast(f"创建新会话失败: {msg}", icon="❌")
    
    # 修改当前会话名称功能
    if current_session_id and current_session_data:
        # 支持随时修改的会话名称输入框，使用更简洁的标签
        new_name = st.text_input("会话名称", value=current_session_name, key="current_session_name_edit", label_visibility="collapsed")
        
        # 保存按钮
        if st.button("💾 保存", use_container_width=True):
            if new_name and new_name != current_session_name:
                # 更新会话名称
                success, msg = st.session_state.bot.update_session(current_session_id, {"name": new_name}, current_session_data)
                if success:
                    # 更新本地会话列表
                    for i, s in enumerate(st.session_state.sessions):
                        if s.get("id") == current_session_id:
                            st.session_state.sessions[i]["name"] = new_name
                            break
                    # 更新当前会话名称显示
                    current_session_name = new_name
                    st.toast(f"会话名称已更新为: {new_name}", icon="✅")
                else:
                    st.toast(f"更新失败: {msg}", icon="❌")
    
    # 显示会话列表
    if st.session_state.sessions:
        for session in st.session_state.sessions:
            session_id = session.get("id")
            session_name = session.get("name", "未命名会话")
            created_time = session.get("created", "")
            
            # 创建会话选择按钮
            if st.button(f"{session_name}", key=f"session_{session_id}", use_container_width=True):
                # 检查是否有有效token
                if not user_token:
                    st.error("请先输入API Token！")
                    continue
                    
                # 设置当前会话ID
                if st.session_state.bot:
                    # 确保bot实例使用正确的token
                    st.session_state.bot.token = user_token
                    st.session_state.bot.session_id = session_id
                    
                    # 自动选择当前会话的模型
                    session_model = session.get("model", "gemini-3-pro-preview")
                    st.session_state.selected_model = session_model
                    st.session_state.current_session_model = session_model
                    
                    st.session_state.status = f"✅ 已切换到会话: {session_name}"
                    # 清空当前聊天记录，因为切换了会话
                    st.session_state.messages = []
                    
                    # 加载该会话的历史聊天记录
                    success, data = st.session_state.bot.get_chat_records(session_id)
                    if success:
                        if data.get("records"):
                            # 将历史记录转换为消息格式
                            # 确保按时间正序添加，先反转记录列表
                            for record in reversed(data["records"]):
                                # 每条记录包含一个完整的对话回合
                                user_text = record.get("userText")
                                ai_text = record.get("aiText")
                                
                                # 添加用户消息
                                if user_text:
                                    st.session_state.messages.append({
                                        "role": "user",
                                        "content": user_text
                                    })
                                
                                # 添加AI回复
                                if ai_text:
                                    st.session_state.messages.append({
                                        "role": "assistant",
                                        "content": ai_text
                                    })
                            st.toast(f"已切换到会话: {session_name}，加载了 {len(data['records'])} 条历史记录", icon="✅")
                        else:
                            st.toast(f"已切换到会话: {session_name}，但没有历史记录", icon="✅")
                    else:
                        st.toast(f"加载历史记录失败: {data}", icon="❌")
                        st.toast(f"已切换到会话: {session_name}", icon="✅")
                else:
                    bot_instance = AIClient(user_token)
                    bot_instance.session_id = session_id
                    st.session_state.bot = bot_instance
                    
                    # 自动选择当前会话的模型
                    session_model = session.get("model", "gemini-3-pro-preview")
                    st.session_state.selected_model = session_model
                    st.session_state.current_session_model = session_model
                    
                    st.session_state.status = f"✅ 已连接到会话: {session_name}"
                    st.session_state.messages = []
                    
                    # 加载该会话的历史聊天记录
                    success, data = bot_instance.get_chat_records(session_id)
                    if success:
                        if data.get("records"):
                            # 将历史记录转换为消息格式
                            # 确保按时间正序添加，先反转记录列表
                            for record in reversed(data["records"]):
                                # 每条记录包含一个完整的对话回合
                                user_text = record.get("userText")
                                ai_text = record.get("aiText")
                                
                                # 添加用户消息
                                if user_text:
                                    st.session_state.messages.append({
                                        "role": "user",
                                        "content": user_text
                                    })
                                
                                # 添加AI回复
                                if ai_text:
                                    st.session_state.messages.append({
                                        "role": "assistant",
                                        "content": ai_text
                                    })
                            st.toast(f"已连接到会话: {session_name}，加载了 {len(data['records'])} 条历史记录", icon="✅")
                        else:
                            st.toast(f"已连接到会话: {session_name}，但没有历史记录", icon="✅")
                    else:
                        st.toast(f"加载历史记录失败: {data}", icon="❌")
                        st.toast(f"已连接到会话: {session_name}", icon="✅")
            
            
    else:
        st.info("暂无历史会话")

# 4. 自动初始化 (如果还没连接)
if st.session_state.bot is None and not st.session_state.sessions:
    # 如果没有bot实例且没有会话列表，显示警告
    st.warning("请确保已加载会话列表")

# 辅助函数：处理AI回复，折叠<think>标签内容
def process_ai_content(content):
    """
    处理AI回复内容，将<think>...</think>标签内的内容折叠
    """
    import re
    
    # 使用正则表达式匹配<think>标签内容
    pattern = r'<think>(.*?)</think>'
    matches = re.findall(pattern, content, re.DOTALL)
    
    if matches:
        # 提取<think>标签内容
        think_content = matches[0]
        # 提取主要内容（去除<think>标签）
        main_content = re.sub(pattern, '', content, flags=re.DOTALL)
        
        # 返回处理后的内容和思考内容
        return main_content.strip(), think_content.strip()
    else:
        # 没有<think>标签，返回原内容
        return content, None

# 5. 渲染历史聊天记录
for message in st.session_state.messages:
    # 区分用户和AI的样式
    avatar = "👤" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar):
        if message["role"] == "assistant":
            # 处理AI回复，折叠<think>内容
            main_content, think_content = process_ai_content(message["content"])
            
            # 如果有思考内容，使用折叠面板显示在最上面
            if think_content:
                with st.expander("查看深度思考"):
                    st.markdown(think_content)
            
            # 显示主要内容
            if main_content:
                st.markdown(main_content)
        else:
            # 用户消息直接显示
            st.markdown(message["content"])
        
        if "file_name" in message and message["file_name"]:
            st.caption(f"📎 附件: {message['file_name']}")

# 6. 处理用户输入
# 聊天输入区域
prompt = st.chat_input("输入您的问题...")

# 输入栏下方区域 - 模型选择和附件上传
# 使用固定容器确保它们始终在输入框下方
with st.container():
    st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
    
    # 创建两列布局，用于放置模型选择和附件上传
    input_col1, input_col2 = st.columns([1, 1], gap="medium")
    
    with input_col1:
        # 模型选择栏 - 确保显示最近会话的模型
        if st.session_state.models and st.session_state.bot:
            # 直接使用模型的value值作为显示文本
            model_values = [model.get("value") for model in st.session_state.models if model.get("value")]
            
            # 获取当前会话信息
            current_session_id = None
            current_session_data = None
            current_session_model = st.session_state.current_session_model
            
            # 查找当前会话信息，确保使用正确的模型
            for session in st.session_state.sessions:
                if session.get("id") == st.session_state.bot.session_id:
                    current_session_id = session.get("id")
                    current_session_data = session
                    # 确保使用当前会话的模型
                    current_session_model = session.get("model", st.session_state.current_session_model)
                    # 更新状态
                    st.session_state.selected_model = current_session_model
                    st.session_state.current_session_model = current_session_model
                    break
            
            # 创建下拉选择框，显示标题，直接使用current_session_model
            selected_model_value = st.selectbox(
                "选择模型",
                options=model_values,
                index=model_values.index(current_session_model) if current_session_model in model_values else 0,
                key="model_select"
            )
            
            # 确保bot实例使用正确的token
            if user_token:
                st.session_state.bot.token = user_token
            
            # 如果模型发生变化，更新会话使用的模型
            if selected_model_value != current_session_model and current_session_id and current_session_data:
                # 更新会话模型（发送PUT请求）
                success, msg = st.session_state.bot.update_session(current_session_id, {"model": selected_model_value}, current_session_data)
                if success:
                    # 更新本地会话列表
                    for i, s in enumerate(st.session_state.sessions):
                        if s.get("id") == current_session_id:
                            st.session_state.sessions[i]["model"] = selected_model_value
                            break
                    # 更新状态
                    st.session_state.selected_model = selected_model_value
                    st.session_state.current_session_model = selected_model_value
                    st.toast(f"已切换到模型: {selected_model_value}", icon="✅")
                else:
                    st.toast(f"更新模型失败: {msg}", icon="❌")
    
    with input_col2:
        # 附件上传入口
        uploaded_file = st.file_uploader(
            "📎 上传文档/图片", 
            help="支持拖入上传或点击选择文件",
            label_visibility="collapsed"
        )
        
        if uploaded_file:
            st.info(f"已选择: {uploaded_file.name}")

if prompt:

    # 检查是否连接
    if not st.session_state.bot:
        st.error("请先连接会话！")
    else:
        # --- 用户消息处理 ---
        file_name_record = uploaded_file.name if uploaded_file else None

        # 显示用户消息
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
            if file_name_record:
                st.caption(f"📎 已上传: {file_name_record}")

        # 保存到历史
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
            "file_name": file_name_record
        })

        # --- AI 消息处理 (流式) ---
        with st.chat_message("assistant", avatar="🤖"):
            # 使用占位符实现流式响应，支持处理<think>标签
            response_placeholder = st.empty()
            full_response = ""
            
            # 迭代流式响应
            for chunk in st.session_state.bot.chat_stream(prompt, uploaded_file):
                full_response += chunk
                
                # 处理AI回复，折叠<think>内容
                main_content, think_content = process_ai_content(full_response)
                
                # 生成显示内容
                display_content = ""
                
                # 如果有思考内容，使用折叠面板显示
                if think_content:
                    display_content += f"""
<details>
  <summary>💡 深度思考</summary>
  <div style="margin-top: 10px;">
    {think_content}
  </div>
</details>
                    """
                
                # 添加主要内容
                display_content += main_content
                
                # 更新占位符内容
                response_placeholder.markdown(display_content, unsafe_allow_html=True)

        # 保存 AI 回复到历史
        st.session_state.messages.append({"role": "assistant", "content": full_response})
