import psutil
import time
import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

# 配置日志
LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "server_resource.log"
LOG_MAX_SIZE = 256 * 1024  # 256KB，与package.py保持一致
LOG_BACKUP_COUNT = 5       # 保留5个备份，与package.py保持一致

# 创建日志文件夹
LOG_DIR.mkdir(exist_ok=True)

# 配置日志
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 日志格式（与package.py保持一致）
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# 文件处理器（带轮转功能，与package.py保持一致）
file_handler = RotatingFileHandler(
    LOG_FILE,
    maxBytes=LOG_MAX_SIZE,
    backupCount=LOG_BACKUP_COUNT,
    encoding='utf-8'
)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

def find_django_process():
    """查找Django相关进程"""
    django_processes = []
    main_pid = None
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.cmdline()
            if cmdline:
                # 将命令行转换为字符串，便于搜索
                cmd_str = ' '.join(cmdline)
                # 查找Django进程：包含manage.py或runserver或gunicorn的进程
                if 'manage.py' in cmd_str or 'runserver' in cmd_str or 'gunicorn' in cmd_str:
                    django_processes.append(proc)
                    # 确定主进程（包含manage.py或gunicorn的进程）
                    if any('manage.py' in arg for arg in cmdline) or any('gunicorn' in arg for arg in cmdline):
                        main_pid = proc.pid
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return django_processes, main_pid

def monitor_processes(duration=300, interval=5):
    """监控Django进程的资源使用情况"""
    start_time = time.time()
    end_time = start_time + duration
    logger.info(f"开始监控Django服务资源使用情况，持续时间: {duration}秒，检查间隔: {interval}秒")
    
    while time.time() < end_time:
        processes, main_pid = find_django_process()
        if not processes:
            logger.warning("未找到Django进程")
            time.sleep(interval)
            continue
        
        total_cpu = 0.0
        total_memory = 0.0
        
        for proc in processes:
            try:
                # 获取CPU使用率（间隔0.1秒采样）
                proc_cpu = proc.cpu_percent(interval=0.1)
                # 获取内存使用量（MB）
                proc_memory = proc.memory_info().rss / (1024 * 1024)
                total_cpu += proc_cpu
                total_memory += proc_memory
                
                logger.info(f"进程PID: {proc.pid}, CPU: {proc_cpu:.2f}%, 内存: {proc_memory:.2f} MB")
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        logger.info(f"总资源使用 - CPU: {total_cpu:.2f}%, 内存: {total_memory:.2f} MB")
        time.sleep(interval)
    
    logger.info("监控结束")

if __name__ == "__main__":
    # 默认监控5分钟，每5秒检查一次
    monitor_processes(duration=300, interval=5)