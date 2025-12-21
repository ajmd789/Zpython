import os
import sys
import subprocess
import time
import platform
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import shutil

# 配置参数
PROJECT_NAME = "zpython_django"  # 项目名称
DJANGO_ENTRY = "manage.py"       # Django入口文件
PORT = 5555                      # 部署端口
CHECK_URL = f"http://127.0.0.1:{PORT}/index/"  # 服务校验URL
ASSETS_DIR = "assets"            # 静态资源目录
DB_FILE = "db.sqlite3"           # 数据库文件
VENV_NAME = "venv"               # 虚拟环境名称

# Gunicorn配置（生产环境）
GUNICORN_WORKERS = 2             # Worker数量（建议为CPU核心数的1-2倍）
GUNICORN_TIMEOUT = 30            # 超时时间（秒）
GUNICORN_BIND = f"0.0.0.0:{PORT}"  # 绑定地址和端口
WSGI_MODULE = "zproject.wsgi:application"  # WSGI应用模块路径

# 跨平台配置
SYSTEM = platform.system()
VENV_PYTHON = Path(VENV_NAME) / ("Scripts" if SYSTEM == "Windows" else "bin") / ("python.exe" if SYSTEM == "Windows" else "python3")
VENV_GUNICORN = Path(VENV_NAME) / ("Scripts" if SYSTEM == "Windows" else "bin") / "gunicorn"

# 日志配置
LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "package.log"
LOG_MAX_SIZE = 256 * 1024  # 256KB
LOG_BACKUP_COUNT = 5

# 项目根目录自动检测
PROJECT_ROOT = None

def find_project_root():
    """自动查找项目根目录"""
    global PROJECT_ROOT
    
    # 从当前脚本位置开始向上查找
    current_path = Path(__file__).parent
    
    # 查找包含manage.py和zproject目录的目录
    for path in [current_path, current_path.parent, current_path.parent.parent]:
        if (path / "manage.py").exists() and (path / "zproject").is_dir():
            PROJECT_ROOT = path
            logger.info(f"自动定位到项目根目录：{PROJECT_ROOT}")
            return True
    
    logger.error("无法找到项目根目录！请确保脚本位于项目目录或其子目录中。")
    return False

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

