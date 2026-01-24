import socket
import struct
import binascii
import logging
import threading
import sys
import os
from logging.handlers import RotatingFileHandler

# 配置日志
# 确保日志目录存在
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, 'logs')
if not os.path.exists(LOG_DIR):
    try:
        os.makedirs(LOG_DIR)
    except Exception:
        pass

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('STUN-Server')

# 添加单独的文件日志
try:
    file_handler = RotatingFileHandler(
        os.path.join(LOG_DIR, 'stun.log'),
        maxBytes=1024*1024,
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)
except Exception as e:
    print(f"Failed to setup file logging: {e}")

class StunServer:
    def __init__(self, host='0.0.0.0', port=3478):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.sock.bind((self.host, self.port))
        except OSError as e:
            logger.error(f"Failed to bind to {self.host}:{self.port}: {e}")
            # 不直接退出，而是抛出异常让调用者处理
            raise e
        self.running = False
        
    def start(self):
        self.running = True
        logger.info(f"STUN Server started on {self.host}:{self.port}")
        
        while self.running:
            try:
                data, addr = self.sock.recvfrom(2048)
                self.handle_request(data, addr)
            except Exception as e:
                logger.error(f"Error: {e}")
                
    def handle_request(self, data, addr):
        # 简单的 STUN 解析
        # STUN 消息头: Type(2) + Length(2) + Cookie(4) + TransactionID(12)
        if len(data) < 20:
            return
            
        msg_type = struct.unpack("!H", data[0:2])[0]
        
        # Binding Request: 0x0001
        if msg_type == 0x0001:
            logger.info(f"Received Binding Request from {addr}")
            response = self.build_binding_response(data, addr)
            self.sock.sendto(response, addr)
            
    def build_binding_response(self, request_data, addr):
        # Binding Response: 0x0101
        msg_type = 0x0101
        
        # Magic Cookie (RFC 5389)
        magic_cookie = 0x2112A442
        
        # Transaction ID (same as request)
        trans_id = request_data[8:20]
        
        # MAPPED-ADDRESS (0x0001) or XOR-MAPPED-ADDRESS (0x0020)
        # 这里使用 XOR-MAPPED-ADDRESS (RFC 5389 推荐)
        
        # XOR-MAPPED-ADDRESS Attribute
        # Type(2) + Length(2) + Family(1) + Port(2) + IP(4)
        attr_type = 0x0020
        attr_len = 8
        family = 0x01 # IPv4
        
        # Port XOR mapping
        # Port is XORed with high 16 bits of magic cookie
        port = addr[1]
        x_port = port ^ (magic_cookie >> 16)
        
        # IP XOR mapping
        # IP is XORed with magic cookie
        ip_int = struct.unpack("!I", socket.inet_aton(addr[0]))[0]
        x_ip = ip_int ^ magic_cookie
        
        # 构建 Attribute Value
        attr_value = struct.pack("!xBH4s", family, x_port, struct.pack("!I", x_ip))
        
        # Attribute header
        attr_header = struct.pack("!HH", attr_type, attr_len)
        
        # Message Body
        body = attr_header + attr_value
        
        # Message Header
        msg_len = len(body)
        header = struct.pack("!HH4s", msg_type, msg_len, struct.pack("!I", magic_cookie)) + trans_id
        
        return header + body

if __name__ == "__main__":
    server = StunServer()
    try:
        server.start()
    except KeyboardInterrupt:
        logger.info("Stopping server...")
