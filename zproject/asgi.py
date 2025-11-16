import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import zapp.routing  # 导入应用的 WebSocket 路由（稍后创建）

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zproject.settings')

# 协议路由：根据请求类型（HTTP/WebSocket）分发处理
application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # HTTP 请求仍用 Django 原生处理
    "websocket": AuthMiddlewareStack(
        URLRouter(
            zapp.routing.websocket_urlpatterns
        )
    ),
})