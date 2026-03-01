# Requirements: 修正前端 API 请求路径

## 1. 背景
用户反馈前端 Taro 项目中的 API 请求路径配置有误。
当前请求路径为：`https://haoguozhi.com/apipy/auth/register`
期望请求路径为：`https://haoguozhi.com/apipy/api/auth/register`

## 2. 需求详情
- 将前端代码中所有涉及 `/apipy/auth/` 的请求路径修正为 `/apipy/api/auth/`。
- 确保 `register`、`login` 等相关功能均使用新的路径格式。
- 保持 `BASE_URL` 配置（开发环境为空字符串，生产环境为 `https://haoguozhi.com`）与代理配置的兼容性。

## 3. 涉及范围
- 注册页面 (`register/index.tsx`)
- 登录页面 (`login/index.tsx`)
- 认证上下文 (`AuthContext.tsx`)
