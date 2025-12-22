#!/usr/bin/env python3
"""
Django项目打包部署脚本 - 服务器专用版本
用于在Linux服务器上生成部署文件
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

# WSGI配置
WSGI_MODULE = "zproject.wsgi:application"  # WSGI模块
GUNICORN_BIND = f"0.0.0.0:{PORT}"          # Gunicorn绑定地址
GUNICORN_WORKERS = 2                       # Worker数量
GUNICORN_TIMEOUT = 30                      # 超时时间（秒）

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

def check_dependencies():
    """检查依赖项"""
    logger.info("检查依赖项...")
    
    # 检查requirements.txt是否存在
    requirements_file = Path(PROJECT_ROOT) / "requirements.txt"
    if not requirements_file.exists():
        logger.warning(f"未找到{requirements_file}，跳过依赖检查")
        return True
    
    # 检查关键依赖
    critical_deps = ["django", "gunicorn"]
    missing_deps = []
    
    try:
        import pkg_resources
        with open(requirements_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    try:
                        pkg_resources.require(line)
                        logger.debug(f"依赖项检查通过: {line}")
                    except (pkg_resources.DistributionNotFound, pkg_resources.VersionConflict):
                        package_name = line.split('>=')[0].split('==')[0].split('<')[0]
                        if any(dep in package_name.lower() for dep in critical_deps):
                            missing_deps.append(line)
                            logger.error(f"缺少关键依赖: {line}")
                        else:
                            logger.warning(f"依赖项问题: {line}")
    except ImportError:
        logger.warning("无法导入pkg_resources，跳过详细依赖检查")
    except Exception as e:
        logger.error(f"依赖检查失败: {e}")
    
    if missing_deps:
        logger.error(f"缺少关键依赖项: {missing_deps}")
        return False
    
    logger.info("依赖项检查完成")
    return True

def generate_startup_scripts():
    """生成启动脚本"""
    logger.info("生成启动脚本...")
    
    # 确保dist目录存在
    dist_dir = Path(PROJECT_ROOT) / "dist"
    dist_dir.mkdir(exist_ok=True)
    
    # 生成Linux启动脚本（gunicorn）
    linux_script = f"""#!/bin/bash
# Django项目生产环境启动脚本 - 服务器专用修复版

# 进入脚本所在目录
cd "$(dirname "$0")"

# 激活虚拟环境
source ../{VENV_NAME}/bin/activate > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "错误：无法激活虚拟环境！"
    exit 1
fi

echo "=== 启动Django生产服务器（Gunicorn） ==="
echo "监听地址: {GUNICORN_BIND}"
echo "Worker数量: {GUNICORN_WORKERS}"
echo "超时时间: {GUNICORN_TIMEOUT}秒"
echo ""

# 计算项目根目录
PROJECT_ROOT=$(cd "$(dirname "$(dirname "$0")")" && pwd)
echo "项目根目录: $PROJECT_ROOT"

# 设置PYTHONPATH环境变量
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"
echo "PYTHONPATH: $PYTHONPATH"

# 使用gunicorn启动生产服务器
gunicorn {WSGI_MODULE} \
    --bind {GUNICORN_BIND} \
    --workers {GUNICORN_WORKERS} \
    --timeout {GUNICORN_TIMEOUT} \
    --log-level debug \
    --access-logfile access.log \
    --error-logfile error.log \
    --pythonpath "$PROJECT_ROOT" \
    --chdir "$PROJECT_ROOT" > gunicorn_start.log 2>&1 &

# 检查gunicorn是否成功启动
if [ $? -ne 0 ]; then
    echo "错误：Gunicorn启动失败！"
    exit 1
fi

# 启动服务监控脚本
echo "启动服务监控脚本..."
python "$(dirname "$(dirname "$0")")/monitor_server.py" > monitor_start.log 2>&1 &

echo "服务启动完成！"
echo "访问地址: http://{GUNICORN_BIND}"
echo "日志文件: gunicorn_start.log, access.log, error.log"
"""
    
    # 生成Windows启动脚本（开发用）
    windows_script = f"""@echo off
