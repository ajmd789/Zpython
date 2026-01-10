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
        # 创建data目录用于存储codeData
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
        self._ensure_data_dir_exists()
        # 创建表（如果不存在）
        self._create_table()
        # 初始化股票代码（从a.txt导入）
        self._initialize_codes()
    
    def _ensure_data_dir_exists(self):
        """确保data目录存在"""
        try:
            if not os.path.exists(self.data_dir):
                os.makedirs(self.data_dir)
                logger.info(f"Created data directory: {self.data_dir}")
        except Exception as e:
            logger.error(f"Failed to create data directory: {str(e)}")
            raise Exception("Failed to create data directory. Please try again later.")
    
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
                        codeData TEXT,
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
    
    def mark_code_as_used(self, code, codeData=None):
        """标记股票代码为已使用"""
        try:
            # 获取当前时间
            utc_time = timezone.now()
            beijing_time = utc_time.astimezone(timezone.get_current_timezone())
            used_at = beijing_time.strftime('%Y-%m-%d %H:%M:%S')
            
            # 将codeData存储到文件中
            if codeData is not None:
                code_data_file = os.path.join(self.data_dir, f'{code}.txt')
                with open(code_data_file, 'w', encoding='utf-8') as f:
                    f.write(codeData)
            
            # 更新数据库状态（codeData字段设为None，因为已存储到文件）
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'UPDATE stock_codes SET used = 1, used_at = ?, codeData = ? WHERE code = ?',
                    (used_at, None, code)
                )
                conn.commit()
                
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            logger.error(f"Database update error: {str(e)}")
            raise Exception(f"Database operation failed: {str(e)}")
        except IOError as e:
            logger.error(f"File write error: {str(e)}")
            raise Exception(f"Failed to write codeData to file: {str(e)}")
    
    def reset_code_usage(self):
        """重置所有代码为未使用状态（用于测试或重新开始）"""
        try:
            # 重置数据库中的状态
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('UPDATE stock_codes SET used = 0, used_at = NULL, codeData = NULL')
                conn.commit()
            
            # 清理data目录中所有的codeData文件
            for filename in os.listdir(self.data_dir):
                if filename.endswith('.txt'):
                    file_path = os.path.join(self.data_dir, filename)
                    try:
                        os.remove(file_path)
                        logger.info(f"Removed codeData file: {file_path}")
                    except IOError as e:
                        logger.error(f"Failed to remove file {file_path}: {str(e)}")
                        # 继续清理其他文件，不中断整个过程
            
            return cursor.rowcount
        except sqlite3.Error as e:
            logger.error(f"Database update error: {str(e)}")
            raise Exception("Database operation failed. Please try again later.")
        except IOError as e:
            logger.error(f"Directory read error: {str(e)}")
            raise Exception("Failed to clean up codeData files. Please try again later.")
    
    def get_code_info(self, code):
        """获取指定股票代码的详细信息"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM stock_codes WHERE code = ?', (code,))
                code_row = cursor.fetchone()
                
                if not code_row:
                    return None
                
                # 从数据库获取基本信息
                code_info = dict(code_row)
                
                # 从文件中读取codeData
                code_data_file = os.path.join(self.data_dir, f'{code}.txt')
                if os.path.exists(code_data_file):
                    try:
                        with open(code_data_file, 'r', encoding='utf-8') as f:
                            code_info['codeData'] = f.read()
                    except IOError as e:
                        logger.error(f"File read error for {code}: {str(e)}")
                        code_info['codeData'] = None
                else:
                    code_info['codeData'] = None
                
                return code_info
        except sqlite3.Error as e:
            logger.error(f"Database read error: {str(e)}")
            raise Exception("Database operation failed. Please try again later.")
    
    def get_all_used_codes(self):
        """获取所有已使用的股票代码及其详细信息"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM stock_codes WHERE used = 1 ORDER BY used_at DESC')
                code_rows = cursor.fetchall()
                
                result = []
                for code_row in code_rows:
                    # 从数据库获取基本信息
                    code_info = dict(code_row)
                    code = code_info['code']
                    
                    # 从文件中读取codeData
                    code_data_file = os.path.join(self.data_dir, f'{code}.txt')
                    if os.path.exists(code_data_file):
                        try:
                            with open(code_data_file, 'r', encoding='utf-8') as f:
                                code_info['codeData'] = f.read()
                        except IOError as e:
                            logger.error(f"File read error for {code}: {str(e)}")
                            code_info['codeData'] = None
                    else:
                        code_info['codeData'] = None
                    
                    result.append(code_info)
                
                return result
        except sqlite3.Error as e:
            logger.error(f"Database read error: {str(e)}")
            raise Exception("Database operation failed. Please try again later.")

# 创建全局实例
stock_code_service = StockCodeService()
