#!/usr/bin/env python3
"""
Django项目一键部署脚本
功能：自动检测环境、创建虚拟环境、安装依赖、打包项目、启动服务、设置开机自启
服务器端专用版本
"""

import os
import sys
import subprocess
import time
import platform
import logging
import traceback
from logging.handlers import RotatingFileHandler
from pathlib import Path
import shutil
import json

# 确保使用Python3
if sys.version_info[0] < 3:
    print("错误：需要使用Python 3运行此脚本")
    sys.exit(1)

# 配置参数
PROJECT_NAME = "zpython_django"  # 项目名称
DJANGO_ENTRY = "manage.py"       # Django入口文件
PORT = 5555                      # 部署端口
CHECK_URL = f"http://127.0.0.1:{PORT}/index/"  # 服务校验URL
ASSETS_DIR = "assets"            # 静态资源目录
DB_FILE = "db.sqlite3"           # 数据库文件
VENV_NAME = "venv"               # 虚拟环境名称

# WSGI配置
WSGI_MODULE = "zproject.wsgi:application"  # WSGI模块
GUNICORN_BIND = f"0.0.0.0:{PORT}"          # Gunicorn绑定地址
GUNICORN_WORKERS = 2                       # Worker数量
GUNICORN_TIMEOUT = 30                      # 超时时间（秒）