def run_cmd(cmd, desc="执行命令", cwd=None):
    """跨平台执行命令，带日志输出"""
    logger.info(f"\n=== {desc} ===")
    logger.info(f"命令：{cmd}")
    logger.info(f"工作目录：{cwd or os.getcwd()}")
    try:
        result = subprocess.run(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8", errors="ignore", cwd=cwd
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

def git_pull():
    """执行git pull更新代码"""
    if not PROJECT_ROOT:
        logger.error("项目根目录未设置，无法执行git pull")
        return False
    
    cmd = "git pull"
    return run_cmd(cmd, "拉取最新代码", cwd=PROJECT_ROOT)

def generate_requirements():
    """生成requirements.txt文件"""
    try:
        if not PROJECT_ROOT:
            logger.error("项目根目录未设置，无法生成requirements.txt")
            return False
            
        requirements_path = PROJECT_ROOT / "requirements.txt"
        
        # 生成requirements.txt
        cmd = f"pip freeze > {requirements_path}"
        return run_cmd(cmd, "生成requirements.txt", cwd=PROJECT_ROOT)
    except Exception as e:
        logger.error(f"生成requirements.txt失败：{str(e)}")
        return False

def create_venv():
    """创建虚拟环境"""
    if not PROJECT_ROOT:
        logger.error("项目根目录未设置，无法创建虚拟环境")
        return False
    
    venv_path = PROJECT_ROOT / VENV_NAME
    if venv_path.exists():
        logger.info(f"虚拟环境已存在：{venv_path}")
        logger.info("正在重新创建虚拟环境...")
        shutil.rmtree(venv_path)
    
    venv_cmd = f"python -m venv {VENV_NAME}"
    return run_cmd(venv_cmd, "创建虚拟环境", cwd=PROJECT_ROOT)

def install_deps():
    """安装项目依赖"""
    if not PROJECT_ROOT:
        logger.error("项目根目录未设置，无法安装依赖")
        return False
    
    # 更新虚拟环境路径为绝对路径
    venv_python = PROJECT_ROOT / VENV_NAME / ("Scripts" if SYSTEM == "Windows" else "bin") / ("python.exe" if SYSTEM == "Windows" else "python3")
    deps_cmd = f"{venv_python} -m pip install --upgrade pip && {venv_python} -m pip install -r requirements.txt gunicorn"
    return run_cmd(deps_cmd, "安装项目依赖和gunicorn", cwd=PROJECT_ROOT)

def generate_deploy_files():
    """生成部署相关文件"""
    if not PROJECT_ROOT:
        logger.error("项目根目录未设置，无法生成部署文件")
        return False
    # 生成Linux启动脚本（gunicorn）
    linux_script = f"""#!/bin/bash
# Django项目生产环境启动脚本

# 进入脚本所在目录
cd "$(dirname "$0")"

# 激活虚拟环境
source ../{VENV_NAME}/bin/activate

echo "=== 启动Django生产服务器（Gunicorn） ==="
echo "监听地址: {GUNICORN_BIND}"
echo "Worker数量: {GUNICORN_WORKERS}"
echo "超时时间: {GUNICORN_TIMEOUT}秒"
echo ""

# 使用gunicorn启动生产服务器
gunicorn {WSGI_MODULE} \
    --bind {GUNICORN_BIND} \
    --workers {GUNICORN_WORKERS} \
    --timeout {GUNICORN_TIMEOUT} \
    --log-level info \
    --access-logfile access.log \
    --error-logfile error.log &

# 启动服务监控脚本
echo "启动服务监控脚本..."
python ../monitor_server.py &

echo ""
echo "=== 服务已启动 ==="
echo "访问地址: http://$(hostname -I | awk '{{print $1}}'):{PORT}"
echo ""
echo "若要设置开机自启，请运行："
echo "sudo ./install_systemd_service.sh"
"""
    
    # 生成Windows启动脚本（开发用runserver）
    windows_script = f"""@echo off
REM Django项目启动脚本

cd /d "%~dp0"

REM 激活虚拟环境
call ..\\{VENV_NAME}\\Scripts\\activate.bat

echo === 启动Django服务器 ===
echo 监听地址: {GUNICORN_BIND}
echo.

REM 使用Django开发服务器（Windows环境）
echo 启动Django服务器...
start "Django Server" python {DJANGO_ENTRY} runserver {GUNICORN_BIND} --noreload

REM 启动服务监控脚本
echo 启动服务监控脚本...
start "Server Monitor" python monitor_server.py

echo.
echo === 服务已启动 ===
"""
    
    # 生成systemd服务配置文件（Django应用）
    systemd_service = f"""[Unit]
Description=Zpython Django Application
After=network.target

[Service]
User={os.getlogin() if os.getlogin() != 'SYSTEM' else 'ubuntu'}
Group={os.getlogin() if os.getlogin() != 'SYSTEM' else 'ubuntu'}
WorkingDirectory={PROJECT_ROOT}
ExecStart={PROJECT_ROOT}/{VENV_NAME}/bin/gunicorn {WSGI_MODULE} --bind {GUNICORN_BIND} --workers {GUNICORN_WORKERS} --timeout {GUNICORN_TIMEOUT}
Restart=always

[Install]
WantedBy=multi-user.target
"""
    
    # 生成systemd服务配置文件（监控脚本）
    monitor_systemd_service = f"""[Unit]
Description=Zpython Server Monitor
After=network.target zpython.service
Requires=zpython.service

[Service]
User={os.getlogin() if os.getlogin() != 'SYSTEM' else 'ubuntu'}
Group={os.getlogin() if os.getlogin() != 'SYSTEM' else 'ubuntu'}
WorkingDirectory={PROJECT_ROOT}
ExecStart={PROJECT_ROOT}/{VENV_NAME}/bin/python {PROJECT_ROOT}/monitor_server.py
Restart=always

[Install]
WantedBy=multi-user.target
"""
    
    # 生成systemd服务安装脚本
    systemd_install_script = f"""#!/bin/bash
# Systemd服务安装脚本

echo "=== 安装Zpython Systemd服务 ==="

# 复制服务文件到systemd目录
sudo cp zpython.service /etc/systemd/system/
sudo cp zpython-monitor.service /etc/systemd/system/

# 重新加载systemd配置
sudo systemctl daemon-reload

# 启用服务（开机自启）
sudo systemctl enable zpython zpython-monitor

# 启动服务
sudo systemctl start zpython zpython-monitor

echo ""
echo "=== Systemd服务安装完成！ ==="
echo "Django应用服务状态："
sudo systemctl status zpython --no-pager
echo ""
echo "监控服务状态："
sudo systemctl status zpython-monitor --no-pager
"""

    try:
        # 确保dist目录存在
        dist_dir = PROJECT_ROOT / "dist"
        dist_dir.mkdir(exist_ok=True)
        
        # 保存Linux启动脚本
        linux_script_path = dist_dir / "start_production.sh"
        linux_script_path.write_text(linux_script, encoding="utf-8")
        linux_script_path.chmod(0o755)  # 添加执行权限
        logger.info(f"生成Linux启动脚本: {linux_script_path}")

        # 保存Windows启动脚本
        windows_script_path = dist_dir / "start_server.bat"
        windows_script_path.write_text(windows_script, encoding="utf-8")
        logger.info(f"生成Windows启动脚本: {windows_script_path}")
        
        # 保存systemd服务配置文件
        systemd_path = dist_dir / "zpython.service"
        systemd_path.write_text(systemd_service, encoding="utf-8")
        logger.info(f"生成Systemd服务配置: {systemd_path}")
        
        # 保存监控服务配置文件
        monitor_systemd_path = dist_dir / "zpython-monitor.service"
        monitor_systemd_path.write_text(monitor_systemd_service, encoding="utf-8")
        logger.info(f"生成监控服务配置: {monitor_systemd_path}")
        
        # 保存systemd服务安装脚本
        systemd_install_path = dist_dir / "install_systemd_service.sh"
        systemd_install_path.write_text(systemd_install_script, encoding="utf-8")
        systemd_install_path.chmod(0o755)  # 添加执行权限
        logger.info(f"生成Systemd服务安装脚本: {systemd_install_path}")

        return True
    except Exception as e:
        logger.error(f"生成部署文件失败: {str(e)}")
        return False

def start_production_service():
    """启动生产环境服务"""
    if not PROJECT_ROOT:
        logger.error("项目根目录未设置，无法启动服务")
        return False
    
    dist_dir = PROJECT_ROOT / "dist"
    if not dist_dir.exists():
        logger.error(f"dist目录不存在：{dist_dir}")
        return False
    
    start_script = dist_dir / "start_production.sh"
    if not start_script.exists():
        logger.error(f"启动脚本不存在：{start_script}")
        return False
    
    cmd = f"./{start_script.name}"
    return run_cmd(cmd, "启动生产环境服务", cwd=dist_dir)

def install_systemd_service():
    """安装Systemd服务"""
    if not PROJECT_ROOT:
        logger.error("项目根目录未设置，无法安装Systemd服务")
        return False
    
    dist_dir = PROJECT_ROOT / "dist"
    if not dist_dir.exists():
        logger.error(f"dist目录不存在：{dist_dir}")
        return False
    
    install_script = dist_dir / "install_systemd_service.sh"
    if not install_script.exists():
        logger.error(f"Systemd安装脚本不存在：{install_script}")
        return False
    
    cmd = f"sudo ./{install_script.name}"
    return run_cmd(cmd, "安装Systemd服务", cwd=dist_dir)

def main():
    """主流程：自动定位项目→拉取代码→创建虚拟环境→安装依赖→生成部署文件→启动服务→安装Systemd服务"""
    logger.info("===== Django项目部署工具 =====")
    
    # 自动定位项目根目录
    if not find_project_root():
        logger.error("\n===== 流程终止：无法找到项目根目录 =====")
        sys.exit(1)
    
    steps = [
        ("拉取最新代码", git_pull),
        ("生成requirements.txt", generate_requirements),
        ("创建虚拟环境", create_venv),
        ("安装依赖", install_deps),
        ("生成部署文件", generate_deploy_files),
        ("启动生产环境服务", start_production_service),
        ("安装Systemd服务", install_systemd_service)
    ]

    for step_name, step_func in steps:
        if not step_func():
            logger.error(f"\n===== 流程终止：{step_name}失败 =====")
            sys.exit(1)

    logger.info(f"\n===== 部署完成！ =====")
    logger.info(f"项目名称：{PROJECT_NAME}")
    logger.info(f"项目目录：{PROJECT_ROOT}")
    logger.info(f"虚拟环境：{VENV_NAME}")
    logger.info(f"部署端口：{PORT}")
    logger.info(f"访问地址：http://127.0.0.1:{PORT}/index/")
    logger.info(f"\n所有操作已完成：")
    logger.info(f"  ✓ 自动定位到项目根目录")
    logger.info(f"  ✓ 拉取最新代码")
    logger.info(f"  ✓ 创建虚拟环境并安装依赖")
    logger.info(f"  ✓ 生成部署文件")
    logger.info(f"  ✓ 启动生产环境服务")
    logger.info(f"  ✓ 安装Systemd服务（开机自启）")
    logger.info(f"\n日志文件：{LOG_FILE}")

def generate_only():
    """只生成部署文件，用于测试"""
    logger.info("===== 只生成部署文件 =====")
    
    # 自动定位项目根目录
    if not find_project_root():
        logger.error("\n===== 流程终止：无法找到项目根目录 =====")
        sys.exit(1)
    
    if generate_deploy_files():
        logger.info("\n===== 部署文件生成成功！ =====")
    else:
        logger.error("\n===== 部署文件生成失败！ =====")
        sys.exit(1)

if __name__ == "__main__":
    # 检查是否有参数，支持只生成部署文件
    if len(sys.argv) > 1 and sys.argv[1] == "--generate-only":
        generate_only()
    else:
        main()