rem Django项目启动脚本（Windows开发环境）

echo === 启动Django开发服务器 ===
echo 项目: {PROJECT_NAME}
echo 监听地址: {GUNICORN_BIND}
echo.

rem 检查Python环境
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误：未找到Python！
    pause
    exit /b 1
)

echo 启动Django开发服务器...
cd /d "%~dp0.."
python {DJANGO_ENTRY} runserver {GUNICORN_BIND}

if %errorlevel% neq 0 (
    echo 错误：Django服务器启动失败！
    pause
    exit /b 1
)

echo 服务器启动成功！
pause
"""
    
    # 写入文件
    linux_script_path = dist_dir / "start_production.sh"
    windows_script_path = dist_dir / "start_server.bat"
    
    try:
        # Linux脚本
        with open(linux_script_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(linux_script)
        os.chmod(linux_script_path, 0o755)  # 设置可执行权限
        logger.info(f"生成Linux启动脚本: {linux_script_path}")
        
        # Windows脚本
        with open(windows_script_path, 'w', encoding='utf-8', newline='\r\n') as f:
            f.write(windows_script)
        logger.info(f"生成Windows启动脚本: {windows_script_path}")
        
        return True
    except Exception as e:
        logger.error(f"生成启动脚本失败: {e}")
        return False

def generate_systemd_services():
    """生成systemd服务配置"""
    logger.info("生成systemd服务配置...")
    
    dist_dir = Path(PROJECT_ROOT) / "dist"
    
    # 生成systemd服务配置文件（Django应用）
    # 使用占位符，让安装脚本自动替换为实际路径
    user = "ubuntu"  # Linux服务器默认用户
    
    # 使用PLACEHOLDER_PROJECT_ROOT作为占位符，安装时会被替换为实际路径
    systemd_service = f"""[Unit]
Description=Zpython Django Application
After=network.target

[Service]
User={user}
Group={user}
WorkingDirectory=PLACEHOLDER_PROJECT_ROOT
ExecStart=bash -c 'export PYTHONPATH=PLACEHOLDER_PROJECT_ROOT:$PYTHONPATH && cd PLACEHOLDER_PROJECT_ROOT && PLACEHOLDER_PROJECT_ROOT/{VENV_NAME}/bin/gunicorn {WSGI_MODULE} --bind {GUNICORN_BIND} --workers {GUNICORN_WORKERS} --timeout {GUNICORN_TIMEOUT} --log-level debug --access-logfile access.log --error-logfile error.log --pythonpath PLACEHOLDER_PROJECT_ROOT --chdir PLACEHOLDER_PROJECT_ROOT'
Restart=always

[Install]
WantedBy=multi-user.target
"""
    
    # 监控服务配置
    monitor_service = f"""[Unit]
Description=Zpython Monitor Service
After=network.target zpython.service

