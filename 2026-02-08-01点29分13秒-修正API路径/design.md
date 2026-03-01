# Design: 修正前端 API 请求路径

## 1. 方案概述
通过全局搜索替换的方式，将前端代码中硬编码的 API 路径进行更新，插入 missing 的 `/api` 路径段。

## 2. 修改文件清单

### 2.1 `frontend/src/pages/register/index.tsx`
- 修改注册接口调用路径。
- 原代码：`fetch(\`\${BASE_URL}/apipy/auth/register\`)`
- 新代码：`fetch(\`\${BASE_URL}/apipy/api/auth/register\`)`

### 2.2 `frontend/src/pages/login/index.tsx`
- 修改登录接口调用路径。
- 原代码：`fetch(\`\${BASE_URL}/apipy/auth/login\`)`
- 新代码：`fetch(\`\${BASE_URL}/apipy/api/auth/login\`)`

### 2.3 `frontend/src/context/AuthContext.tsx`
- 修改所有认证相关接口调用路径。
- `getUserInfo`: `/apipy/auth/userinfo` -> `/apipy/api/auth/userinfo`
- `login`: `/apipy/auth/login` -> `/apipy/api/auth/login`
- `logout`: `/apipy/auth/logout` -> `/apipy/api/auth/logout`
- `register`: `/apipy/auth/register` -> `/apipy/api/auth/register`
- `updateUserInfo`: `/apipy/auth/update` -> `/apipy/api/auth/update`

## 3. 验证计划
- 检查代码修改是否正确。
- 确认 `BASE_URL` 和代理配置不需要修改（代理重写规则兼容新的路径）。
