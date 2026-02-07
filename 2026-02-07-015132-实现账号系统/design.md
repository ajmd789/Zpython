# 账号系统设计文档

## 1. 项目概述

本设计文档描述了基于 Django + React + Taro 的账号系统实现方案，包括用户注册、登录、登出、用户信息管理等功能。系统设计遵循业界最佳实践，确保安全性、可扩展性和用户体验。

## 2. 技术栈

- **后端**：Django 4.2、SQLite（默认数据库）
- **前端**：React 18、TypeScript、Taro 4.1.11、Sass
- **认证方式**：Django Session 认证

## 3. 数据库设计

### 3.1 数据模型

#### 3.1.1 User 模型（使用 Django 内置）

| 字段名 | 类型 | 描述 | 约束 |
|-------|------|------|------|
| id | BigAutoField | 用户ID | 主键 |
| username | CharField(150) | 账号名 | 唯一，必填 |
| password | CharField(128) | 密码哈希 | 必填 |
| email | EmailField(254) | 邮箱 | 可选，唯一 |
| first_name | CharField(150) | 名 | 可选 |
| last_name | CharField(150) | 姓 | 可选 |
| is_active | BooleanField | 是否活跃 | 默认 True |
| is_staff | BooleanField | 是否员工 | 默认 False |
| is_superuser | BooleanField | 是否超级用户 | 默认 False |
| last_login | DateTimeField | 最后登录时间 | 可选 |
| date_joined | DateTimeField | 注册时间 | 自动设置 |

#### 3.1.2 UserProfile 模型（扩展）

| 字段名 | 类型 | 描述 | 约束 |
|-------|------|------|------|
| id | BigAutoField | 主键 | 主键 |
| user | OneToOneField(User) | 关联用户 | 唯一，必填 |
| phone | CharField(11) | 手机号 | 可选，唯一 |
| nickname | CharField(50) | 昵称 | 可选 |
| avatar | CharField(255) | 头像URL | 可选 |
| created_at | DateTimeField | 创建时间 | 自动设置 |
| updated_at | DateTimeField | 更新时间 | 自动设置 |

## 4. API 接口设计

### 4.1 接口列表

| 接口路径 | 方法 | 功能描述 | 模块 |
|---------|------|----------|------|
| `/apipy/auth/register` | POST | 用户注册 | zapp.views |
| `/apipy/auth/login` | POST | 用户登录 | zapp.views |
| `/apipy/auth/logout` | POST | 用户登出 | zapp.views |
| `/apipy/auth/userinfo` | GET | 获取用户信息 | zapp.views |
| `/apipy/auth/update` | POST | 更新用户信息 | zapp.views |
| `/apipy/auth/changepassword` | POST | 修改密码 | zapp.views |

### 4.2 接口详情

#### 4.2.1 注册接口

- **路径**：`/apipy/auth/register`
- **方法**：POST
- **参数**：
  - username: 账号名（必填，3-150字符）
  - password: 密码（必填，6-128字符）
  - email: 邮箱（可选）
  - phone: 手机号（可选，11位）
  - nickname: 昵称（可选）
- **返回**：
  - 成功：`{"code": 200, "data": {"user_id": 1, "username": "..."}, "message": "success"}`
  - 失败：`{"code": 400, "data": null, "message": "错误信息"}`

#### 4.2.2 登录接口

- **路径**：`/apipy/auth/login`
- **方法**：POST
- **参数**：
  - username: 账号名（必填）
  - password: 密码（必填）
- **返回**：
  - 成功：`{"code": 200, "data": {"user_id": 1, "username": "..."}, "message": "success"}`
  - 失败：`{"code": 401, "data": null, "message": "账号或密码错误"}`

#### 4.2.3 登出接口

- **路径**：`/apipy/auth/logout`
- **方法**：POST
- **参数**：无
- **返回**：
  - 成功：`{"code": 200, "data": null, "message": "success"}`

#### 4.2.4 获取用户信息

