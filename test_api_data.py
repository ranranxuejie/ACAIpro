# 测试API返回的数据结构
import sys
import os

# 将src目录添加到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from core import AIClient

# 测试get_chat_records方法返回的数据结构
def test_api_data():
    # 使用测试token
    user_token = "your_test_token_here"
    bot = AIClient(user_token)
    
    # 使用测试会话ID
    test_session_id = "your_test_session_id_here"
    
    # 调用API获取聊天记录
    success, data = bot.get_chat_records(test_session_id)
    
    if success:
        print("API返回数据:")
        import json
        print(json.dumps(data, ensure_ascii=False, indent=2))
        
        if data.get("records"):
            print("\n第一条记录的结构:")
            print(json.dumps(data["records"][0], ensure_ascii=False, indent=2))
    else:
        print(f"API调用失败: {data}")

if __name__ == "__main__":
    test_api_data()
