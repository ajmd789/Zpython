import os
import sys
import logging
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))

# 导入generate_startup_scripts函数
from scripts.package import generate_startup_scripts

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 创建dist目录
Path("dist").mkdir(exist_ok=True)

# 测试生成启动脚本
logger.info("测试生成启动脚本...")
if generate_startup_scripts():
    logger.info("启动脚本生成成功！")
    # 列出dist目录中的文件
    logger.info("dist目录中的文件:")
    for file in Path("dist").iterdir():
        logger.info(f"  {file.name}")
else:
    logger.error("启动脚本生成失败！")
