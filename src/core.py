# 核心业务逻辑模块 - 处理AI客户端和API调用
import requests
import json
import base64
from .config import CONFIG

class AIClient:
    """
    AI客户端类，处理与API的交互
    """
    def __init__(self, token):
        """
        初始化AI客户端
        
        Args:
            token (str): API访问令牌
        """
        self.token = token
        self.session_id = None
        self.base_url = CONFIG["base_url"]
        self.headers = {
            "Authorization": token,
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
        更新会话信息（名称或模型）
        
        Args:
            session_id (str): 会话ID
            update_data (dict): 要更新的数据
            session_data (dict): 当前会话数据
            
        Returns:
            tuple: (成功状态, 消息)
        """
        url = f"{self.base_url}/chat/session/{session_id}"
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

    def chat_stream(self, user_text, file_obj=None):
        """
        流式聊天生成器
        
        Args:
            user_text (str): 用户输入文本
            file_obj: 文件对象
            
        Yields:
            str: 流式生成的文本块
        """
        if not self.session_id:
            yield "⚠️ 会话未连接，请先创建或选择会话！"
            return

        # 初始化tokens信息
        self.last_tokens_used = 0

        url = f"{self.base_url}/chat/completions"

        files_data = []
        if file_obj:
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
                            # 检查是否包含 "type":"string"，只保留 string 类型的内容
                            if isinstance(data_obj, dict) and data_obj.get("type") == "string":
                                content = data_obj.get("data", "")
                                yield content
                            # 检查是否包含object类型数据，从中提取completionTokens
                            elif isinstance(data_obj, dict) and data_obj.get("type") == "object":
                                # 保存tokens信息
                                data = data_obj.get("data", {})
                                # 优先使用completionTokens
                                self.last_tokens_used = data.get("completionTokens", 0)
                                # 保存完整数据，用于调试
                                self.last_api_response = data_obj
                            # 检查是否包含stats类型数据，保持兼容
                            elif isinstance(data_obj, dict) and data_obj.get("type") == "stats":
                                # 保存tokens信息
                                self.last_tokens_used = data_obj.get("data", {}).get("totalToken", 0)
                        except:
                            continue
        except Exception as e:
            yield f"❌ 网络请求错误: {e}"
