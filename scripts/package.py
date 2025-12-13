import os
import sys
import subprocess
import time
import platform
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

# 配置参数
PROJECT_NAME = "zpython_django"  # 打包后可执行文件名
DJANGO_ENTRY = "manage.py"       # Django入口文件
PORT = 5555                      # 部署端口
CHECK_URL = f"http://127.0.0.1:{PORT}/index/"  # 服务校验URL
ASSETS_DIR = "assets"            # 静态资源目录
DB_FILE = "db.sqlite3"           # 数据库文件
SCRIPTS_TO_PACK = ["扫描.py", "扫描全部.py"]  # 需额外打包的业务脚本

# 跨平台配置
SYSTEM = platform.system()
VENV_PYTHON = Path("venv") / ("Scripts" if SYSTEM == "Windows" else "bin") / ("python.exe" if SYSTEM == "Windows" else "python3")
PYINSTALLER_ADD_DATA_SEP = ";" if SYSTEM == "Windows" else ":"  # Windows用;，Linux用:
CLEAR_CMD = "rm -rf build dist __pycache__ *.spec" if SYSTEM == "Linux" else "del /f /s /q build dist __pycache__ *.spec"

# 日志配置
LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "package.log"
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

def run_cmd(cmd, desc="执行命令"):
    """跨平台执行命令，带日志输出"""
    logger.info(f"\n=== {desc} ===")
    logger.info(f"命令：{cmd}")
    try:
        result = subprocess.run(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8", errors="ignore"
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

def clear_old_build():
    """清理旧打包产物"""
    return run_cmd(CLEAR_CMD, "清理旧打包产物")

def install_deps():
    """安装依赖（含PyInstaller）"""
    deps_cmd = f"{VENV_PYTHON} -m pip install --upgrade pip && {VENV_PYTHON} -m pip install -r requirements.txt pyinstaller"
    return run_cmd(deps_cmd, "安装项目依赖和打包工具")

def package_django():
    """打包Django主程序（含Channels依赖）"""
    # 构建add-data参数（携带数据库、静态资源）
    add_data = [
        f"{DB_FILE}{PYINSTALLER_ADD_DATA_SEP}.",
        f"{ASSETS_DIR}{PYINSTALLER_ADD_DATA_SEP}{ASSETS_DIR}"
    ]
    add_data_str = " ".join([f"--add-data \"{item}\"" for item in add_data])

    # 隐藏导入（适配Channels/Twisted）
    hidden_imports = [
        "zapp", "channels", "channels.layers", "daphne", "twisted",
        "twisted.internet", "twisted.web", "zope.interface"
    ]
    hidden_import_str = " ".join([f"--hidden-import {item}" for item in hidden_imports])

    # PyInstaller打包命令
    package_cmd = (
        f"{VENV_PYTHON} -m PyInstaller "
        f"--name {PROJECT_NAME} "
        f"--onefile "
        f"--clean "
        f"{hidden_import_str} "
        f"{add_data_str} "
        f"{DJANGO_ENTRY}"
    )
    return run_cmd(package_cmd, "打包Django主程序")

def package_scripts():
    """打包业务脚本（扫描.py、扫描全部.py）"""
    for script in SCRIPTS_TO_PACK:
        if not Path(script).exists():
            logger.warning(f"{script}不存在，跳过打包")
            continue
        script_name = Path(script).stem  # 去除后缀，作为可执行文件名
        package_cmd = (
            f"{VENV_PYTHON} -m PyInstaller "
            f"--name {script_name} "
            f"--onefile "
            f"--clean "
            f"{script}"
        )
        if not run_cmd(package_cmd, f"打包业务脚本：{script}"):
            return False
    return True

def main():
    """主流程：清理→安装依赖→打包"""
    logger.info("===== Django项目打包工具 =====")
    steps = [
        ("清理旧产物", clear_old_build),
        ("安装依赖", install_deps),
        ("打包Django", package_django),
        ("打包业务脚本", package_scripts)
    ]

    for step_name, step_func in steps:
        if not step_func():
            logger.error(f"\n===== 流程终止：{step_name}失败 =====")
            sys.exit(1)

    logger.info(f"\n===== 打包成功！ =====")
    logger.info(f"Django打包产物：dist/{PROJECT_NAME}（{SYSTEM}可执行文件）")
    logger.info(f"业务脚本产物：dist/（{', '.join(SCRIPTS_TO_PACK)}对应的可执行文件）")
    logger.info(f"日志文件：{LOG_FILE}")

if __name__ == "__main__":
    main()