[Service]
User={user}
Group={user}
WorkingDirectory=PLACEHOLDER_PROJECT_ROOT
ExecStart=PLACEHOLDER_PROJECT_ROOT/{VENV_NAME}/bin/python monitor_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
    
    # 安装脚本
    install_script = f"""#!/bin/bash
# Systemd服务安装脚本

set -e

echo "=== 安装Zpython Systemd服务 ==="

# 获取当前目录的绝对路径
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
SERVICE_NAME="zpython"
MONITOR_SERVICE_NAME="zpython-monitor"

echo "项目根目录: $PROJECT_ROOT"

# 检查systemd是否可用
if ! command -v systemctl &> /dev/null; then
    echo "错误：systemctl命令不可用，可能不支持systemd"
    exit 1
fi

# 停止并禁用现有服务（如果存在）
echo "停止现有服务..."
sudo systemctl stop $SERVICE_NAME $MONITOR_SERVICE_NAME 2>/dev/null || true
sudo systemctl disable $SERVICE_NAME $MONITOR_SERVICE_NAME 2>/dev/null || true

# 替换服务文件中的占位符
echo "配置服务文件..."
sed "s|PLACEHOLDER_PROJECT_ROOT|$PROJECT_ROOT|g" "$SCRIPT_DIR/zpython.service" > /tmp/zpython.service
sed "s|PLACEHOLDER_PROJECT_ROOT|$PROJECT_ROOT|g" "$SCRIPT_DIR/zpython-monitor.service" > /tmp/zpython-monitor.service

# 复制服务文件到systemd目录
echo "安装服务文件..."
sudo cp /tmp/zpython.service /etc/systemd/system/
sudo cp /tmp/zpython-monitor.service /etc/systemd/system/

# 重新加载systemd配置
echo "重新加载systemd配置..."
sudo systemctl daemon-reload

# 启用服务
echo "启用服务..."
sudo systemctl enable $SERVICE_NAME
sudo systemctl enable $MONITOR_SERVICE_NAME

# 清理临时文件
rm -f /tmp/zpython.service /tmp/zpython-monitor.service

echo "服务安装完成！"
echo ""
echo "使用方法："
echo "  启动服务:   sudo systemctl start $SERVICE_NAME $MONITOR_SERVICE_NAME"
echo "  停止服务:   sudo systemctl stop $SERVICE_NAME $MONITOR_SERVICE_NAME"
echo "  重启服务:   sudo systemctl restart $SERVICE_NAME $MONITOR_SERVICE_NAME"
echo "  查看状态:   sudo systemctl status $SERVICE_NAME --no-pager"
echo "  查看日志:   sudo journalctl -u $SERVICE_NAME -f"
echo ""
echo "注意：首次安装后需要手动启动服务"
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

def copy_monitor_script():
    """复制监控脚本"""
    logger.info("复制监控脚本...")
    
    src_path = Path(PROJECT_ROOT) / "monitor_server.py"
    dst_path = Path(PROJECT_ROOT) / "dist" / "monitor_server.py"
    
    if not src_path.exists():
        logger.warning(f"监控脚本不存在: {src_path}")
        return False
    
    try:
        shutil.copy2(src_path, dst_path)
        logger.info(f"监控脚本已复制: {dst_path}")
        return True
    except Exception as e:
        logger.error(f"复制监控脚本失败: {e}")
        return False

def generate_server_diagnostic_scripts():
    """生成服务器端诊断脚本"""
    logger.info("生成服务器端诊断脚本...")
    
    dist_dir = Path(PROJECT_ROOT) / "dist"
    
    # 诊断脚本
    diagnose_script = """#!/bin/bash
# 服务器端Python路径诊断脚本

echo "=== Python环境诊断 ==="
echo "当前工作目录: $(pwd)"
echo ""

# 检查Python版本和路径
echo "=== Python环境信息 ==="
python3 -c "
import sys
print('Python版本:', sys.version)
print('Python可执行文件:', sys.executable)
print('当前工作目录:', sys.path[0])
print('Python模块搜索路径:')
for i, path in enumerate(sys.path):
    print(f'  {i}: {path}')
"

echo ""
echo "=== 逐步导入测试 ==="
echo "测试1: 导入zproject"
python3 -c "
try:
    import zproject
    print('✓ 成功导入zproject')
    print('zproject路径:', zproject.__file__)
except Exception as e:
    print('❌ 导入zproject失败:', e)
    print('当前sys.path:')
    import sys
    for p in sys.path:
        print('  ', p)
"

echo ""
echo "测试2: 导入zproject.wsgi"
python3 -c "
try:
    import zproject.wsgi
    print('✓ 成功导入zproject.wsgi')
    print('zproject.wsgi路径:', zproject.wsgi.__file__)
    print('WSGI应用:', getattr(zproject.wsgi, 'application', '未找到application'))
except Exception as e:
    print('❌ 导入zproject.wsgi失败:', e)
"

echo ""
echo "=== 文件系统检查 ==="
echo "检查zproject目录是否存在:"
if [ -d "zproject" ]; then
    echo "✓ zproject目录存在"
    echo "zproject目录内容:"
    ls -la zproject/
