import time
import random
import threading
import uuid
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

logger = logging.getLogger(__name__)

class WebRTCRoomManager:
    def __init__(self):
        self.rooms = {}
        self.lock = threading.Lock()
        self.heartbeat_timeout = 30  # 心跳超时时间（秒）
    
    def create_room(self, max_capacity=2):
        """创建一个新的语音房间"""
        with self.lock:
            room_id = f"room_{uuid.uuid4().hex[:8]}"
            self.rooms[room_id] = {
                'slots': [None] * max_capacity,
                'created_at': time.time(),
                'max_capacity': max_capacity
            }
            logger.info(f"Created room {room_id} with capacity {max_capacity}")
            return room_id
    
    def get_room(self, room_id):
        """获取房间信息，如果房间不存在则创建"""
        with self.lock:
            if room_id not in self.rooms:
                # 创建默认房间
                self.rooms[room_id] = {
                    'slots': [None, None],
                    'created_at': time.time(),
                    'max_capacity': 2
                }
                logger.info(f"Created default room {room_id} with capacity 2")
            return self.rooms.get(room_id)
    
    def generate_user_id(self):
        """生成唯一的用户 ID"""
        return f"user_{uuid.uuid4().hex[:10]}"
    
    def join_room(self, room_id, user_id):
        """用户加入房间"""
        with self.lock:
            # 如果房间不存在，先创建房间
            if room_id not in self.rooms:
                self.rooms[room_id] = {
                    'slots': [None, None],
                    'created_at': time.time(),
                    'max_capacity': 2
                }
                logger.info(f"Created default room {room_id} with capacity 2")
            
            room = self.rooms[room_id]
            
            # 检查用户是否已经在房间中
            for i, slot in enumerate(room['slots']):
                if slot and slot['user_id'] == user_id:
                    logger.info(f"User {user_id} already in room {room_id} at slot {i}")
                    # 更新用户活动时间
                    slot['last_active'] = time.time()
                    return True, i, "User already in room"
            
            # 找到空闲槽位，按顺序分配（先分配0号槽位，再分配1号槽位）
            for i, slot in enumerate(room['slots']):
                if slot is None:
                    room['slots'][i] = {
                        'user_id': user_id,
                        'joined_at': time.time(),
                        'last_active': time.time(),
                        'last_spoke': time.time(),  # 添加最后说话时间
                        'ice_candidates': [],
                        'offer': None,
                        'answer': None
                    }
                    logger.info(f"User {user_id} joined room {room_id} at slot {i}")
                    return True, i, "success"
            
            return False, -1, "Room is full"
    
    def leave_room(self, room_id, user_id):
        """用户离开房间"""
        with self.lock:
            room = self.rooms.get(room_id)
            if not room:
                return False, "Room not found"
            
            for i, slot in enumerate(room['slots']):
                if slot and slot['user_id'] == user_id:
                    room['slots'][i] = None
                    logger.info(f"User {user_id} left room {room_id}")
                    return True, "success"
            
            return True, "User not in room"
    
    def update_heartbeat(self, room_id, user_id):
        """更新用户心跳"""
        with self.lock:
            room = self.rooms.get(room_id)
            if not room:
                return False, "Room not found"
            
            for i, slot in enumerate(room['slots']):
                if slot and slot['user_id'] == user_id:
                    room['slots'][i]['last_active'] = time.time()
                    logger.debug(f"Updated heartbeat for user {user_id} in room {room_id}")
                    return True, "success"
            
            return False, "User not in room"
    
    def set_offer(self, room_id, user_id, offer):
        """设置用户的 offer"""
        with self.lock:
            room = self.rooms.get(room_id)
            if not room:
                return False, "Room not found"
            
            for i, slot in enumerate(room['slots']):
                if slot and slot['user_id'] == user_id:
                    room['slots'][i]['offer'] = offer
                    logger.debug(f"Set offer for user {user_id} in room {room_id}")
                    return True, "success"
            
            return False, "User not in room"
    
    def set_answer(self, room_id, user_id, answer):
        """设置用户的 answer"""
        with self.lock:
            room = self.rooms.get(room_id)
            if not room:
                return False, "Room not found"
            
            for i, slot in enumerate(room['slots']):
                if slot and slot['user_id'] == user_id:
                    room['slots'][i]['answer'] = answer
                    logger.debug(f"Set answer for user {user_id} in room {room_id}")
                    return True, "success"
            
            return False, "User not in room"
    
    def add_ice_candidate(self, room_id, user_id, candidate):
        """添加 ICE candidate"""
        with self.lock:
            room = self.rooms.get(room_id)
            if not room:
                return False, "Room not found"
            
            for i, slot in enumerate(room['slots']):
                if slot and slot['user_id'] == user_id:
                    slot['ice_candidates'].append(candidate)
                    logger.debug(f"Added ICE candidate for user {user_id} in room {room_id}")
                    return True, "success"
            
            return False, "User not in room"
    
    def clear_ice_candidates(self, room_id, user_id):
        """清除 ICE candidates"""
        with self.lock:
            room = self.rooms.get(room_id)
            if not room:
                return False, "Room not found"
            
            for i, slot in enumerate(room['slots']):
                if slot and slot['user_id'] == user_id:
                    slot['ice_candidates'] = []
                    logger.debug(f"Cleared ICE candidates for user {user_id} in room {room_id}")
                    return True, "success"
            
            return False, "User not in room"
    
    def update_spoke_time(self, room_id, user_id):
        """更新用户最后说话时间"""
        with self.lock:
            room = self.rooms.get(room_id)
            if not room:
                return False, "Room not found"
            
            for i, slot in enumerate(room['slots']):
                if slot and slot['user_id'] == user_id:
                    slot['last_spoke'] = time.time()
                    slot['last_active'] = time.time()  # 同时更新活动时间
                    logger.debug(f"Updated spoke time for user {user_id} in room {room_id}")
                    return True, "success"
            
            return False, "User not in room"
    
    def cleanup_inactive_users(self):
        """清理不活跃的用户和30秒不说话的用户"""
        with self.lock:
            current_time = time.time()
            for room_id, room in list(self.rooms.items()):
                for i, slot in enumerate(room['slots']):
                    if slot:
                        # 检查30秒不说话的用户
                        if current_time - slot['last_spoke'] > 30:
                            logger.info(f"Removed silent user {slot['user_id']} from room {room_id} (30s without speaking)")
                            room['slots'][i] = None
                        # 检查心跳超时的用户
                        elif current_time - slot['last_active'] > self.heartbeat_timeout:
                            logger.info(f"Removed inactive user {slot['user_id']} from room {room_id}")
                            room['slots'][i] = None
                
                # 检查房间是否为空，如果为空则删除
                if all(slot is None for slot in room['slots']):
                    logger.info(f"Deleted empty room {room_id}")
                    del self.rooms[room_id]

