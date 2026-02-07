# Tasks: 修复接口配置与后端导入

- [ ] Task 1: 修复后端 `zapp/views.py` 导入错误
    - [ ] 在 `zapp/views.py` 中添加 `from django.contrib.auth.models import User`。

- [ ] Task 2: 配置前端代理
    - [ ] 检查 `frontend/config/dev.ts` 是否存在。
    - [ ] 修改 `frontend/config/dev.ts`，配置 `h5.devServer.proxy`，将 `/apipy` 代理至 `http://haoguozhi.com`。

- [ ] Task 3: 验证
    - [ ] 提示用户重启前端开发服务器。
