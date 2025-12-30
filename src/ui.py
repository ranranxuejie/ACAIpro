# UI组件模块 - 处理Streamlit界面组件和布局
import streamlit as st
from .core import AIClient
from .config import CONFIG
from .file_utils import integrate_files_into_content

# 初始化Session State
def init_session_state():
    """
    初始化所有Session State变量
    """
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
    if "saved_api_token" not in st.session_state:
        st.session_state.saved_api_token = CONFIG["token"]
    if "remember_token" not in st.session_state:
        # 如果从CONFIG加载了token，默认记住token
        st.session_state.remember_token = bool(CONFIG["token"])
    if "useFiles" not in st.session_state:
        st.session_state.useFiles = []  # 存储对话中涉及的所有文件

# 渲染侧边栏
def render_sidebar():
    """
    渲染侧边栏组件
    """
    with st.sidebar:
        # 模型选择 - 移动到侧边栏，支持二级分类
        if st.session_state.models and st.session_state.bot:
            # 直接使用模型的value值作为显示文本
            model_values = [model.get("value") for model in st.session_state.models if model.get("value")]
            
            # 获取当前会话信息
            current_session_id = None
            current_session_data = None
            current_session_model = st.session_state.current_session_model
            user_token = st.session_state.get("saved_api_token", CONFIG["token"])
            
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
            
            # 固定模型分类列表，英文全部大写
            fixed_categories = ["GPT", "GEMINI", "CLAUDE", "DEEPSEEK", "SORA", "GLM", "QWEN3", "DOUBAO", "其他"]
            
            # 模型分类逻辑，不区分大小写
            model_categories = {category: [] for category in fixed_categories}
            
            for model in model_values:
                # 转换为小写，方便匹配
                model_lower = model.lower()
                category_assigned = False
                
                # 按固定顺序匹配分类，比较时不区分大小写
                for category in fixed_categories[:-1]:  # 排除"其他"分类
                    # 将分类也转为小写进行比较
                    category_lower = category.lower()
                    if category_lower in model_lower:
                        model_categories[category].append(model)
                        category_assigned = True
                        break
                
                # 如果没有匹配到任何分类，归为"其他"
                if not category_assigned:
                    model_categories["其他"].append(model)
            
            # 初始化分类会话状态
            if "selected_category" not in st.session_state:
                # 默认选择当前模型所在的分类
                current_model_category = "其他"
                for category, models in model_categories.items():
                    if current_session_model in models:
                        current_model_category = category
                        break
                st.session_state.selected_category = current_model_category
            
            # 创建模型选择容器，设置固定高度
            with st.container(height=200):
                # 标题  
                st.subheader("选择模型")
                
                # 一级分类选择 - 第一行，使用非空标签但隐藏
                categories = fixed_categories
                selected_category = st.selectbox(
                    "一级分类",  # 非空标签，用于可访问性
                    options=categories,
                    index=categories.index(st.session_state.selected_category) if st.session_state.selected_category in categories else 0,
                    key="model_category_select",
                    label_visibility="collapsed"  # 隐藏标签
                )
                
                # 更新分类状态
                st.session_state.selected_category = selected_category
                
                # 二级模型选择 - 第二行，使用非空标签但隐藏
                category_models = model_categories[selected_category]
                
                # 确定当前模型在分类中的索引
                current_model_index = 0
                if current_session_model in category_models:
                    current_model_index = category_models.index(current_session_model)
                
                selected_model_value = st.selectbox(
                    "具体模型",  # 非空标签，用于可访问性
                    options=category_models,
                    index=current_model_index,
                    key="model_select",
                    label_visibility="collapsed"  # 隐藏标签
                )
            
            # 如果模型发生变化，更新会话使用的模型
            if selected_model_value != current_session_model and current_session_id and current_session_data:
                # 确保bot实例使用正确的token
                if user_token:
                    st.session_state.bot.token = user_token
                # 更新会话模型（发送PUT请求）
                bot_instance = AIClient(user_token)
                bot_instance.session_id = current_session_id
                success, msg = bot_instance.update_session(current_session_id, {"model": selected_model_value}, current_session_data)
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
        
        # 新建会话按钮
        if st.button("🆕 新建会话", use_container_width=True):
            user_token = st.session_state.get("saved_api_token", CONFIG["token"])
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
                    # 强制刷新界面，确保会话列表更新
                    st.rerun()
                else:
                    st.toast(f"创建新会话失败: {msg}", icon="❌")
        
        # 获取当前会话信息
        current_session_name = "未命名会话"
        current_session_id = None
        current_session_data = None
        user_token = st.session_state.get("saved_api_token", CONFIG["token"])
        
        if st.session_state.bot and st.session_state.bot.session_id:
            # 查找当前会话信息
            for session in st.session_state.sessions:
                if session.get("id") == st.session_state.bot.session_id:
                    current_session_name = session.get("name", "未命名会话")
                    current_session_id = session.get("id")
                    current_session_data = session
                    break
        
        # 修改当前会话名称功能 - 放在一行
        if current_session_id and current_session_data:
            col_name, col_save = st.columns([3, 1])
            with col_name:
                new_name = st.text_input("会话名称", value=current_session_name, key="current_session_name_edit", label_visibility="collapsed")
            with col_save:
                if st.button("💾", key="save_name", use_container_width=True):
                    if new_name and new_name != current_session_name:
                        # 更新会话名称
                        success, msg = st.session_state.bot.update_session(current_session_id, {"name": new_name}, current_session_data)
                        if success:
                            # 更新本地会话列表
                            for i, s in enumerate(st.session_state.sessions):
                                if s.get("id") == current_session_id:
                                    st.session_state.sessions[i]["name"] = new_name
                                    break
                            st.toast(f"会话名称已更新为: {new_name}", icon="✅")
                            # 强制刷新界面，确保会话列表更新
                            st.rerun()
                        else:
                            st.toast(f"更新失败: {msg}", icon="❌")
        
        # 可展开的历史会话
        with st.expander("📜 历史会话", expanded=False):
            if st.session_state.sessions:
                for session in st.session_state.sessions:
                    session_id = session.get("id")
                    session_name = session.get("name", "未命名会话")
                    
                    # 创建会话行，将删除选项与会话名称合并
                    col1, col2 = st.columns([0.8, 0.2])
                    
                    with col1:
                        # 创建会话选择按钮
                        if st.button(f"{session_name}", key=f"session_{session_id}", use_container_width=True):
                            # 检查是否有有效token
                            user_token = st.session_state.get("saved_api_token", CONFIG["token"])
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
                                        for record in reversed(data["records"]):
                                            # 每条记录包含一个完整的对话回合
                                            user_text = record.get("userText")
                                            ai_text = record.get("aiText")
                                            use_files = record.get("useFiles", [])
                                            
                                            # 确保use_files始终是一个可迭代对象
                                            if use_files is None:
                                                use_files = []
                                            
                                            # 添加用户消息
                                            if user_text:
                                                st.session_state.messages.append({
                                                    "role": "user",
                                                    "content": user_text,
                                                    "tokens": record.get("useTokens", 0),
                                                    "files": use_files,
                                                    "file_name": record.get("fileName", "")
                                                })
                                            
                                            # 添加AI回复（不包含文件信息）
                                            if ai_text:
                                                st.session_state.messages.append({
                                                    "role": "assistant",
                                                    "content": ai_text,
                                                    "tokens": record.get("useTokens", 0)
                                                })
                                            
                                            # 同时更新全局useFiles列表，避免重复
                                            for file in use_files:
                                                file_exists = any(existing_file.get("name") == file.get("name") for existing_file in st.session_state.useFiles)
                                                if not file_exists:
                                                    st.session_state.useFiles.append(file)
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
                                        for record in reversed(data["records"]):
                                            # 每条记录包含一个完整的对话回合
                                            user_text = record.get("userText")
                                            ai_text = record.get("aiText")
                                            use_files = record.get("useFiles", [])
                                            
                                            # 确保use_files始终是一个可迭代对象
                                            if use_files is None:
                                                use_files = []
                                            
                                            # 添加用户消息
                                            if user_text:
                                                st.session_state.messages.append({
                                                    "role": "user",
                                                    "content": user_text,
                                                    "tokens": record.get("useTokens", 0),
                                                    "files": use_files,
                                                    "file_name": record.get("fileName", "")
                                                })
                                            
                                            # 添加AI回复（不包含文件信息）
                                            if ai_text:
                                                st.session_state.messages.append({
                                                    "role": "assistant",
                                                    "content": ai_text,
                                                    "tokens": record.get("useTokens", 0)
                                                })
                                            
                                            # 同时更新全局useFiles列表，避免重复
                                            for file in use_files:
                                                file_exists = any(existing_file.get("name") == file.get("name") for existing_file in st.session_state.useFiles)
                                                if not file_exists:
                                                    st.session_state.useFiles.append(file)
                                        st.toast(f"已连接到会话: {session_name}，加载了 {len(data['records'])} 条历史记录", icon="✅")
                                    else:
                                        st.toast(f"已连接到会话: {session_name}，但没有历史记录", icon="✅")
                                else:
                                    st.toast(f"加载历史记录失败: {data}", icon="❌")
                                    st.toast(f"已连接到会话: {session_name}", icon="✅")
                    
                    with col2:
                        # 添加三个点按钮，点击后显示删除选项
                        # 不使用key参数，避免API兼容性问题
                        with st.popover("⋮"):
                            if st.button(f"删除会话", key=f"delete_{session_id}", use_container_width=True, type="secondary"):
                                # 直接执行删除会话逻辑，不再显示确认弹窗
                                user_token = st.session_state.get("saved_api_token", CONFIG["token"])
                                if not user_token:
                                    st.error("请先输入API Token！")
                                else:
                                    # 创建bot实例进行删除操作
                                    bot_instance = AIClient(user_token)
                                    success, msg = bot_instance.delete_session(session_id)
                                    if success:
                                        # 重新加载会话列表
                                        success, data = bot_instance.get_sessions()
                                        if success:
                                            # 更新会话列表
                                            st.session_state.sessions = data
                                            
                                            # 触发侧边栏刷新状态
                                            if "sidebar_refresh" not in st.session_state:
                                                st.session_state.sidebar_refresh = 0
                                            st.session_state.sidebar_refresh += 1
                                            
                                            st.toast(f"已删除会话: {session_name}", icon="✅")
                                            # 刷新界面，确保侧边栏历史会话更新
                                            st.rerun()
                                    else:
                                        st.toast(f"删除会话失败: {msg}", icon="❌")
            else:
                st.info("暂无历史会话")
        
        # 可展开的配置
        with st.expander("⚙️ 配置", expanded=False):
            # API密钥配置区
            # 从session_state获取保存的token，默认使用CONFIG["token"]
            saved_token = st.session_state.get("saved_api_token", CONFIG["token"])
            
            user_token = st.text_input(
                "API Token",
                value=saved_token,
                type="password",
                help="输入您的API令牌",
                key="api_token_input"  # 添加唯一key，避免重复ID错误
            )
            
            # 添加记住token选项
            remember_token = st.checkbox("记住API Token", value=st.session_state.get("remember_token", False))
            
            # 处理token保存逻辑
            token_changed = False
            current_token = st.session_state.get("saved_api_token", CONFIG["token"])
            
            # 检查是否有初始token（从secrets或env var）但尚未保存到session_state
            has_initial_token = CONFIG["token"] and not st.session_state.get("saved_api_token")
            
            if remember_token:
                if st.session_state.get("saved_api_token") != user_token:
                    st.session_state["saved_api_token"] = user_token
                    st.session_state["remember_token"] = True
                    token_changed = True
            else:
                if "saved_api_token" in st.session_state:
                    del st.session_state["saved_api_token"]
                    st.session_state["remember_token"] = False
                    token_changed = True
                    # 取消记住时，使用空token
                    user_token = ""
            
            # 如果有初始token但尚未处理，触发token变化
            if has_initial_token and not token_changed:
                token_changed = True
                user_token = CONFIG["token"]
                st.session_state["saved_api_token"] = user_token
                st.session_state["remember_token"] = True
            
            # 处理会话列表逻辑
            if user_token:
                # 有token时的逻辑
                if token_changed:
                    # 只有在token实际发生变化时，才重新加载会话列表
                    bot_instance = AIClient(user_token)
                    
                    # 始终重新加载会话列表，确保使用最新token获取的会话
                    success, data = bot_instance.get_sessions()
                    if success:
                        # 更新历史会话列表
                        st.session_state.sessions = data
                        st.toast(f"已加载 {len(data)} 个会话", icon="✅")
                        
                        # 如果有会话
                        if data:
                            current_session_id = None
                            current_session_name = "未命名会话"
                            current_session_data = None
                            
                            # 如果当前已有会话，使用相同ID
                            if st.session_state.bot and st.session_state.bot.session_id:
                                # 检查当前会话ID是否在新的会话列表中
                                for session in data:
                                    if session.get("id") == st.session_state.bot.session_id:
                                        current_session_id = session.get("id")
                                        current_session_name = session.get("name", "未命名会话")
                                        current_session_data = session
                                        break
                            
                            # 如果当前会话不存在或没有会话，使用最新会话
                            if not current_session_id:
                                # 根据创建时间排序，取最新的会话
                                recent_session = max(data, key=lambda x: x.get('created', ''))
                                current_session_id = recent_session.get('id')
                                current_session_name = recent_session.get('name', '未命名会话')
                                current_session_data = recent_session
                            
                            # 设置当前会话ID
                            bot_instance.session_id = current_session_id
                            st.session_state.bot = bot_instance
                            
                            # 自动选择当前会话的模型
                            session_model = next((s.get("model") for s in data if s.get("id") == current_session_id), "gemini-3-pro-preview")
                            st.session_state.selected_model = session_model
                            st.session_state.current_session_model = session_model
                            
                            st.session_state.status = f"✅ 已连接到会话: {current_session_name}"
                            
                            # 加载该会话的历史聊天记录
                            success, records_data = st.session_state.bot.get_chat_records(current_session_id)
                            if success and records_data.get("records"):
                                # 清空当前消息列表，重新加载历史记录
                                st.session_state.messages = []
                                # 将历史记录转换为消息格式
                                for record in reversed(records_data["records"]):
                                    user_text = record.get("userText")
                                    ai_text = record.get("aiText")
                                    use_files = record.get("useFiles", [])
                                    
                                    # 确保use_files始终是一个可迭代对象，即使record.get返回None
                                    if use_files is None:
                                        use_files = []
                                    
                                    if user_text:
                                        st.session_state.messages.append({
                                            "role": "user",
                                            "content": user_text,
                                            "tokens": record.get("useTokens", 0),
                                            "files": use_files,  # 添加历史记录中的文件信息
                                            "file_name": record.get("fileName", "")  # 兼容旧的文件名记录
                                        })
                                    if ai_text:
                                        st.session_state.messages.append({
                                            "role": "assistant",
                                            "content": ai_text,
                                            "tokens": record.get("useTokens", 0)
                                        })
                                    
                                    # 同时更新全局useFiles列表，避免重复
                                    for file in use_files:
                                        file_exists = any(existing_file.get("name") == file.get("name") for existing_file in st.session_state.useFiles)
                                        if not file_exists:
                                            st.session_state.useFiles.append(file)
                                st.toast(f"已更新会话历史记录", icon="✅")
                        
                        # 强制刷新侧边栏，确保历史会话列表更新
                        # 这里通过更新一个状态变量来触发重新渲染
                        if "sidebar_refresh" not in st.session_state:
                            st.session_state.sidebar_refresh = 0
                        st.session_state.sidebar_refresh += 1
                        
                        # 刷新历史会话的会话状态
                        st.rerun()
                    else:
                        st.info("暂无历史会话")
                else:
                    # 没有token变化时，不需要显示加载失败消息
                    pass
            else:
                # 没有token时，只重置机器人实例和状态，不清空会话列表
                st.session_state.bot = None
                st.session_state.messages = []
                st.session_state.status = "未连接"
            
            # 初始化会话状态中的对话参数
            if "chat_params" not in st.session_state:
                st.session_state.chat_params = {
                    "contextCount": CONFIG["contextCount"],
                    "prompt": CONFIG["prompt"],
                    "temperature": float(CONFIG["temperature"])
                }
            
            # 上下文数量
            st.session_state.chat_params["contextCount"] = st.slider(
                "上下文数量",
                min_value=1,
                max_value=100,
                value=int(st.session_state.chat_params["contextCount"]),
                help="控制对话中使用的历史上下文数量"
            )
            
            # 系统提示词
            st.session_state.chat_params["prompt"] = st.text_area(
                "系统提示词",
                value=st.session_state.chat_params["prompt"],
                height=100,
                help="AI的系统提示词，指导AI的回复风格和行为"
            )
            
            # 温度参数
            st.session_state.chat_params["temperature"] = st.slider(
                "温度",
                min_value=0.0,
                max_value=1.0,
                step=0.1,
                value=float(st.session_state.chat_params["temperature"]),
                help="控制AI回复的随机性，值越高越随机"
            )
            
            # 保存对话参数到配置
            if st.button("保存对话参数", use_container_width=True):
                # 更新CONFIG中的对话参数
                CONFIG["contextCount"] = st.session_state.chat_params["contextCount"]
                CONFIG["prompt"] = st.session_state.chat_params["prompt"]
                CONFIG["temperature"] = st.session_state.chat_params["temperature"]
                st.toast("对话参数已保存", icon="✅")