else
    echo "❌ zproject目录不存在"
fi

echo ""
echo "检查manage.py是否存在:"
if [ -f "manage.py" ]; then
    echo "✓ manage.py存在"
else
    echo "❌ manage.py不存在"
fi

echo ""
echo "=== 虚拟环境检查 ==="
echo "虚拟环境路径: $VIRTUAL_ENV"
if [ -n "$VIRTUAL_ENV" ]; then
    echo "✓ 虚拟环境已激活"
else
    echo "❌ 虚拟环境未激活"
fi
"""
    
    # 修复脚本
    fix_script = """#!/bin/bash
# 服务器端Python路径修复脚本

echo "=== Python路径修复脚本 ==="
echo "当前工作目录: $(pwd)"
echo ""

# 方法1: 设置PYTHONPATH并测试
echo "方法1: 设置PYTHONPATH环境变量..."
export PYTHONPATH=/var/codes/deploy/backend/backendCodes/zp1:$PYTHONPATH
echo "PYTHONPATH: $PYTHONPATH"

echo ""
echo "测试导入zproject..."
python3 -c "
import sys
print('当前sys.path:')
for i, p in enumerate(sys.path):
    print(f'  {i}: {p}')

try:
    import zproject
    print('✓ 成功导入zproject')
    print('zproject路径:', zproject.__file__)
except Exception as e:
    print('❌ 导入zproject失败:', e)
"

echo ""
echo "方法2: 使用pythonpath参数启动Gunicorn..."
echo "命令:"
echo "gunicorn zproject.wsgi:application \\"
echo "    --bind 0.0.0.0:5555 \\"
echo "    --workers 1 \\"
echo "    --timeout 30 \\"
echo "    --log-level debug \\"
echo "    --pythonpath /var/codes/deploy/backend/backendCodes/zp1 \\"
echo "    --chdir /var/codes/deploy/backend/backendCodes/zp1"

echo ""
echo "方法3: 使用完整路径启动..."
echo "命令:"
echo "cd /var/codes/deploy/backend/backendCodes/zp1"
echo "export PYTHONPATH=/var/codes/deploy/backend/backendCodes/zp1:$PYTHONPATH"
echo "source venv/bin/activate"
echo "gunicorn zproject.wsgi:application --bind 0.0.0.0:5555 --workers 1 --timeout 30 --log-level debug"

echo ""
echo "=== 推荐的完整修复步骤 ==="
echo "1. 停止当前服务:"
echo "   sudo systemctl stop zpython zpython-monitor"
echo "   pkill -f gunicorn"
echo ""
echo "2. 手动测试启动:"
echo "   cd /var/codes/deploy/backend/backendCodes/zp1"
echo "   export PYTHONPATH=/var/codes/deploy/backend/backendCodes/zp1:$PYTHONPATH"
echo "   source venv/bin/activate"
echo "   gunicorn zproject.wsgi:application --bind 0.0.0.0:5555 --workers 1 --timeout 30 --log-level debug --pythonpath /var/codes/deploy/backend/backendCodes/zp1 --chdir /var/codes/deploy/backend/backendCodes/zp1"
echo ""
echo "3. 如果手动启动成功，重新部署systemd服务:"
echo "   sudo ./install_systemd_service.sh"
"""
    
    # 手动调试脚本
    manual_debug_script = """#!/bin/bash
# 手动调试启动脚本 - 服务器端使用

echo "=== 手动调试启动脚本 ==="
echo "当前工作目录: $(pwd)"
echo ""

# 停止现有服务
echo "1. 停止现有服务..."
sudo systemctl stop zpython zpython-monitor 2>/dev/null || true
pkill -f gunicorn 2>/dev/null || true

echo ""
echo "2. 激活虚拟环境..."
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "✓ 虚拟环境已激活"
else
    echo "❌ 虚拟环境不存在"
    exit 1
fi

