from django.apps import AppConfig
import threading
import logging
import sys
import os

logger = logging.getLogger('zapp.apps')

class ZappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'zapp'

    def ready(self):
        # 避免在 Django reload 时启动两次，或者在 migration 等命令时启动
        # RUN_MAIN 是 Django reloader 设置的环境变量
        # 但如果是 daphne 启动，可能没有 RUN_MAIN
        # 我们尝试启动，如果端口占用则忽略（说明已经启动了）
        
        # 检查是否是主进程或 runserver 的重载进程
        # 为了简单起见，我们尝试导入并启动 STUN 服务
        # 注意：在生产环境多进程模式下（如 gunicorn/uwsgi 多 worker），
        # 只有一个进程能成功绑定端口，其他会失败并被捕获。
        
        self.start_stun_server()

    def start_stun_server(self):
        try:
            # 尝试导入 stun_server (假设在项目根目录)
            # 将项目根目录加入 sys.path
            current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            if current_dir not in sys.path:
                sys.path.append(current_dir)
                
            from stun_server import StunServer
            
            def run_stun():
                try:
                    server = StunServer()
                    logger.info("Starting built-in STUN server...")
                    server.start()
                except OSError as e:
                    if "Address already in use" in str(e) or e.errno == 48:
                        logger.info("STUN server port 3478 already in use. Assuming it's running.")
                    else:
                        logger.error(f"Failed to start STUN server: {e}")
                except Exception as e:
                    logger.error(f"Unexpected error starting STUN server: {e}")

            # 启动守护线程
            thread = threading.Thread(target=run_stun, daemon=True)
            thread.start()
            
        except ImportError:
            logger.warning("Could not import stun_server.py. STUN server will not start automatically.")
        except Exception as e:
            logger.error(f"Error in start_stun_server: {e}")
