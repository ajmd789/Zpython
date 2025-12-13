import os
import sys
import subprocess
import time
import platform
import requests
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

# 配置参数
PROJECT_NAME = "zpython_django"  # 打包后可执行文件名
PORT = 5555                      # 部署端口
CHECK_URL = f"http://127.0.0.1:{PORT}/index/"  # 服务校验URL

# 跨平台配置
SYSTEM = platform.system()

# 日志配置
LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "run_test.log"
LOG_MAX_SIZE = 256 * 1024  # 256KB
LOG_BACKUP_COUNT = 5

# 创建日志文件夹
LOG_DIR.mkdir(exist_ok=True)

# 配置日志
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# 日志格式
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# 控制台处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# 文件处理器（带轮转功能）
file_handler = RotatingFileHandler(
    LOG_FILE,
    maxBytes=LOG_MAX_SIZE,
    backupCount=LOG_BACKUP_COUNT,
    encoding='utf-8'
)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

def run_cmd(cmd, desc="执行命令", shell=True, blocking=True):
    """跨平台执行命令，带日志输出"""
    logger.info(f"\n=== {desc} ===")
    logger.info(f"命令：{cmd}")
    
    if blocking:
        try:
            result = subprocess.run(
                cmd, shell=shell, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8", errors="ignore"
            )
            if result.returncode == 0:
                stdout_content = result.stdout[:200] if result.stdout else ""  # 处理None情况
                logger.info(f"成功：{stdout_content}...")  # 只打印前200字符，避免输出过长
                return True
            else:
                stderr_content = result.stderr if result.stderr else ""  # 处理None情况
                logger.error(f"失败：{stderr_content}")
                return False
        except Exception as e:
            logger.error(f"执行命令时出错：{str(e)}")
            return False
    else:
        # 非阻塞执行
        try:
            process = subprocess.Popen(
                cmd, shell=shell, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8", errors="ignore"
            )
            logger.info(f"命令已启动，进程ID：{process.pid}")
            return True
        except Exception as e:
            logger.error(f"命令启动失败：{str(e)}")
            return False

def start_service():
    """启动Django服务（后台运行）"""
    exe_path = Path("dist") / (f"{PROJECT_NAME}.exe" if SYSTEM == "Windows" else PROJECT_NAME)
    if not exe_path.exists():
        logger.error(f"打包产物不存在：{exe_path}")
        return False

    # 启动命令（后台运行）
    if SYSTEM == "Windows":
        # Windows后台运行（隐藏cmd窗口）
        start_cmd = f"start /b {exe_path} runserver 0.0.0.0:{PORT} --noreload"
    else:
        # Linux后台运行（nohup）
        start_cmd = f"nohup {exe_path} runserver 0.0.0.0:{PORT} --noreload > dist/server.log 2>&1 &"
    
    return run_cmd(start_cmd, f"启动服务到{PORT}端口", blocking=False)

def check_port_service():
    """检查5555端口是否有服务，且服务可正常访问"""
    logger.info(f"\n=== 检查{PORT}端口服务 ===")
    time.sleep(5)  # 等待服务启动（可根据项目启动速度调整）

    # 1. 检查端口是否被占用
    if SYSTEM == "Windows":
        port_check_cmd = f"netstat -ano | findstr :{PORT}"
    else:
        port_check_cmd = f"ss -tulpn | grep :{PORT} || netstat -tulpn | grep :{PORT}"
    
    if not run_cmd(port_check_cmd, "检查端口是否占用"):
        logger.error(f"{PORT}端口无服务运行")
        return False

    # 2. 检查服务是否正常响应
    try:
        response = requests.get(CHECK_URL, timeout=10)
        if response.status_code == 200:
            logger.info(f"成功：{CHECK_URL} 响应正常（状态码200）")
            return True
        else:
            logger.error(f"失败：{CHECK_URL} 响应状态码：{response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        logger.error(f"失败：无法连接到 {CHECK_URL}，服务可能未启动")
        return False
    except Exception as e:
        logger.error(f"失败：访问{CHECK_URL}出错：{str(e)}")
        return False

def stop_service():
    """停止Django服务"""
    logger.info(f"\n=== 停止{PORT}端口服务 ===")
    
    if SYSTEM == "Windows":
        # Windows停止服务
        # 先找到占用指定端口的进程ID
        port_check_cmd = f"netstat -ano | findstr :{PORT}"
        result = subprocess.run(
            port_check_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8"
        )
        
        if result.returncode == 0:
            # 解析进程ID
            lines = result.stdout.strip().split('\n')
            if lines:
                # 取最后一行的最后一个字段作为进程ID
                pid = lines[-1].strip().split()[-1]
                logger.info(f"找到占用{PORT}端口的进程ID：{pid}")
                
                # 终止进程
                kill_cmd = f"taskkill /F /PID {pid}"
                return run_cmd(kill_cmd, f"终止进程{pid}")
            else:
                logger.info(f"未找到占用{PORT}端口的进程")
                return True
        else:
            logger.error(f"检查端口占用时出错：{result.stderr}")
            return False
    else:
        # Linux停止服务
        # 找到占用指定端口的进程ID
        port_check_cmd = f"lsof -i :{PORT} | grep LISTEN | awk '{{print $2}}'"
        result = subprocess.run(
            port_check_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8"
        )
        
        if result.returncode == 0:
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid:
                    logger.info(f"找到占用{PORT}端口的进程ID：{pid}")
                    kill_cmd = f"kill -9 {pid}"
                    run_cmd(kill_cmd, f"终止进程{pid}")
            return True
        else:
            logger.info(f"未找到占用{PORT}端口的进程")
            return True

def main():
    """主流程：启动服务→校验服务→等待停止"""
    logger.info("===== Django项目测试运行工具 =====")
    
    # 检查打包产物是否存在
    exe_path = Path("dist") / (f"{PROJECT_NAME}.exe" if SYSTEM == "Windows" else PROJECT_NAME)
    if not exe_path.exists():
        logger.error(f"打包产物不存在：{exe_path}")
        logger.error("请先运行package.py进行打包")
        sys.exit(1)
    
    # 启动服务
    if not start_service():
        logger.error("服务启动失败")
        sys.exit(1)
    
    # 检查服务
    if not check_port_service():
        logger.error("服务检查失败")
        stop_service()
        sys.exit(1)
    
    logger.info(f"\n===== 服务启动成功！ =====")
    logger.info(f"服务已部署到：{CHECK_URL}")
    logger.info("按Ctrl+C停止服务...")
    
    # 等待用户终止
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("\n用户中断，停止服务")
        stop_service()
        logger.info("服务已停止")
        sys.exit(0)
    except Exception as e:
        logger.error(f"程序异常：{str(e)}")
        stop_service()
        sys.exit(1)

if __name__ == "__main__":
    main()