# 渲染聊天区域
def render_chat_area():
    """
    渲染聊天区域组件
    """
    # 添加CSS样式定制用户对话框背景颜色、代码块高度和样式、输入框样式、侧边栏样式
    st.markdown("""
    <style>
    /* 设置代码块样式 */
    .stMarkdown pre {
        max-height: 300px;
        overflow-y: auto;
        background-color: #181818 !important;
    }
    /* 设置代码块内文本颜色 */
    .stMarkdown code {
        background-color: #181818 !important;
    }
    /* 设置聊天输入框字体大小，比默认大一号 */
    [data-testid='stChatInput'] textarea {
        font-size: 1.2rem !important;
        border-radius: 0.5rem !important;
    }
    /* 设置聊天输入框组件的圆角 - 全面覆盖所有容器 */

    [data-testid='stChatInput'] > div:first-child {
        border-radius: 0.8rem !important;
        overflow: hidden !important;
        min-height: 8rem !important;
    }
    [data-testid='stChatInput'] > div > div {
        border-radius: 0.8rem !important;
        overflow: hidden !important;
    }
    [data-testid='stChatInput'] [data-testid='stFileUploadDropzone'] {
        border-radius: 0.8rem !important;
    }
    /* 设置聊天输入框按钮的圆角 */
    [data-testid='stChatInput'] .stButton > button {
        border-radius: 0.8rem !important;
    }
    /* 移除侧边栏所有元素的边缘线条 */
    [data-testid='stSidebar'] * {
        border: none !important;
        box-shadow: none !important;
        outline: none !important;
    }
    /* 移除侧边栏选择框的边框 */
    [data-testid='stSidebar'] .stSelectbox {
        border: none !important;
    }
    /* 移除侧边栏按钮的边框 */
    [data-testid='stSidebar'] .stButton > button {
        border: none !important;
    }
    /* 移除侧边栏文本输入框的边框 */
    [data-testid='stSidebar'] .stTextInput > div > div > input {
        border: none !important;
    }
    /* 移除侧边栏展开器的边框 */
    [data-testid='stSidebar'] .stExpander {
        border: none !important;
    }
    /* 移除侧边栏容器的边框 */
    [data-testid='stSidebar'] .stContainer {
        border: none !important;
    }
    
    /* 设置人类输入文本的样式 */
    /* 根据实际DOM结构，使用aria-label识别用户消息 */
    [data-testid="stChatMessage"]:has([aria-label="Chat message from user"]) {
        background-color: #2F2F2F !important;
        /* 靠右显示，宽度不超过2/3 */
        margin-left: auto !important;
        margin-right: 0 !important;
        max-width: 66.67% !important;
        /* 内部文本保持左对齐 */
        text-align: left !important;
        /* 头像靠右显示 - 使用flex布局反转 */
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
    """, unsafe_allow_html=True)
    
    # 渲染历史聊天记录
    if not st.session_state.messages:
        # 空状态提示
        st.info("请在下方输入您的问题开始对话。")
    else:
        # 使用容器渲染聊天记录，优化滚动性能
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.messages:
                # 区分用户和AI的样式
                avatar = " " if message["role"] == "user" else " "
                
                # 显示消息内容
                with st.chat_message(message["role"]):
                    if message["role"] == "user":
                        # 用户消息实现：显示部分内容+点击展开，超过50行时展开
                        content = message["content"]
                        
                        # 使用file_utils模块格式化文件附件
                        from .file_utils import format_file_attachments
                        file_html = format_file_attachments(
                            message.get("files", []),
                            message.get("file_name"),
                            message.get("file_url")
                        )
                        
                        # 如果有文件附件，使用HTML显示
                        if file_html:
                            st.markdown(file_html, unsafe_allow_html=True)
                            # 添加换行
                            st.markdown("\n\n")
                        
                        # 定义显示的初始行数
                        initial_lines = 50
                        lines = content.split('\n')
                        
                        if len(lines) > initial_lines:
                            # 显示前面的部分内容
                            initial_content = '\n'.join(lines[:initial_lines])
                            
                            # 显示初始内容，使用st.text避免markdown渲染
                            st.text(initial_content)
                            
                            # 使用st.expander实现点击展开
                            with st.expander("... 展开查看完整消息"):
                                # 显示完整消息，使用st.text避免markdown渲染
                                st.text(content)
                        else:
                            # 短消息直接显示，使用st.text避免markdown渲染
                            st.text(content)
                    else:
                        # AI消息使用默认样式
                        # 处理AI回复，折叠<think>内容
                        from .utils import process_ai_content
                        main_content, think_content, _ = process_ai_content(message["content"])
                        
                        # 如果有思考内容，使用折叠面板显示
                        if think_content:
                            with st.expander("查看思考过程"):
                                st.markdown(think_content)
                        
                        # 显示主要内容 - 不限制高度
                        if main_content:
                            st.markdown(main_content)
                
                # 只在最新机器回复下方展示use tokens
                if message["role"] == "assistant" and message == st.session_state.messages[-1]:
                    # 显示tokens使用信息
                    use_tokens = message.get("tokens", 0)
                    st.caption(f"💡 使用tokens: {use_tokens}")
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
            from .file_utils import format_file_attachments
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
            # 使用占位符实现流式响应
            response_container = st.container()
            full_response = ""
            
            # 迭代流式响应
            for chunk in st.session_state.bot.chat_stream(prompt, uploaded_file):
                full_response += chunk
                
                # 清除之前的所有内容
                response_container.empty()
                
                # 在容器中处理和显示内容
                with response_container:
                    # 处理AI回复，折叠<think>内容
                    from .utils import process_ai_content
                    main_content, think_content, is_thinking = process_ai_content(full_response)
                    
                    # 显示思考过程（如果有）
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
        st.caption(f"💡 使用tokens: {tokens_used}")
        
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

