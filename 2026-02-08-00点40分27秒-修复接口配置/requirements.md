# Requirements: 修复接口配置与后端导入

## 1. 背景
用户反馈前端请求 `http://192.168.0.105:10087/apipy/auth/register` 失败，期望请求转发至 `haoguozhi.com`。
同时，后端代码审查发现 `zapp/views.py` 中缺少 `User` 模型的导入，会导致注册接口报错。

## 2. 核心需求

### 2.1 前端代理修正
- **目标**：修改 Taro 前端的开发配置，将 API 请求代理到 `http://haoguozhi.com`（或 `https`，视实际情况而定）。
- **文件**：`frontend/config/dev.ts` (需要检查是否存在，若不存在则检查 `index.ts` 中的代理配置)。
- **路径匹配**：确保 `/apipy` 开头的请求被正确转发。

### 2.2 后端 Bug 修复
- **目标**：修复 `zapp/views.py` 中的 `NameError: name 'User' is not defined`。
- **文件**：`zapp/views.py`。
- **操作**：添加 `from django.contrib.auth.models import User`。

## 3. 交付物
- 更新后的前端配置文件。
- 修复后的后端视图文件。
