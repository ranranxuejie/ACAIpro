# Streamlit Secrets 配置指南

本文档详细说明如何配置 Streamlit Secrets，让应用优先从 Secrets 中读取 API 密钥，适合本地开发和部署环境。

## 一、本地开发环境配置

### 1. 创建 Secrets 文件

在项目根目录下创建 `.streamlit` 文件夹，然后在其中创建 `secrets.toml` 文件：

```bash
mkdir -p .streamlit
notepad .streamlit/secrets.toml
```

### 2. 配置 Secrets 内容

在 `secrets.toml` 文件中添加以下内容：

```toml
[achuan_ai]
token = "your-api-token-here"
base_url = "https://achuanai.vip/api"
```

将 `your-api-token-here` 替换为您的 Achuan AI API 密钥。

### 3. 验证配置

启动应用后，应用会自动从 Secrets 中读取配置，无需手动输入 API Token。

## 二、部署环境配置

### Streamlit Cloud 部署

1. 登录 [Streamlit Cloud](https://streamlit.io/cloud)
2. 创建新应用或进入现有应用
3. 点击右侧菜单栏的 "⚙️ Settings"
4. 在 "Secrets" 选项卡中，添加以下内容：
   ```toml
   [achuan_ai]
   token = "your-api-token-here"
   base_url = "https://achuanai.vip/api"
   ```
5. 点击 "Save" 保存配置
6. 重新部署应用

### Vercel 部署

1. 登录 Vercel
2. 进入项目设置
3. 在 "Environment Variables" 中添加：
   - 键：`STREAMLIT_ACHUAN_AI_TOKEN`
   - 值：`your-api-token-here`
4. 保存并重新部署

### 其他部署平台

对于其他部署平台，您可以：
1. 使用环境变量 `ACHUAN_AI_TOKEN` 设置 API 密钥
2. 或按照平台文档配置类似的 Secrets 功能

## 三、配置优先级

应用会按照以下优先级读取配置：

1. **Streamlit Secrets**：最高优先级，适合部署环境
2. **环境变量**：次之，适合本地开发
3. **会话记忆**：用户勾选 "记住API Token" 时保存
4. **手动输入**：用户每次输入的 Token
5. **默认值**：空字符串

## 四、注意事项

1. **安全性**：不要将 `secrets.toml` 文件提交到 GitHub，确保它已被 `.gitignore` 忽略
2. **隐私保护**：API 密钥是敏感信息，不要分享给他人
3. **定期更新**：建议定期更新 API 密钥，提高安全性
4. **本地调试**：本地开发时，可以先使用手动输入方式验证功能，再配置 Secrets

## 五、验证配置是否生效

启动应用后，如果看到以下情况，说明 Secrets 配置已生效：

1. API Token 输入框中自动填充了密钥（显示为******）
2. 不需要手动输入密钥即可使用应用
3. 会话列表正常加载

## 六、常见问题

### Q: Secrets 配置不生效怎么办？

A: 检查以下几点：
1. 确认 `secrets.toml` 文件路径正确（`.streamlit/secrets.toml`）
2. 确认配置格式正确，使用 `[achuan_ai]` 作为分组名称
3. 确认 API 密钥格式正确
4. 检查应用是否重启

### Q: 如何测试 Secrets 配置？

A: 可以在代码中添加调试信息：
```python
if st.secrets:
    st.write("Secrets 加载成功")
    st.write(f"Token 配置: {'已配置' if st.secrets.achuan_ai.get('token') else '未配置'}")
else:
    st.write("未检测到 Secrets")
```

### Q: 部署时 Secrets 配置丢失？

A: 确认部署平台支持 Secrets 功能，或改用环境变量配置。

## 七、最佳实践

1. **分离配置和代码**：不要将 API 密钥硬编码到代码中
2. **使用不同密钥**：为不同环境使用不同的 API 密钥
3. **定期轮换密钥**：提高安全性
4. **限制密钥权限**：如果 API 支持，限制密钥的使用权限
5. **监控密钥使用**：关注 API 密钥的使用情况，防止滥用

通过正确配置 Streamlit Secrets，您可以在不同环境中轻松管理 API 密钥，避免每次手动输入的麻烦，同时保持安全性。