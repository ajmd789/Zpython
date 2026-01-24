from django.urls import re_path
from . import consumers

# WebSocket 路由：将 /ws/chat/ 路径映射到 ChatConsumer
websocket_urlpatterns = [
    re_path(r'ws/chat/$', consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/voice/(?P<room_id>[\w-]+)/$', consumers.VoiceConsumer.as_asgi()),
]