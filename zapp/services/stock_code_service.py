# zapp/services/stock_code_service.py
import sqlite3
import os
import logging
from datetime import datetime
from django.utils import timezone
from django.conf import settings

# 设置日志记录器
logger = logging.getLogger(__name__)

# 数据库路径，与memo_service共享同一个数据库
if os.name == 'nt':
    DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'accounting.db')
else:
    DB_PATH = '/var/codes/deploy/backend/backendCodes/the-go/accounting.db'

class StockCodeService:
    def __init__(self):
        self.db_path = DB_PATH
        self.assets_dir = settings.ASSETS_DIR
        # 创建表（如果不存在）
        self._create_table()
        # 初始化股票代码（从a.txt导入）
        self._initialize_codes()
    
    def _create_table(self):
        """创建stock_codes表（如果不存在）"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS stock_codes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        code TEXT NOT NULL UNIQUE,
                        used INTEGER DEFAULT 0,
                        used_at TEXT,
                        created_at TEXT NOT NULL
                    )
                ''')
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Database table creation error: {str(e)}")
            raise Exception("Database operation failed. Please try again later.")
    
    def _initialize_codes(self):
        """从a.txt文件导入股票代码到数据库"""
        try:
            # 读取a.txt文件内容
            a_txt_path = os.path.join(self.assets_dir, 'a.txt')
            if not os.path.exists(a_txt_path):
                logger.warning(f"a.txt file not found: {a_txt_path}")
                return
            
            with open(a_txt_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 解析股票代码（假设每行一个代码，格式如：融新锦动力(300157)）
            # 提取括号中的数字作为股票代码
            import re
            codes = re.findall(r'\((\d+)\)', content)
            
            # 去重
            unique_codes = list(set(codes))
            
            # 获取当前时间
            utc_time = timezone.now()
            beijing_time = utc_time.astimezone(timezone.get_current_timezone())
            created_at = beijing_time.strftime('%Y-%m-%d %H:%M:%S')
            
            # 批量插入数据库，仅插入不存在的代码
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                for code in unique_codes:
                    cursor.execute(
                        'INSERT OR IGNORE INTO stock_codes (code, created_at) VALUES (?, ?)',
                        (code, created_at)
                    )
                conn.commit()
            
            logger.info(f"Initialized {len(unique_codes)} stock codes from a.txt")
        except Exception as e:
            logger.error(f"Failed to initialize stock codes: {str(e)}")
            # 初始化失败不影响服务运行，仅记录日志
    
    def get_unused_code(self):
        """获取一个未使用的股票代码"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                # 获取第一个未使用的代码
                cursor.execute('SELECT * FROM stock_codes WHERE used = 0 LIMIT 1')
                code_row = cursor.fetchone()
                
                if not code_row:
                    return None
                
                return dict(code_row)
        except sqlite3.Error as e:
            logger.error(f"Database read error: {str(e)}")
            raise Exception("Database operation failed. Please try again later.")
    
    def mark_code_as_used(self, code):
        """标记股票代码为已使用"""
        try:
            # 获取当前时间
            utc_time = timezone.now()
            beijing_time = utc_time.astimezone(timezone.get_current_timezone())
            used_at = beijing_time.strftime('%Y-%m-%d %H:%M:%S')
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'UPDATE stock_codes SET used = 1, used_at = ? WHERE code = ?',
                    (used_at, code)
                )
                conn.commit()
                
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            logger.error(f"Database update error: {str(e)}")
            raise Exception("Database operation failed. Please try again later.")
    
    def reset_code_usage(self):
        """重置所有代码为未使用状态（用于测试或重新开始）"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('UPDATE stock_codes SET used = 0, used_at = NULL')
                conn.commit()
                return cursor.rowcount
        except sqlite3.Error as e:
            logger.error(f"Database update error: {str(e)}")
            raise Exception("Database operation failed. Please try again later.")

# 创建全局实例
stock_code_service = StockCodeService()