# 自动加载模型列表和会话
def auto_load_data():
    """
    自动加载模型列表和会话
    """
    # 检查并处理初始token
    def process_initial_token():
        """
        检查并处理初始token
        """
        # 检查是否有初始token（从secrets或env var）但尚未保存到session_state
        has_initial_token = CONFIG["token"] and not st.session_state.get("saved_api_token")
        
        if has_initial_token:
            # 保存初始token到session_state
            st.session_state["saved_api_token"] = CONFIG["token"]
            st.session_state["remember_token"] = True
            return True
        return False
    
    # 处理初始token
    token_processed = process_initial_token()
    
    # 自动加载模型列表
    if not st.session_state.models:
        bot_instance = AIClient(st.session_state.get("saved_api_token", CONFIG["token"]))
        success, data = bot_instance.get_model_list()
        if success:
            st.session_state.models = data.get("models", [])
            # 始终默认使用gemini的preview模型
            st.session_state.selected_model = "gemini-3-pro-preview"
            st.session_state.current_session_model = "gemini-3-pro-preview"

    # 自动加载会话列表并打开最近一次对话
    # 只有在会话列表为空时才加载，避免无限循环
    if not st.session_state.sessions or token_processed:  # 当token被处理时，强制加载会话列表
        bot_instance = AIClient(st.session_state.get("saved_api_token", CONFIG["token"]))
        success, data = bot_instance.get_sessions()
        if success:
            # 始终更新会话列表
            st.session_state.sessions = data
            if data:
                st.toast(f"已加载 {len(data)} 个会话", icon="✅")
                
                # 只有在没有bot实例时，才初始化bot和会话
                if not st.session_state.bot:
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
                    
                    # 只有在消息列表为空时，才加载历史聊天记录
                    if not st.session_state.messages:
                        # 加载该会话的历史聊天记录
                        success, records_data = st.session_state.bot.get_chat_records(session_id)
                        if success and records_data.get("records"):
                            # 将历史记录转换为消息格式
                            for record in reversed(records_data["records"]):
                                user_text = record.get("userText")
                                ai_text = record.get("aiText")
                                
                                if user_text:
                                    st.session_state.messages.append({
                                        "role": "user",
                                        "content": user_text,
                                        "tokens": record.get("useTokens", 0)
                                    })
                                if ai_text:
                                    st.session_state.messages.append({
                                        "role": "assistant",
                                        "content": ai_text,
                                        "tokens": record.get("useTokens", 0)
                                    })
            else:
                # 会话列表为空时，初始化bot
                if not st.session_state.bot:
                    st.session_state.bot = bot_instance
        # 移除自动加载时的st.rerun()，避免无限循环
