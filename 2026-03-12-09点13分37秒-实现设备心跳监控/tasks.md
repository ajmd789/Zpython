# 开发任务：设备心跳监控

- [ ] 1. **数据库设计**: 在 `zapp/models.py` 中添加 `Device` 模型，并进行迁移。
- [ ] 2. **后端 API**:
    - [ ] 2.1 实现 `heartbeat_api` 接收 POST 请求，更新设备心跳时间。
    - [ ] 2.2 实现 `get_devices_api` 返回设备列表。
    - [ ] 2.3 配置 `zapp/urls.py` 路由。
- [ ] 3. **前端页面**:
    - [ ] 3.1 创建 `zapp/templates/zapp/device_monitor.html`，实现心跳列表展示。
    - [ ] 3.2 实现自动刷新逻辑（AJAX）。
- [ ] 4. **主页集成**:
    - [ ] 4.1 修改 `zapp/templates/zapp/homepage.html`，添加跳转链接。
- [ ] 5. **测试与验证**:
    - [ ] 5.1 手动发送 POST 请求测试心跳接口。
    - [ ] 5.2 验证前端页面展示是否正确。
    - [ ] 5.3 检查自动刷新是否工作。
