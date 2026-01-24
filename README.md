
## 语音连麦功能 (WebRTC + WebSocket)

本功能实现了基于 WebRTC 的语音连麦，完全采用自建服务，不依赖外部 STUN/TURN 服务器。

### 架构设计

1.  **信令服务 (Signaling)**: 使用 Django Channels (WebSocket) 替代传统的 HTTP 轮询，实现低延迟信令交换 (Offer/Answer/ICE)。
2.  **NAT 穿透 (STUN)**: 内置轻量级 Python STUN 服务器 (`stun_server.py`)，运行在本地 UDP 3478 端口，实现 P2P 连接所需的 IP/Port 发现。
3.  **日志系统**: 
    - 独立日志文件 `logs/voice.log`，记录详细的信令交互和 WebRTC 状态。
    - 前端日志通过 WebSocket 发送或直接在控制台输出。

### 调试与测试

为了验证语音功能的完整链路，提供了自动化测试脚本 `test_voice.py`。

#### 1. 环境准备

```bash
# 创建虚拟环境
python3 -m venv venv

# 安装依赖
venv/bin/pip install -r requirements.txt
venv/bin/pip install selenium webdriver-manager daphne
```

#### 2. 运行自动化测试

该脚本会自动启动 Django (Daphne) 服务器和 STUN 服务器，并模拟两个用户加入房间。

```bash
# 运行测试
venv/bin/python test_voice.py
```

**测试流程**:
1.  启动 `stun_server.py` (UDP :3478)。
2.  启动 `daphne` (Django ASGI :8000)。
3.  打开两个 Chrome 浏览器窗口 (User A, User B)。
4.  自动导航至 `/voice_room/`。
5.  自动点击 "上麦"。
6.  检查 WebSocket 连接和 P2P 连接状态。
7.  检查 `logs/voice.log` 是否生成。

#### 3. 手动运行

如果需要手动调试，只需启动 Django 服务即可（STUN 服务会自动随 Django 启动）：

**Web 服务**:
```bash
venv/bin/daphne -p 8000 zproject.asgi:application
```
*或者使用 `python manage.py runserver`*

访问: http://127.0.0.1:8000/voice-room

### 日志查看

查看语音相关日志：
```bash
tail -f logs/voice.log
```
