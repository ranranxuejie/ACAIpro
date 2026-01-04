# 侧边栏模块 - 处理侧边栏组件
import streamlit as st
from .core import AIClient
from .config import CONFIG

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
                                                    "tokens": record.get("completionTokens", 0),
                                                    "files": use_files,
                                                    "file_name": record.get("fileName", "")
                                                })
                                            
                                            # 添加AI回复（不包含文件信息）
                                            if ai_text:
                                                st.session_state.messages.append({
                                                    "role": "assistant",
                                                    "content": ai_text,
                                                    "tokens": record.get("completionTokens", 0)
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
                                                    "tokens": record.get("completionTokens", 0),
                                                    "files": use_files,
                                                    "file_name": record.get("fileName", "")
                                                })
                                            
                                            # 添加AI回复（不包含文件信息）
                                            if ai_text:
                                                st.session_state.messages.append({
                                                    "role": "assistant",
                                                    "content": ai_text,
                                                    "tokens": record.get("completionTokens", 0)
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
                                            "tokens": record.get("completionTokens", 0),
                                            "files": use_files,  # 添加历史记录中的文件信息
                                            "file_name": record.get("fileName", "")  # 兼容旧的文件名记录
                                        })
                                    if ai_text:
                                        st.session_state.messages.append({
                                            "role": "assistant",
                                            "content": ai_text,
                                            "tokens": record.get("completionTokens", 0)
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
                
                # 发送PUT请求到API更新会话参数
                if st.session_state.bot and st.session_state.bot.session_id:
                    import requests
                    
                    # 构建请求URL
                    session_id = st.session_state.bot.session_id
                    url = f"{CONFIG['base_url']}/chat/session/{session_id}"
                    
                    # 构建完整的请求负载，包含所有必要字段
                    payload = {
                        "id": int(session_id),
                        "name": "新对话",  # 暂时使用默认名称
                        "model": st.session_state.selected_model,
                        "contextCount": st.session_state.chat_params["contextCount"],
                        "temperature": st.session_state.chat_params["temperature"],
                        "prompt": st.session_state.chat_params["prompt"],
                        "presencePenalty": CONFIG["presencePenalty"],
                        "frequencyPenalty": CONFIG["frequencyPenalty"],
                        "maxToken": CONFIG["maxToken"],
                        "topSort": CONFIG["topSort"],
                        "plugins": [],
                        "mcp": [],
                        "icon": "",
                        "useAppId": 0
                    }
                    
                    # 获取当前bot的headers
                    headers = st.session_state.bot.headers
                    
                    try:
                        # 发送PUT请求
                        response = requests.put(url, headers=headers, json=payload)
                        if response.status_code == 200:
                            st.toast("对话参数已保存", icon="✅")
                        else:
                            st.toast(f"保存失败: {response.status_code}", icon="❌")
                    except Exception as e:
                        st.toast(f"保存失败: {str(e)}", icon="❌")
                else:
                    st.toast("请先连接会话", icon="❌")
