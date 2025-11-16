import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):
    # 连接建立时调用
    async def connect(self):
        # 定义一个房间组（用于多客户端通信）
        self.room_group_name = 'chat_group'
        
        # 加入房间组
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        # 接受客户端连接
        await self.accept()

    # 连接关闭时调用
    async def disconnect(self, close_code):
        # 离开房间组
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # 收到客户端消息时调用
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']  # 解析客户端发送的消息
        
        # 向房间组内所有客户端广播消息
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',  # 对应下方的 chat_message 方法
                'message': message
            }
        )

    # 处理组内消息并发送给当前客户端
    async def chat_message(self, event):
        message = event['message']
        
        # 向客户端发送消息
        await self.send(text_data=json.dumps({
            'message': message
        }))