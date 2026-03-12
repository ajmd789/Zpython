# 设计文档：设备心跳监控系统

## 1. 数据库设计 (Schema)

在 `zapp/models.py` 中新增 `Device` 模型：

```python
class Device(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="设备名称")
    last_heartbeat = models.DateTimeField(auto_now=True, verbose_name="最后心跳时间")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP地址")
    status = models.CharField(max_length=20, default='offline', verbose_name="状态") # 可以通过计算得出，或者存储以便快速查询

    def is_online(self):
        # 判断是否在线（例如最近5分钟内有心跳）
        from django.utils import timezone
        import datetime
        return timezone.now() - self.last_heartbeat < datetime.timedelta(minutes=5)
```

## 2. API 设计

### 2.1 心跳上报接口 (`POST /api/heartbeat/`)
- **URL**: `/api/heartbeat/`
- **Method**: POST
- **Body**:
  ```json
  {
      "device_name": "MyDevice",
      "timestamp": 1678886400
  }
  ```
- **Response**:
  ```json
  {
      "code": 200,
      "message": "Heartbeat received",
      "data": { "device_name": "MyDevice", "status": "online" }
  }
  ```

### 2.2 在线设备列表接口 (`GET /api/devices/`)
- **URL**: `/api/devices/`
- **Method**: GET
- **Response**:
  ```json
  {
      "code": 200,
      "message": "success",
      "data": [
          {
              "name": "MyDevice",
              "last_heartbeat": "2023-03-15 10:00:00",
              "ip_address": "192.168.1.100",
              "status": "online"
          },
          ...
      ]
  }
  ```

## 3. 前端设计

### 3.1 页面 (`device_monitor.html`)
- **布局**: 类似于 `timestamp.html`，使用简单的 CSS Grid 或 Flexbox。
- **组件**:
  - 标题栏。
  - 设备列表区域：每个设备显示为一个卡片或表格行。
  - 刷新按钮：手动刷新。
  - 自动刷新开关：默认开启。
- **交互**:
  - 页面加载时请求 `/api/devices/`。
  - 定时器每 5-10 秒请求一次。
  - 如果请求失败，显示错误提示。

### 3.2 主页修改 (`homepage.html`)
- 在导航栏或主要功能区添加 "设备监控" 链接，指向 `/device_monitor/`。

## 4. 实现步骤
1.  修改 `zapp/models.py` 添加 `Device` 模型。
2.  运行 `makemigrations` 和 `migrate`。
3.  在 `zapp/views.py` 实现 `heartbeat_api` 和 `get_devices_api`。
4.  在 `zapp/urls.py` 添加路由。
5.  创建 `zapp/templates/zapp/device_monitor.html`。
6.  修改 `zapp/templates/zapp/homepage.html`。
7.  测试接口和页面。
