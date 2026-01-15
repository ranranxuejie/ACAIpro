import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import json
import time
import requests
import base64

# ==========================================
# 1. 这里填入你的配置 (或者保留你原本的 import)
# ==========================================
CONFIG = {
    "base_url": "https://achuanai.vip/api", # 假设的基础URL，请确认是否正确
    "contextCount": 5,
    "frequencyPenalty": 0,
    "maxToken": 10000000,
    "presencePenalty": 0,
    "prompt": "",
    "temperature": 0.5,
    "topSort": 0
}

# 填入你的 Token
MY_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjEwMTI4LCJzaWduIjoiNGEwMTE3MmI3MjU3NzIxNDk3ODZiMTQ3N2Q2MmQ4ZjQiLCJyb2xlIjoidXNlciIsImV4cCI6MTc2OTQ3OTI2MCwibmJmIjoxNzY2ODAwODYwLCJpYXQiOjE3NjY4MDA4NjB9.bvYZUkuc_RBkJdyFEYQqRA7mw1Zlv3LeNnMz20ZJZCk" 

# ==========================================
# 2. 你的 AIClient 类 (精简版，适配桥接)
# ==========================================
class AIClient:
    def __init__(self, token):
        self.token = token
        self.headers = {
            "Authorization": token,
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0",
            "Origin": "https://achuanai.vip",
            "Referer": "https://achuanai.vip/chat",
            "x-app-version": "2.14.0"
        }
        self.base_url = CONFIG["base_url"]

    def create_session(self, model="gemini-1.5-pro"):
        url = f"{self.base_url}/chat/session"
        payload = {
            "model": model,
            "contextCount": CONFIG["contextCount"],
            "maxToken": CONFIG["maxToken"],
            "temperature": CONFIG["temperature"],
            "topSort": CONFIG["topSort"]
        }
        try:
            res = requests.post(url, headers=self.headers, json=payload).json()
            if res.get("code") == 0:
                return res['data']['id']
        except:
            pass
        return None

    def chat_stream(self, session_id, user_text):
        url = f"{self.base_url}/chat/completions"
        payload = {
            "sessionId": session_id,
            "text": user_text,
            "files": [],
            # 其他参数...
        }

        # 模拟 OpenAI 的流式响应格式
        try:
            with requests.post(url, headers=self.headers, json=payload, stream=True) as response:
                for line in response.iter_lines():
                    if line:
                        decoded_line = line.decode('utf-8')
                        if decoded_line.startswith("data:"):
                            json_str = decoded_line[5:].strip()
                            if json_str == "[DONE]": break
                            try:
                                data_obj = json.loads(json_str)
                                if isinstance(data_obj, dict) and data_obj.get("type") == "string":
                                    content = data_obj.get("data", "")
                                    # 转换为 OpenAI 格式
                                    yield f"data: {json.dumps({'choices': [{'delta': {'content': content}}]})}\n\n"
                            except:
                                continue
        except Exception as e:
            err_msg = str(e)
            yield f"data: {json.dumps({'choices': [{'delta': {'content': err_msg}}]})}\n\n"

        yield "data: [DONE]\n\n"

# ==========================================
# 3. FastAPI 服务 (标准 OpenAI 接口伪装)
# ==========================================
app = FastAPI()
client = AIClient(MY_TOKEN)

@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    data = await request.json()

    # 获取用户发送的内容
    messages = data.get("messages", [])
    last_user_msg = messages[-1]["content"] if messages else "Hello"
    model = data.get("model", "gemini-1.5-pro")

    # 1. 创建会话 (每次请求创建一个新会话，或者你可以做缓存)
    session_id = client.create_session(model=model)

    if not session_id:
        return {"error": "Failed to create session"}

    # 2. 如果有上下文历史，可能需要先发给服务器(略)，这里直接发最后一句
    # 简单的实现只发最后一句，复杂的实现需要循环发送 history

    return StreamingResponse(
        client.chat_stream(session_id, last_user_msg), 
        media_type="text/event-stream"
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)