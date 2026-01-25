import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger('zapp.webrtc_service')

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

class VoiceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            self.room_id = self.scope['url_route']['kwargs'].get('room_id', 'main-room')
            self.room_group_name = f'voice_{self.room_id}'
            self.user_id = None
            
            logger.info(f"WebSocket connecting: {self.channel_name} to {self.room_group_name}")

            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
            logger.info(f"WebSocket connected: {self.channel_name}")
        except Exception as e:
            logger.error(f"WebSocket connection failed: {e}", exc_info=True)
            await self.close()

    async def disconnect(self, close_code):
        try:
            logger.info(f"WebSocket disconnected: {self.channel_name} from {self.room_group_name}")
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        except Exception as e:
            logger.error(f"WebSocket disconnect error: {e}", exc_info=True)

    async def receive(self, text_data=None, bytes_data=None):
        if text_data:
            try:
                data = json.loads(text_data)
                action = data.get('action')
                self.user_id = data.get('user_id')
                
                logger.debug(f"Received WS message: {action} from {self.user_id}")
                
                # 转发信令给房间内其他人
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'voice_signal',
                        'sender_channel_name': self.channel_name,
                        'data': data
                    }
                )
            except json.JSONDecodeError:
                logger.error("Invalid JSON received")
            except Exception as e:
                logger.error(f"WebSocket receive error: {e}", exc_info=True)
        
    async def voice_signal(self, event):
        try:
            # 不发给自己
            if self.channel_name != event['sender_channel_name']:
                await self.send(text_data=json.dumps(event['data']))
        except Exception as e:
            logger.error(f"WebSocket send error: {e}", exc_info=True)