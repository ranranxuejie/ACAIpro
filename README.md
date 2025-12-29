# 然然 AI - Achuan AI 客户端

一个基于 Streamlit 构建的 AI 聊天客户端，支持 Achuan AI API。

## 功能特性

- ✨ 会话管理：创建、切换、重命名会话
- 🤖 模型选择：支持多种 AI 模型切换
- 📎 文件上传：支持拖入上传文件
- 💬 流式响应：实时显示 AI 回复
- 📝 历史记录：自动保存和加载会话记录
- 🔒 安全配置：支持从环境变量读取 API 密钥

## 部署方式

### 1. 克隆仓库

```bash
git clone https://github.com/your-username/achuan-ai-client.git
cd achuan-ai-client
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置 API 密钥

#### 方式一：环境变量（推荐）

在部署环境中设置环境变量：

```bash
# Linux/Mac
export ACHUAN_AI_TOKEN="your-api-token"

# Windows PowerShell
$env:ACHUAN_AI_TOKEN="your-api-token"

# Windows CMD
set ACHUAN_AI_TOKEN=your-api-token
```

#### 方式二：应用内配置

启动应用后，在侧边栏的"配置"部分输入 API Token。

### 4. 启动应用

```bash
streamlit run app.py
```

## 在线部署

### Vercel 部署

1. Fork 本仓库到你的 GitHub 账户
2. 在 Vercel 中导入你的仓库
3. 在 Vercel 项目设置中添加环境变量：
   - 名称：`ACHUAN_AI_TOKEN`
   - 值：你的 Achuan AI API 密钥
4. 部署完成后访问应用 URL

### Streamlit Cloud 部署

1. Fork 本仓库到你的 GitHub 账户
2. 登录 [Streamlit Cloud](https://streamlit.io/cloud)
3. 点击"New app"按钮
4. 选择你的仓库和分支
5. 在"Advanced settings"中添加环境变量：
   - 名称：`ACHUAN_AI_TOKEN`
   - 值：你的 Achuan AI API 密钥
6. 部署并访问应用

## 项目结构

```
├── app.py              # 主应用文件
├── requirements.txt    # 依赖列表
├── .gitignore         # Git 忽略文件
└── README.md          # 项目说明
```

## 依赖列表

- streamlit
- requests
- python-dotenv

## 安全注意事项

1. 🔒 **不要**将 API 密钥硬编码到代码中
2. 🔒 **不要**将 `.env` 文件上传到 GitHub
3. 🔒 使用环境变量或应用内配置来管理敏感信息
4. 🔒 定期更新你的 API 密钥

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 更新日志

### v1.0.0
- 初始版本
- 支持会话管理
- 支持模型选择
- 支持文件上传
- 支持流式响应
- 支持环境变量配置