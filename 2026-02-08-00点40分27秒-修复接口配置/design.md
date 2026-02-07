# Design: 修复接口配置与后端导入

## 1. 后端修复方案 (Backend)

### 1.1 问题定位
在 `zapp/views.py` 的 `register` 函数中使用了 `User.objects.filter(...)` 和 `User.objects.create_user(...)`，但文件头部缺少 `from django.contrib.auth.models import User` 的导入语句。

### 1.2 修复代码
在 `zapp/views.py` 的导入区域（文件顶部或 `register` 函数之前的相关导入块）添加：
```python
from django.contrib.auth.models import User
```
同时确保 `authenticate`, `login`, `logout` 等函数也已正确导入（已存在，无需修改）。

## 2. 前端配置修改方案 (Frontend)

### 2.1 代理配置位置
Taro 项目的开发环境配置通常位于 `frontend/config/dev.ts`。如果该文件只包含基础配置，则需要在 `h5` 字段下添加或修改 `devServer` 配置。

### 2.2 代理规则
我们需要将 `/apipy` 开头的请求代理到 `http://haoguozhi.com`。

```typescript
// frontend/config/dev.ts

export default {
  logger: {
    quiet: false,
    stats: true
  },
  mini: {},
  h5: {
    devServer: {
      proxy: {
        '/apipy': {
          target: 'http://haoguozhi.com', // 目标服务器
          changeOrigin: true,             // 允许跨域
          secure: false,                  // 如果是 https 且证书自签名，可能需要设为 false
          // pathRewrite: { '^/apipy': '/apipy' } // 通常不需要重写，除非后端不包含此前缀
        }
      }
    }
  }
}
```

### 2.3 验证
配置修改后，需要重启 Taro 开发服务器（`npm run dev:h5`）才能生效。
请求流程：
前端 (`/apipy/auth/register`) -> 本地 DevServer -> 代理 -> `http://haoguozhi.com/apipy/auth/register`

## 3. 步骤
1.  修改 `zapp/views.py`。
2.  查找并修改 `frontend/config/dev.ts`（若无则创建或修改 `index.ts` 中的 dev 判断块，但标准 Taro 项目应有 `dev.ts`）。