- **路径**：`/apipy/auth/userinfo`
- **方法**：GET
- **返回**：
  - 成功：`{"code": 200, "data": {"user_id": 1, "username": "...", "email": "...", "phone": "...", "nickname": "..."}, "message": "success"}`
  - 失败：`{"code": 401, "data": null, "message": "未登录"}`

#### 4.2.5 更新用户信息

- **路径**：`/apipy/auth/update`
- **方法**：POST
- **参数**：
  - email: 邮箱（可选）
  - phone: 手机号（可选）
  - nickname: 昵称（可选）
- **返回**：
  - 成功：`{"code": 200, "data": {"user_id": 1, "username": "...", "email": "...", "phone": "...", "nickname": "..."}, "message": "success"}`
  - 失败：`{"code": 401, "data": null, "message": "未登录"}`

#### 4.2.6 修改密码

- **路径**：`/apipy/auth/changepassword`
- **方法**：POST
- **参数**：
  - old_password: 旧密码（必填）
  - new_password: 新密码（必填，6-128字符）
- **返回**：
  - 成功：`{"code": 200, "data": null, "message": "success"}`
  - 失败：`{"code": 400, "data": null, "message": "旧密码错误"}`

## 5. 前端设计

### 5.1 页面结构

- **登录页面**：`frontend/src/pages/login/index.tsx`
  - 账号输入框
  - 密码输入框
  - 登录按钮
  - 注册链接

- **注册页面**：`frontend/src/pages/register/index.tsx`
  - 账号输入框
  - 密码输入框
  - 确认密码输入框
  - 邮箱输入框（可选）
  - 手机号输入框（可选）
  - 昵称输入框（可选）
  - 注册按钮
  - 登录链接

- **主页面**：`frontend/src/pages/index/index.tsx`
  - 登录状态显示
  - 用户信息下拉菜单
  - 登出按钮

### 5.2 全局状态管理

使用 React Context API 创建 `AuthContext`，用于管理用户登录状态和提供认证相关方法：

- `isAuthenticated`: 是否登录
- `user`: 用户信息
- `login()`: 登录方法
- `logout()`: 登出方法
- `register()`: 注册方法
- `updateUserInfo()`: 更新用户信息方法

### 5.3 路由配置

在 Taro 配置文件中添加登录和注册页面路由：

```json
{
  "pages": [
    "pages/index/index",
    "pages/login/index",
    "pages/register/index"
  ]
}
```

## 6. 安全考虑

1. **密码加密**：使用 Django 内置的密码哈希函数，确保密码安全存储
2. **输入验证**：对所有用户输入进行严格验证，防止注入攻击
3. **CSRF 保护**：使用 Django 内置的 CSRF 保护机制
4. **会话管理**：使用 Django Session 管理用户会话，确保会话安全
5. **错误处理**：返回友好的错误信息，避免泄露系统细节
6. **权限控制**：对需要认证的接口进行权限检查

## 7. 后续扩展

1. **手机验证码**：添加手机号验证功能
2. **头像上传**：支持用户上传头像
3. **第三方登录**：集成微信、QQ等第三方登录
4. **密码找回**：通过邮箱或手机号找回密码
5. **多因素认证**：添加短信验证码、邮箱验证码等多因素认证

## 8. 部署建议

1. **生产环境**：使用 PostgreSQL 或 MySQL 数据库，提高性能和可靠性
2. **HTTPS**：启用 HTTPS 加密传输，保护用户数据
3. **会话配置**：在生产环境中使用持久化会话存储，如 Redis
4. **日志记录**：完善日志记录，便于问题排查
5. **监控**：添加系统监控，及时发现和处理异常

## 9. 测试计划

1. **单元测试**：测试后端 API 接口
2. **集成测试**：测试前后端集成功能
3. **用户测试**：测试用户注册、登录、登出等核心功能
4. **安全测试**：测试密码加密、CSRF 保护等安全功能

## 10. 实现步骤

1. **创建 UserProfile 模型**
2. **实现认证相关视图**
3. **配置 URL 路由**
4. **运行数据库迁移**
5. **创建前端登录页面**
6. **创建前端注册页面**
7. **添加全局状态管理**
8. **修改主页面**
9. **测试账号系统功能**
10. **部署和上线**