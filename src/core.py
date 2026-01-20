# 核心业务逻辑模块 - 处理AI客户端和API调用
import requests
import json
import base64
from .config import CONFIG

class AIClient:
    """
    AI客户端类，处理与API的交互
    """
    def __init__(self, authorization):
        self.authorization = authorization
        self.session_id = None
        self.base_url = CONFIG["base_url"]
        # 新增：用于存储最后一次对话的完整元数据（时间、Tokens等）
        self.last_chat_metadata = {}
        self.last_tokens_used = 0
        self.headers = {
            "Authorization": authorization,
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0",
            "Origin": "https://achuanai.vip",
            "Referer": "https://achuanai.vip/chat",
            "x-app-version": "2.14.0",
            "priority": "u=1, i",
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "Sec-Ch-Ua": '"Microsoft Edge";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin"
        }

    def create_session(self, model="gemini-3-pro-preview"):
        """
        创建新会话
        
        Args:
            model (str): 要使用的模型名称
            
        Returns:
            tuple: (成功状态, 消息或会话ID)
        """

        url = f"{self.base_url}/chat/session"
        payload = {
            "model": model, 
            "plugins": [], 
            "mcp": [],
            "contextCount": CONFIG["contextCount"],
            "frequencyPenalty": CONFIG["frequencyPenalty"],
            "maxToken": CONFIG["maxToken"],
            "presencePenalty": CONFIG["presencePenalty"],
            "prompt": CONFIG["prompt"],
            "temperature": CONFIG["temperature"],
            "topSort": CONFIG["topSort"]
        }
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            if response.status_code == 200:
                res_json = response.json()
                if res_json.get("code") == 0:
                    self.session_id = res_json['data']['id']
                    return True, str(self.session_id)
                else:
                    return False, res_json.get('msg')
            return False, f"HTTP {response.status_code}"
        except Exception as e:
            return False, str(e)

    def process_streamlit_file(self, uploaded_file):
        """
        处理Streamlit上传的文件，转换为API需要的格式
        
        Args:
            uploaded_file: Streamlit上传文件对象
            
        Returns:
            dict or None: 处理后的文件数据，或None（如果处理失败）
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

            # 构造API需要的格式
            return {
                "name": filename,
                "data": f"data:application/{ext};base64,{encoded}"
            }
        except Exception as e:
            return None

    def get_sessions(self):
        """
        获取历史会话列表
        
        Returns:
            tuple: (成功状态, 会话列表或错误消息)
        """
        url = f"{self.base_url}/chat/session"
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
        
        Args:
            session_id (str): 会话ID
            page (int): 页码
            
        Returns:
            tuple: (成功状态, 聊天记录或错误消息)
        """
        url = f"{self.base_url}/chat/record/{session_id}?page={page}"
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
        更新会话信息（名称、置顶状态等）

        Args:
            session_id (str): 会话ID
            update_data (dict): 要更新的数据（如 {"name": "新名称"}）
            session_data (dict): 当前会话的完整原始数据

        Returns:
            tuple: (成功状态, 消息)
        """
        url = f"{self.base_url}/chat/session/{session_id}"
        try:
            # 1. 以当前会话数据为基础，保留 id, created, model, uid 等字段
            payload = session_data.copy()

            # 2. 根据需求：生成参数以 CONFIG 全局配置为准
            # 强制同步以下字段，防止前端使用了旧的配置
            config_sync_keys = [
                "contextCount", 
                "frequencyPenalty", 
                "maxToken", 
                "presencePenalty", 
                "prompt", 
                "temperature"
            ]

            for key in config_sync_keys:
                if key in CONFIG:
                    payload[key] = CONFIG[key]

            # 3. 应用本次明确的更新 (例如 name, topSort)
            # 这会覆盖掉上面的 Config 值（如果 update_data 里也有的话），也会覆盖掉旧的 session_data
            payload.update(update_data)

            # 发送 PUT 请求
            response = requests.put(url, headers=self.headers, json=payload)

            if response.status_code == 200:
                res_json = response.json()
                if res_json.get("code") == 0:
                    return True, "会话信息更新成功"
                else:
                    return False, res_json.get('msg', '更新失败')
            return False, f"HTTP {response.status_code}"

        except Exception as e:
            return False, str(e)

    def toggle_session_pin(self, session_data):
        """
        [新增] 切换会话置顶状态
        Args:
            session_data (dict): 当前会话的完整数据
        """
        current_sort = session_data.get("topSort", 0)
        # 如果当前是1，则设为0；否则设为1
        new_sort = 0 if current_sort == 1 else 1

        return self.update_session(
            session_data["id"], 
            {"topSort": new_sort}, 
            session_data
        )

    def get_model_list(self):
        """
        获取所有可选模型
        
        Returns:
            tuple: (成功状态, 模型列表或错误消息)
        """
        url = f"{self.base_url}/chat/tmpl"
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
    
    def delete_session(self, session_id):
        """
        删除指定会话
        
        Args:
            session_id (str): 要删除的会话ID
            
        Returns:
            tuple: (成功状态, 消息)
        """
        url = f"{self.base_url}/chat/session/{session_id}"
        try:
            response = requests.delete(url, headers=self.headers)
            if response.status_code == 200:
                res_json = response.json()
                if res_json.get("code") == 0:
                    return True, "会话删除成功"
                else:
                    return False, res_json.get('msg')
            return False, f"HTTP {response.status_code}"
        except Exception as e:
            return False, str(e)
    
    def delete_chat_record(self, cid, sid, task_id=""):
        """
        删除指定的聊天记录
        
        Args:
            cid (str): 聊天记录ID
            sid (str): 会话ID
            task_id (str, optional): 任务ID
            
        Returns:
            tuple: (成功状态, 消息)
        """
        # 构建请求URL
        url = f"{self.base_url}/chat/record?cid={cid}&sid={sid}"
        if task_id:
            url += f"&taskId={task_id}"
        
        try:
            response = requests.delete(url, headers=self.headers)
            if response.status_code == 200:
                # 检查API返回的JSON格式
                try:
                    res_json = response.json()
                    if res_json.get("code") == 0:
                        return True, "聊天记录删除成功"
                    else:
                        return False, res_json.get('msg', "删除失败")
                except json.JSONDecodeError:
                    # 如果返回的不是JSON格式，可能是直接返回成功信息
                    return True, "聊天记录删除成功"
            return False, f"HTTP {response.status_code}"
        except Exception as e:
            return False, str(e)

    def chat_stream(self, user_text, file_obj=None):
        """
        流式聊天生成器
        """
        if not self.session_id:
            yield "⚠️ 会话未连接，请先创建或选择会话！"
            return

        # 重置元数据
        self.last_tokens_used = 0
        self.last_chat_metadata = {} # 初始化为空字典

        url = f"{self.base_url}/chat/completions"

        files_data = []
        if file_obj:
            # 支持单个文件或多个文件
            if isinstance(file_obj, list):
                # 处理多个文件
                for uploaded_file in file_obj:
                    processed_file = self.process_streamlit_file(uploaded_file)
                    if processed_file:
                        files_data.append(processed_file)
            else:
                # 处理单个文件
                processed_file = self.process_streamlit_file(file_obj)
                if processed_file:
                    files_data.append(processed_file)

        payload = {
            "sessionId": self.session_id,
            "text": user_text,
            "files": files_data,
            "contextCount": CONFIG["contextCount"],
            "frequencyPenalty": CONFIG["frequencyPenalty"],
            "maxToken": CONFIG["maxToken"],
            "presencePenalty": CONFIG["presencePenalty"],
            "prompt": CONFIG["prompt"],
            "temperature": CONFIG["temperature"],
            "topSort": CONFIG["topSort"]
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
                            
                            # 1. 处理字符串内容 (流式文本)
                            if isinstance(data_obj, dict) and data_obj.get("type") == "string":
                                content = data_obj.get("data", "")
                                yield content
                                
                            # 2. 处理对象元数据 (API返回的最终统计信息)
                            elif isinstance(data_obj, dict) and data_obj.get("type") == "object":
                                # data 结构示例: {"id":..., "created":"...", "updated":"...", "completionTokens":...}
                                data = data_obj.get("data", {})
                                
                                # 保存完整元数据到实例变量，供外部读取
                                self.last_chat_metadata = data
                                
                                # 为了兼容旧逻辑，更新 tokens
                                self.last_tokens_used = data.get("completionTokens", 0)
                                
                            # 3. 处理 stats 类型 (兼容性)
                            elif isinstance(data_obj, dict) and data_obj.get("type") == "stats":
                                self.last_tokens_used = data_obj.get("data", {}).get("totalToken", 0)
                                
                        except Exception:
                            continue
        except Exception as e:
            yield f"❌ 网络请求错误: {e}"