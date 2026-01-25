# Zpython 项目文档

## 语音连麦模块 (WebRTC + WebSocket)

本模块实现了基于 WebRTC 的实时语音连麦功能，采用全自建服务架构，不依赖第三方 STUN/TURN 服务。

### 1. 核心架构与流程

本系统由前端 (HTML/JS)、信令服务 (Django Channels)、NAT 穿透服务 (Python STUN) 和 Nginx 反向代理组成。

```mermaid
sequenceDiagram
    participant UserA as 用户 A (Browser)
    participant Nginx as Nginx 代理
    participant Django as Django (Daphne)
    participant STUN as 自建 STUN Server
    participant UserB as 用户 B (Browser)

    Note over UserA, UserB: 1. 建立 WebSocket 信令连接
    UserA->>Nginx: WSS /ws/voice/main-room/
    Nginx->>Django: Upgrade to WebSocket (Localhost:5555)
    Django-->>UserA: Connection Established (101)
    
    UserB->>Nginx: WSS /ws/voice/main-room/
    Nginx->>Django: Upgrade to WebSocket
    Django-->>UserB: Connection Established (101)

    Note over UserA, UserB: 2. NAT 穿透 (ICE Candidate 收集)
    UserA->>STUN: UDP Binding Request (:3478)
    STUN-->>UserA: UDP Binding Response (Public IP:Port)
    UserA->>UserA: 生成 ICE Candidate (含公网地址)

    Note over UserA, UserB: 3. P2P 连接建立 (SDP 交换)
    UserA->>Django: Send Offer (Via WebSocket)
    Django->>UserB: Forward Offer
    UserB->>UserB: Set Remote Desc & Create Answer
    UserB->>Django: Send Answer
    Django->>UserA: Forward Answer
    
    UserA->>Django: Send ICE Candidate
    Django->>UserB: Forward ICE Candidate
    UserB->>UserB: Add ICE Candidate (Success)

    Note over UserA, UserB: 4. 语音通话
    UserA<->UserB: SRTP P2P 直接传输音频流
```

### 2. 关键代码位置

#### 2.1 Nginx 配置 (反向代理)
负责将 HTTPS 流量转发给 Django，并将 `/ws/` 路径的请求升级为 WebSocket 协议。

*   **配置说明**: 必须显式配置 `Upgrade` 和 `Connection` 头。
*   **代码示例**:
    ```nginx
    # WebSocket 服务
    location /ws/ {
        proxy_pass http://localhost:5555;
        
        # 协议升级关键配置
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    ```

#### 2.2 前端实现 (WebRTC 逻辑)
*   **文件位置**: [`zapp/templates/zapp/voice_room.html`](zapp/templates/zapp/voice_room.html)
*   **核心功能**:
    *   **STUN 配置**: [Line 386-395](zapp/templates/zapp/voice_room.html#L386-395) - 指定自建 STUN 服务器地址 (`stun:haoguozhi.com:3478`)。
    *   **WebSocket 连接**: [Line 437-471](zapp/templates/zapp/voice_room.html#L437-471) - 处理信令消息 (offer, answer, ice-candidate)。
    *   **WebRTC PeerConnection**: [Line 766-808](zapp/templates/zapp/voice_room.html#L766-808) - 管理 P2P 连接生命周期。

#### 2.3 后端信令服务 (Django Channels)
*   **路由配置**: [`zapp/routing.py`](zapp/routing.py) - 定义 WebSocket URL 路由。
*   **消费者逻辑**: [`zapp/consumers.py`](zapp/consumers.py)
    *   `VoiceConsumer` 类负责处理 `/ws/voice/{room_id}/` 的连接。
    *   接收客户端的 JSON 消息并广播给房间内其他用户（实现信令转发）。

#### 2.4 房间状态管理 (Python)
*   **文件位置**: [`zapp/webrtc_service.py`](zapp/webrtc_service.py)
*   **功能**:
    *   管理房间列表、用户槽位 (Slot 1/2)。
    *   处理用户加入、离开、心跳保活。
    *   提供 HTTP API 供前端轮询房间状态。

#### 2.5 自建 STUN 服务器
*   **文件位置**: [`stun_server.py`](stun_server.py)
*   **功能**:
    *   监听 UDP 3478 端口。
    *   解析 STUN 协议包 (RFC 5389)，返回客户端的公网 IP 和端口 (XOR-MAPPED-ADDRESS)。
    *   **日志**: 输出到 `logs/stun.log`，用于调试 NAT 穿透问题。

### 3. 部署注意事项

1.  **端口开放**: 服务器防火墙必须放行以下端口：
    *   **TCP 5555**: Django/Daphne 服务（仅限本地或 Nginx 连接）。
    *   **UDP 3478**: STUN 服务（必须对公网开放，用于 NAT 穿透）。
2.  **HTTPS 强制**: 浏览器限制 WebRTC 必须在 HTTPS 环境下运行（本地 localhost 除外）。
3.  **进程守护**: 
    *   Django 使用 `systemd` 或 `supervisor` 管理。
    *   STUN 服务目前随 Django 启动 (在 `zapp/apps.py` 中调用)，也可独立部署。