# 创建全局实例
webrtc_manager = WebRTCRoomManager()

# 启动后台线程，定期清理不活跃用户和30秒不说话的用户
def start_cleanup_thread():
    import threading
    def cleanup_loop():
        while True:
            webrtc_manager.cleanup_inactive_users()
            time.sleep(5)  # 每5秒检查一次
    
    thread = threading.Thread(target=cleanup_loop, daemon=True)
    thread.start()
    logger.info("Started cleanup thread for inactive and silent users")

# 启动清理线程
start_cleanup_thread()

@csrf_exempt
def room_api(request):
    """
    WebRTC信令API端点
    :param request: HTTP请求对象
    :return: JSON响应
    """
    try:
        if request.method == 'GET':
            # 获取房间状态
            room_id = request.GET.get('room_id', 'main-room')
            room = webrtc_manager.get_room(room_id)
            
            if not room:
                return JsonResponse({
                    'code': 404,
                    'data': None,
                    'message': 'Room not found'
                }, status=404)
            
            return JsonResponse({
                'code': 200,
                'data': {
                    'room_id': room_id,
                    'slots': room['slots'],
                    'created_at': room['created_at'],
                    'max_capacity': room['max_capacity']
                },
                'message': 'success'
            })
        
        elif request.method == 'POST':
            import json
            body = json.loads(request.body)
            action = body.get('action')
            
            if action == 'generate-id':
                # 生成用户ID
                user_id = webrtc_manager.generate_user_id()
                return JsonResponse({
                    'code': 200,
                    'data': {'user_id': user_id},
                    'message': 'success'
                })
            
            elif action == 'create-room':
                # 创建房间
                max_capacity = body.get('max_capacity', 2)
                room_id = webrtc_manager.create_room(max_capacity)
                return JsonResponse({
                    'code': 200,
                    'data': {'room_id': room_id},
                    'message': 'success'
                })
            
            elif action == 'join':
                # 用户加入房间
                room_id = body.get('room_id', 'main-room')
                user_id = body.get('user_id')
                
                if not user_id:
                    return JsonResponse({
                        'code': 400,
                        'data': None,
                        'message': 'Missing user_id'
                    }, status=400)
                
                success, slot_index, message = webrtc_manager.join_room(room_id, user_id)
                room = webrtc_manager.get_room(room_id)
                
                return JsonResponse({
                    'code': 200 if success else 400,
                    'data': {
                        'success': success,
                        'slot_index': slot_index,
                        'room': room
                    },
                    'message': message
                })
            
            elif action == 'leave':
                # 用户离开房间
                room_id = body.get('room_id', 'main-room')
                user_id = body.get('user_id')
                
                if not user_id:
                    return JsonResponse({
                        'code': 400,
                        'data': None,
                        'message': 'Missing user_id'
                    }, status=400)
                
                success, message = webrtc_manager.leave_room(room_id, user_id)
                room = webrtc_manager.get_room(room_id)
                
                return JsonResponse({
                    'code': 200,
                    'data': {
                        'success': success,
                        'room': room
                    },
                    'message': message
                })
            
            elif action == 'offer':
                # 设置offer
                room_id = body.get('room_id', 'main-room')
                user_id = body.get('user_id')
                offer = body.get('offer')
                
                if not user_id:
                    return JsonResponse({
                        'code': 400,
                        'data': None,
                        'message': 'Missing user_id'
                    }, status=400)
                
                if not offer:
                    return JsonResponse({
                        'code': 400,
                        'data': None,
                        'message': 'Missing offer'
                    }, status=400)
                
                success, message = webrtc_manager.set_offer(room_id, user_id, offer)
                room = webrtc_manager.get_room(room_id)
                
                return JsonResponse({
                    'code': 200 if success else 404,
                    'data': {
                        'success': success,
                        'room': room
                    },
                    'message': message
                })
            
            elif action == 'answer':
                # 设置answer
                room_id = body.get('room_id', 'main-room')
                user_id = body.get('user_id')
                answer = body.get('answer')
                
                if not user_id:
                    return JsonResponse({
                        'code': 400,
                        'data': None,
                        'message': 'Missing user_id'
                    }, status=400)
                
                if not answer:
                    return JsonResponse({
                        'code': 400,
                        'data': None,
                        'message': 'Missing answer'
                    }, status=400)
                
                success, message = webrtc_manager.set_answer(room_id, user_id, answer)
                room = webrtc_manager.get_room(room_id)
                
                return JsonResponse({
                    'code': 200 if success else 404,
                    'data': {
                        'success': success,
                        'room': room
                    },
                    'message': message
                })
            
            elif action == 'ice-candidate':
                # 添加ICE candidate
                room_id = body.get('room_id', 'main-room')
                user_id = body.get('user_id')
                candidate = body.get('candidate')
                
                if not user_id:
                    return JsonResponse({
                        'code': 400,
                        'data': None,
                        'message': 'Missing user_id'
                    }, status=400)
                
                if not candidate:
                    return JsonResponse({
                        'code': 400,
                        'data': None,
                        'message': 'Missing candidate'
                    }, status=400)
                
                success, message = webrtc_manager.add_ice_candidate(room_id, user_id, candidate)
                room = webrtc_manager.get_room(room_id)
                
                return JsonResponse({
                    'code': 200 if success else 404,
                    'data': {
                        'success': success,
                        'room': room
                    },
                    'message': message
                })
            
            elif action == 'clear-ice-candidates':
                # 清除ICE candidates
                room_id = body.get('room_id', 'main-room')
                user_id = body.get('user_id')
                
                if not user_id:
                    return JsonResponse({
                        'code': 400,
                        'data': None,
                        'message': 'Missing user_id'
                    }, status=400)
                
                success, message = webrtc_manager.clear_ice_candidates(room_id, user_id)
                room = webrtc_manager.get_room(room_id)
                
                return JsonResponse({
                    'code': 200 if success else 404,
                    'data': {
                        'success': success,
                        'room': room
                    },
                    'message': message
                })
            
            elif action == 'update-spoke-time':
                # 更新用户最后说话时间
                room_id = body.get('room_id', 'main-room')
                user_id = body.get('user_id')
                
                if not user_id:
                    return JsonResponse({
                        'code': 400,
                        'data': None,
                        'message': 'Missing user_id'
                    }, status=400)
                
                success, message = webrtc_manager.update_spoke_time(room_id, user_id)
                room = webrtc_manager.get_room(room_id)
                
                return JsonResponse({
                    'code': 200 if success else 404,
                    'data': {
                        'success': success,
                        'room': room
                    },
                    'message': message
                })
            
            elif action == 'heartbeat':
                # 更新心跳
                room_id = body.get('room_id', 'main-room')
                user_id = body.get('user_id')
                
                if not user_id:
                    return JsonResponse({
                        'code': 400,
                        'data': None,
                        'message': 'Missing user_id'
                    }, status=400)
                
                success, message = webrtc_manager.update_heartbeat(room_id, user_id)
                room = webrtc_manager.get_room(room_id)
                
                return JsonResponse({
                    'code': 200 if success else 404,
                    'data': {
                        'success': success,
                        'room': room
                    },
                    'message': message
                })
            
            else:
                return JsonResponse({
                    'code': 400,
                    'data': None,
                    'message': 'Unknown action'
                }, status=400)
        
        else:
            return JsonResponse({
                'code': 405,
                'data': None,
                'message': 'Method not allowed'
            }, status=405)
    
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON format in room_api: {request.body}")
        return JsonResponse({
            'code': 400,
            'data': None,
            'message': 'Invalid JSON format'
        }, status=400)
    
    except Exception as e:
        logger.exception(f"Server error in room_api: {str(e)}")
        return JsonResponse({
            'code': 500,
            'data': None,
            'message': f'Server error: {str(e)}'
        }, status=500)