# 日志配置
def setup_logger():
    """配置日志系统"""
    logger = logging.getLogger('package')
    logger.setLevel(logging.DEBUG)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # 文件处理器
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    file_handler = RotatingFileHandler(
        log_dir / 'package.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    
    # 格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

logger = setup_logger()

# 全局变量
PROJECT_ROOT = None

def get_project_root():
    """获取项目根目录"""
    global PROJECT_ROOT
    if PROJECT_ROOT:
        return PROJECT_ROOT
    
    # 尝试多种方式定位项目根目录
    current_dir = Path.cwd()
    
    # 方法1: 检查当前目录是否包含manage.py
    if (current_dir / DJANGO_ENTRY).exists():
        PROJECT_ROOT = str(current_dir)
        return PROJECT_ROOT
    
    # 方法2: 向上查找包含manage.py的目录
    for parent in current_dir.parents:
        if (parent / DJANGO_ENTRY).exists():
            PROJECT_ROOT = str(parent)
            return PROJECT_ROOT
    
    # 方法3: 检查脚本所在目录
    script_dir = Path(__file__).parent.parent
    if (script_dir / DJANGO_ENTRY).exists():
        PROJECT_ROOT = str(script_dir)
        return PROJECT_ROOT
    
    logger.error(f"无法找到项目根目录（包含{DJANGO_ENTRY}的目录）")
    return None

def check_virtual_environment():
    """检查虚拟环境状态"""
    logger.info("检查虚拟环境...")
    
    venv_path = Path(PROJECT_ROOT) / VENV_NAME
    
    # 检查虚拟环境是否已激活
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        logger.info("虚拟环境已激活")
        return True
    
    # 检查虚拟环境是否存在
    if venv_path.exists():
        logger.info(f"检测到虚拟环境目录: {venv_path}")
        logger.warning("虚拟环境未激活")
        
        # 根据操作系统提示不同的激活命令
        if platform.system() == 'Windows':
            logger.info(f"请运行: {VENV_NAME}\Scripts\activate")
        else:
            logger.info(f"请运行: source {VENV_NAME}/bin/activate")
        
        # 在Windows开发环境下，允许跳过虚拟环境检查继续执行
        if platform.system() == 'Windows':
            logger.info("Windows开发环境下，跳过虚拟环境检查继续执行...")
            return True
        
        return False
    
    # 虚拟环境不存在，询问是否创建
    logger.info("未检测到虚拟环境")
    response = input("是否创建新的虚拟环境? (y/n): ").strip().lower()
    
    if response == 'y':
        return create_virtual_environment()
    else:
        logger.error("需要虚拟环境才能继续")
        return False

def create_virtual_environment():
    """创建虚拟环境"""
    logger.info("创建虚拟环境...")
    
    venv_path = Path(PROJECT_ROOT) / VENV_NAME
    
    try:
        # 使用venv模块创建虚拟环境
        import venv
        logger.info(f"正在创建虚拟环境: {venv_path}")
        venv.create(venv_path, with_pip=True)
        logger.info("虚拟环境创建成功")
        
        # 提示用户激活虚拟环境
        logger.info("请激活虚拟环境后重新运行脚本:")
        logger.info(f"  source {VENV_NAME}/bin/activate")
        logger.info("  python3 scripts/package.py --generate-only")
        
        return False  # 需要用户手动激活后重新运行
        
    except Exception as e:
        logger.error(f"创建虚拟环境失败: {e}")
        return False

def install_dependencies():
    """安装项目依赖"""
    logger.info("安装项目依赖...")
    
    requirements_file = Path(PROJECT_ROOT) / "requirements.txt"
    if not requirements_file.exists():
        logger.warning(f"未找到{requirements_file}，跳过依赖安装")
        return True
    
    try:
        # 检查pip是否可用
        result = subprocess.run([sys.executable, "-m", "pip", "--version"], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            logger.error("pip不可用，无法安装依赖")
            return False
        
        logger.info("正在安装依赖包...")
        # 使用pip安装requirements.txt中的依赖
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ], capture_output=True, text=True, cwd=PROJECT_ROOT)
        
        if result.returncode == 0:
            logger.info("依赖安装成功")
            return True
        else:
            logger.error(f"依赖安装失败: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"安装依赖失败: {e}")
        return False

def check_django_setup():
    """检查Django配置"""
    logger.info("检查Django配置...")
    
    try:
        # 确保项目根目录在Python路径中
        if PROJECT_ROOT not in sys.path:
            sys.path.insert(0, PROJECT_ROOT)
            logger.debug(f"已将项目根目录添加到Python路径: {PROJECT_ROOT}")
        
        # 检查是否能导入Django
        import django
        logger.info(f"Django版本: {django.VERSION}")
        
        # 设置Django环境
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zproject.settings')
        django.setup()
        
        # 检查数据库连接
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        logger.info("数据库连接正常")
        
        return True
        
    except Exception as e:
        logger.error(f"Django配置检查失败: {e}")
        return False

def collect_static_files():
    """收集静态文件"""
    logger.info("收集静态文件...")
    
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zproject.settings')
        
        # 运行collectstatic命令
        # 确保在子进程中也能找到项目模块
        env = os.environ.copy()
        if PROJECT_ROOT not in sys.path:
            pythonpath = PROJECT_ROOT
        else:
            pythonpath = ':'.join([PROJECT_ROOT] + sys.path)
        env['PYTHONPATH'] = pythonpath
        
        result = subprocess.run([
            sys.executable, DJANGO_ENTRY, "collectstatic", "--noinput"
        ], capture_output=True, text=True, cwd=PROJECT_ROOT, env=env)
        
        if result.returncode == 0:
            logger.info("静态文件收集成功")
            return True
        else:
            logger.warning(f"静态文件收集失败: {result.stderr}")
            return False  # 不是致命错误，可以继续
            
    except Exception as e:
        logger.warning(f"静态文件收集失败: {e}")
        return False  # 不是致命错误，可以继续

def generate_startup_scripts():
    """生成启动脚本"""
    logger.info("生成启动脚本...")
    
    # 确保dist目录存在
    dist_dir = Path(PROJECT_ROOT) / "dist"
    dist_dir.mkdir(exist_ok=True)
    
    # 生成Linux启动脚本（gunicorn）
    linux_script = f"""#!/bin/bash
# Django项目一键部署启动脚本 - 完整修复版

# 进入脚本所在目录
cd "$(dirname "$0")"
SCRIPT_DIR=$(pwd)

# 计算项目根目录（dist的父目录）
PROJECT_ROOT=$(cd "$SCRIPT_DIR/.." && pwd)
echo "项目根目录: $PROJECT_ROOT"

# 激活虚拟环境
if [ -f "$PROJECT_ROOT/{VENV_NAME}/bin/activate" ]; then
    source $PROJECT_ROOT/{VENV_NAME}/bin/activate
    echo "虚拟环境已激活"
else
    echo "错误：虚拟环境不存在！请先运行部署脚本创建虚拟环境。"
    exit 1
fi

echo "=== 启动Django生产服务器（Gunicorn） ==="
echo "监听地址: {GUNICORN_BIND}"
echo "Worker数量: {GUNICORN_WORKERS}"
echo "超时时间: {GUNICORN_TIMEOUT}秒"
echo ""

# 使用gunicorn启动生产服务器
echo "正在启动Gunicorn..."
gunicorn {WSGI_MODULE} \
    --bind {GUNICORN_BIND} \
    --workers {GUNICORN_WORKERS} \
    --timeout {GUNICORN_TIMEOUT} \
    --log-level debug \
    --access-logfile access.log \
    --error-logfile error.log \
    --pythonpath "$PROJECT_ROOT" \
    --chdir "$PROJECT_ROOT" > gunicorn_start.log 2>&1 &

# 获取Gunicorn进程ID
GUNICORN_PID=$!
echo "Gunicorn进程ID: $GUNICORN_PID"

# 等待Gunicorn启动
sleep 3

# 检查Gunicorn是否成功启动
if kill -0 $GUNICORN_PID 2>/dev/null; then
    echo "Gunicorn启动成功！"
    echo "服务正在运行，访问地址: http://{GUNICORN_BIND}"
    echo "日志文件: access.log, error.log"
else
    echo "✗ Gunicorn启动失败！"
    echo "查看错误日志:"
    tail -n 20 gunicorn_start.log
    exit 1
fi

# 启动服务监控脚本
echo "启动服务监控脚本..."
python "$(dirname "$(dirname "$0")")/monitor_server.py" > monitor_start.log 2>&1 &

if [ $? -eq 0 ]; then
    echo "监控脚本启动成功"
else
    echo "监控脚本启动失败（非致命错误）"
fi

echo ""
echo "=== 部署完成！ ==="
echo "服务状态检查命令:"
echo "  查看Gunicorn进程: ps aux | grep gunicorn"
echo "  查看监听端口: netstat -tlnp | grep {PORT}"
echo "  查看访问日志: tail -f access.log"
echo "  查看错误日志: tail -f error.log"
echo "  测试服务: curl http://localhost:{PORT}"
"""
    
    # 生成停止脚本
    stop_script = f"""#!/bin/bash
# Django项目停止脚本

echo "=== 停止Django服务 ==="

# 停止Gunicorn进程
echo "停止Gunicorn进程..."
pkill -f gunicorn

# 停止监控脚本
echo "停止监控脚本..."
pkill -f monitor_server.py

# 等待进程结束
sleep 2

# 检查是否还有残留进程
echo "检查残留进程..."
remaining_gunicorn=$(pgrep -f gunicorn | wc -l)
remaining_monitor=$(pgrep -f monitor_server.py | wc -l)

if [ $remaining_gunicorn -eq 0 ] && [ $remaining_monitor -eq 0 ]; then
    echo "所有服务已停止"
else
    echo "发现残留进程，强制终止..."
    pkill -9 -f gunicorn
    pkill -9 -f monitor_server.py
    echo "残留进程已终止"
fi

echo "服务停止完成！"
"""
    
    # 写入文件
    linux_script_path = Path(PROJECT_ROOT) / "dist" / "start_production.sh"
    stop_script_path = Path(PROJECT_ROOT) / "dist" / "stop_production.sh"
    
    try:
        # Linux启动脚本
        with open(linux_script_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(linux_script)
        os.chmod(linux_script_path, 0o755)  # 设置可执行权限
        logger.info(f"生成Linux启动脚本: {linux_script_path}")
        
        # Linux停止脚本
        with open(stop_script_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(stop_script)
        os.chmod(stop_script_path, 0o755)  # 设置可执行权限
        logger.info(f"生成Linux停止脚本: {stop_script_path}")
        
        return True
    except Exception as e:
        logger.error(f"生成启动脚本失败: {e}")
        return False

def generate_systemd_services():
    """生成systemd服务配置"""
    logger.info("生成systemd服务配置...")
    
    dist_dir = Path(PROJECT_ROOT) / "dist"
    dist_dir.mkdir(exist_ok=True)
    
    # 检测系统用户
    try:
        import getpass
        user = getpass.getuser()
    except:
        user = "ubuntu"  # 默认用户
    
    # Systemd服务配置（Django应用）
    systemd_service = f"""[Unit]
Description=Zpython Django Application
After=network.target

[Service]
Type=forking
User={user}
Group={user}
WorkingDirectory={PROJECT_ROOT}
ExecStartPre=/bin/sleep 2
ExecStart={PROJECT_ROOT}/dist/start_production.sh
ExecStop={PROJECT_ROOT}/dist/stop_production.sh
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=10
KillMode=mixed
TimeoutStartSec=60
TimeoutStopSec=30

[Install]
WantedBy=multi-user.target
"""
    
    # 监控服务配置
    monitor_service = f"""[Unit]
Description=Zpython Monitor Service
After=network.target zpython.service

[Service]
Type=simple
User={user}
Group={user}
WorkingDirectory={PROJECT_ROOT}
ExecStartPre=/bin/sleep 5
ExecStart={PROJECT_ROOT}/{VENV_NAME}/bin/python {PROJECT_ROOT}/monitor_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
    
    # 一键安装脚本
    install_script = f"""#!/bin/bash
# Zpython Systemd服务一键安装脚本

set -e

echo "==========================================="
echo "  Zpython Systemd服务安装工具"
echo "==========================================="

# 获取当前目录的绝对路径
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
SERVICE_NAME="zpython"
MONITOR_SERVICE_NAME="zpython-monitor"

echo "项目根目录: $PROJECT_ROOT"
echo ""

# 检查systemd是否可用
if ! command -v systemctl &> /dev/null; then
    echo "错误：systemctl命令不可用，当前系统不支持systemd"
    exit 1
fi

echo "1. 检查服务文件..."
if [ ! -f "$SCRIPT_DIR/zpython.service" ] || [ ! -f "$SCRIPT_DIR/zpython-monitor.service" ]; then
    echo "错误：服务文件不存在，请先运行部署脚本生成服务文件"
    exit 1
fi

echo "2. 停止并禁用现有服务（如果存在）..."
sudo systemctl stop $SERVICE_NAME $MONITOR_SERVICE_NAME 2>/dev/null || true
sudo systemctl disable $SERVICE_NAME $MONITOR_SERVICE_NAME 2>/dev/null || true

echo "3. 安装服务文件..."
sudo cp "$SCRIPT_DIR/zpython.service" /etc/systemd/system/
sudo cp "$SCRIPT_DIR/zpython-monitor.service" /etc/systemd/system/

echo "4. 重新加载systemd配置..."
sudo systemctl daemon-reload

echo "5. 启用服务开机自启..."
sudo systemctl enable $SERVICE_NAME
sudo systemctl enable $MONITOR_SERVICE_NAME

echo "6. 启动服务..."
sudo systemctl start $SERVICE_NAME
sleep 3
sudo systemctl start $MONITOR_SERVICE_NAME

echo "7. 检查服务状态..."
echo ""
echo "主服务状态:"
sudo systemctl status $SERVICE_NAME --no-pager -l

echo ""
echo "监控服务状态:"
sudo systemctl status $MONITOR_SERVICE_NAME --no-pager -l

echo ""
echo "==========================================="
echo "  服务安装完成！"
echo "==========================================="
echo ""
echo "服务管理命令："
echo "  启动服务:   sudo systemctl start $SERVICE_NAME $MONITOR_SERVICE_NAME"
echo "  停止服务:   sudo systemctl stop $SERVICE_NAME $MONITOR_SERVICE_NAME"
echo "  重启服务:   sudo systemctl restart $SERVICE_NAME $MONITOR_SERVICE_NAME"
echo "  查看状态:   sudo systemctl status $SERVICE_NAME --no-pager"
echo "  查看日志:   sudo journalctl -u $SERVICE_NAME -f"
echo "  开机自启:   sudo systemctl enable $SERVICE_NAME $MONITOR_SERVICE_NAME"
echo ""
echo "测试服务："
echo "  curl http://localhost:{PORT}"
echo "  curl http://$(hostname -I | awk '{{print $1}}'):{PORT}"
echo ""
echo "如果服务启动失败，请检查日志："
echo "  sudo journalctl -u $SERVICE_NAME -n 50 --no-pager"
echo "  tail -f {PROJECT_ROOT}/error.log"
"""
    
    # 写入文件
    service_files = {
        "zpython.service": systemd_service,
        "zpython-monitor.service": monitor_service,
        "install_systemd_service.sh": install_script
    }
    
    try:
        for filename, content in service_files.items():
            file_path = dist_dir / filename
            with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(content)
            
            if filename.endswith('.sh'):
                os.chmod(file_path, 0o755)  # 设置可执行权限
            
            logger.info(f"生成服务配置: {file_path}")
        
        return True
    except Exception as e:
        logger.error(f"生成systemd服务配置失败: {e}")
        return False

def test_service():
    """测试服务是否正常运行"""
    logger.info("测试服务运行状态...")
    
    try:
        import requests
        
        # 等待服务启动
        logger.info("等待服务启动...")
        time.sleep(5)
        
        # 测试本地访问
        response = requests.get(f"http://127.0.0.1:{PORT}/", timeout=10)
        
        if response.status_code == 200:
            logger.info("服务测试成功！")
            logger.info(f"响应状态码: {response.status_code}")
            return True
        else:
            logger.warning(f"服务返回异常状态码: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        logger.error("无法连接到服务，可能启动失败")
        return False
    except Exception as e:
        logger.error(f"服务测试失败: {e}")
        return False

def create_deploy_summary():
    """创建部署摘要"""
    logger.info("创建部署摘要...")
    
    summary = f"""
# Django项目部署摘要

## 项目信息
- 项目名称: {PROJECT_NAME}
- 项目路径: {PROJECT_ROOT}
- 部署端口: {PORT}
- 虚拟环境: {VENV_NAME}

## 部署状态
- 部署时间: {time.strftime('%Y-%m-%d %H:%M:%S')}
- Python版本: {sys.version}
- 操作系统: {platform.system()} {platform.release()}

## 文件生成
启动脚本: dist/start_production.sh
停止脚本: dist/stop_production.sh  
服务配置: dist/zpython.service
监控配置: dist/zpython-monitor.service
安装脚本: dist/install_systemd_service.sh

## 使用说明

### 手动启动服务
```bash
cd {PROJECT_ROOT}
bash dist/start_production.sh
```

### 设置开机自启（推荐）
```bash
cd {PROJECT_ROOT}
sudo bash dist/install_systemd_service.sh
```

### 服务管理命令
```bash
# 查看状态
sudo systemctl status zpython zpython-monitor

# 启动服务
sudo systemctl start zpython zpython-monitor

# 停止服务  
sudo systemctl stop zpython zpython-monitor

# 重启服务
sudo systemctl restart zpython zpython-monitor

# 查看日志
sudo journalctl -u zpython -f
```

### 测试服务
```bash
# 本地测试
curl http://localhost:{PORT}

# 远程测试
curl http://$(hostname -I | awk '{{print $1}}'):{PORT}
```

### 日志文件
- 访问日志: {PROJECT_ROOT}/access.log
- 错误日志: {PROJECT_ROOT}/error.log
- 启动日志: {PROJECT_ROOT}/gunicorn_start.log

## 故障排除

如果服务启动失败：
1. 检查错误日志: tail -f error.log
2. 检查系统日志: sudo journalctl -u zpython -n 50
3. 手动测试: bash dist/start_production.sh
4. 运行诊断: python manage.py check

## 技术支持
- 确保虚拟环境已激活
- 检查防火墙设置（端口{PORT}）
- 确认所有依赖已安装
- 验证数据库连接正常
"""
    
    try:
        summary_path = Path(PROJECT_ROOT) / "dist" / "DEPLOYMENT_SUMMARY.md"
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        logger.info(f"部署摘要已生成: {summary_path}")
        return True
    except Exception as e:
        logger.error(f"生成部署摘要失败: {e}")
        return False

def full_deployment():
    """完整的一键部署流程"""
    logger.info("=" * 60)
    logger.info("    Django项目一键部署工具")
    logger.info("=" * 60)
    
    # 1. 检查项目根目录
    if not get_project_root():
        logger.error("无法确定项目根目录")
        return False
    
    logger.info(f"项目根目录: {PROJECT_ROOT}")
    
    # 2. 检查虚拟环境
    if not check_virtual_environment():
        return False
    
    # 3. 安装依赖
    if not install_dependencies():
        logger.error("依赖安装失败，继续生成部署文件...")
    
    # 4. 检查Django配置
    if not check_django_setup():
        logger.warning("Django配置检查失败，继续生成部署文件...")
    
    # 5. 收集静态文件
    collect_static_files()
    
    # 6. 生成启动脚本
    if not generate_startup_scripts():
        logger.error("生成启动脚本失败")
        return False
    
    # 7. 生成systemd服务
    if not generate_systemd_services():
        logger.error("生成systemd服务失败")
        return False
    
    # 8. 创建部署摘要
    create_deploy_summary()
    
    logger.info("=" * 60)
    logger.info("    部署文件生成完成！")
    logger.info("=" * 60)
    
    print(f"\n{'=' * 60}")
    print("    一键部署准备就绪！")
    print(f"{'=' * 60}")
    print(f"\n项目路径: {PROJECT_ROOT}")
    print(f"部署端口: {PORT}")
    print(f"虚拟环境: {VENV_NAME}")
    print(f"\n下一步操作:")
    print(f"1. 手动启动: bash dist/start_production.sh")
    print(f"2. 设置开机自启: sudo bash dist/install_systemd_service.sh")
    print(f"3. 查看部署摘要: cat dist/DEPLOYMENT_SUMMARY.md")
    print(f"\n日志文件:")
    print(f"- 部署日志: {PROJECT_ROOT}/logs/package.log")
    print(f"- 服务日志: {PROJECT_ROOT}/access.log, {PROJECT_ROOT}/error.log")
    
    return True

def main():
    """主函数"""
    try:
        # 检查命令行参数
        if len(sys.argv) > 1 and sys.argv[1] == "--generate-only":
            logger.info("===== 只生成部署文件 =====")
            success = full_deployment()
            if success:
                print("\n===== 部署文件生成成功！ =====")
            else:
                print("\n===== 部署文件生成失败！ =====")
                sys.exit(1)
        else:
            # 完整部署流程
            logger.info("===== Django项目一键部署工具 =====")
            success = full_deployment()
            if success:
                print("\n===== 部署完成！ =====")
            else:
                print("\n===== 部署失败！ =====")
                sys.exit(1)
    
    except KeyboardInterrupt:
        logger.info("\n用户中断操作")
        sys.exit(0)
    except Exception as e:
        logger.error(f"发生未预期的错误: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()