echo ""
echo "3. 设置环境变量..."
export PYTHONPATH=/var/codes/deploy/backend/backendCodes/zp1:$PYTHONPATH
echo "PYTHONPATH: $PYTHONPATH"

echo ""
echo "4. 测试Python导入..."
python3 -c "
import sys
print('Python版本:', sys.version)
print('工作目录:', sys.path[0])
try:
    import zproject
    print('✓ 成功导入zproject')
    print('zproject路径:', zproject.__file__)
    
    import zproject.wsgi
    print('✓ 成功导入zproject.wsgi')
    print('WSGI应用:', getattr(zproject.wsgi, 'application', '未找到'))
except Exception as e:
    print('❌ 导入失败:', e)
    import traceback
    traceback.print_exc()
"

echo ""
echo "5. 启动Gunicorn..."
echo "命令:"
echo "gunicorn zproject.wsgi:application \\"
echo "    --bind 0.0.0.0:5555 \\"
echo "    --workers 1 \\"
echo "    --timeout 30 \\"
echo "    --log-level debug \\"
echo "    --pythonpath /var/codes/deploy/backend/backendCodes/zp1 \\"
echo "    --chdir /var/codes/deploy/backend/backendCodes/zp1"

echo ""
echo "正在启动Gunicorn..."
gunicorn zproject.wsgi:application \
    --bind 0.0.0.0:5555 \
    --workers 1 \
    --timeout 30 \
    --log-level debug \
    --pythonpath /var/codes/deploy/backend/backendCodes/zp1 \
    --chdir /var/codes/deploy/backend/backendCodes/zp1

echo ""
echo "=== 启动完成 ==="
echo "如果启动成功，可以访问: http://$(hostname -I | awk '{print $1}'):5555"
echo ""
echo "查看日志:"
echo "tail -f /var/codes/deploy/backend/backendCodes/zp1/access.log"
echo "tail -f /var/codes/deploy/backend/backendCodes/zp1/error.log"
"""
    
    diagnostic_scripts = {
        "diagnose_server.sh": diagnose_script,
        "fix_pythonpath.sh": fix_script,
        "manual_start_debug.sh": manual_debug_script
    }
    
    try:
        for filename, content in diagnostic_scripts.items():
            file_path = dist_dir / filename
            with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(content)
            
            os.chmod(file_path, 0o755)  # 设置可执行权限
            logger.info(f"生成诊断脚本: {file_path}")
        
        return True
    except Exception as e:
        logger.error(f"生成诊断脚本失败: {e}")
        return False

def package_project():
    """打包项目"""
    logger.info("开始打包项目...")
    
    # 获取项目根目录
    global PROJECT_ROOT
    PROJECT_ROOT = get_project_root()
    if not PROJECT_ROOT:
        logger.error("无法确定项目根目录")
        return False
    
    logger.info(f"项目根目录: {PROJECT_ROOT}")
    
    # 检查依赖
    if not check_dependencies():
        return False
    
    # 生成各种脚本
    success = True
    success &= generate_startup_scripts()
    success &= generate_systemd_services()
    success &= copy_monitor_script()
    success &= generate_server_diagnostic_scripts()
    
    if success:
        logger.info("项目打包完成！")
        logger.info(f"部署文件已生成到: {Path(PROJECT_ROOT) / 'dist'}")
    else:
        logger.error("项目打包失败！")
    
    return success

def main():
    """主函数"""
    # 检查命令行参数
    if len(sys.argv) > 1 and sys.argv[1] == "--generate-only":
        logger.info("===== 只生成部署文件 =====")
        success = package_project()
        if success:
            print("\n===== 部署文件生成成功！ =====")
        else:
            print("\n===== 部署文件生成失败！ =====")
            sys.exit(1)
    else:
        # 完整打包流程
        logger.info("===== Django项目打包部署工具 =====")
        success = package_project()
        if success:
            print("\n===== 打包完成！ =====")
            print("请查看dist目录中的部署文件")
        else:
            print("\n===== 打包失败！ =====")
            sys.exit(1)

if __name__ == "__main__":
    main()