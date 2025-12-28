# zapp/services/memo_service.py
import sqlite3
import os
import base64
import logging
import html
from datetime import datetime
from django.utils import timezone

# 设置日志记录器
logger = logging.getLogger(__name__)

# 数据库路径
DB_PATH = '/var/codes/deploy/backend/backendCodes/the-go/accounting.db'
# Windows路径兼容
WINDOWS_DB_PATH = DB_PATH.replace('/', '\\')

class MemoService:
    def __init__(self):
        self.db_path = WINDOWS_DB_PATH if os.name == 'nt' else DB_PATH
        # 获取敏感词文件路径
        self.sensitive_words_file = os.path.join(os.path.dirname(__file__), 'sensitive_words.txt')
        # 加载并解码敏感词
        self.sensitive_words = self._load_sensitive_words()
        # 在初始化时创建表（如果不存在），避免重复操作
        self._create_table()
        
    def _load_sensitive_words(self):
        """从文件加载base64编码的敏感词并解码
        
        Returns:
            list: 解码后的敏感词列表
        """
        sensitive_words = []
        
        try:
            with open(self.sensitive_words_file, 'r', encoding='utf-8') as f:
                for line in f:
                    encoded_word = line.strip()
                    if encoded_word:
                        try:
                            # 解码base64字符串
                            word_bytes = base64.b64decode(encoded_word)
                            word = word_bytes.decode('utf-8')
                            sensitive_words.append(word)
                        except (base64.binascii.Error, UnicodeDecodeError):
                            # 跳过无效的编码行
                            continue
        except FileNotFoundError:
            # 如果文件不存在，返回空列表
            print(f"警告: 敏感词文件不存在: {self.sensitive_words_file}")
        except Exception as e:
            # 处理其他可能的错误
            print(f"加载敏感词时出错: {e}")
        
        return sensitive_words
    
    def _create_table(self):
        """创建memos表（如果不存在）"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS memos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        content TEXT NOT NULL,
                        created_at TEXT NOT NULL
                    )
                ''')
                conn.commit()
        except sqlite3.Error as e:
            # 记录详细错误日志，但只向用户返回通用错误信息
            logger.error(f"Database table creation error: {str(e)}")
            raise Exception("Database operation failed. Please try again later.")
    
    def _check_sensitive_words(self, content):
        """检查内容是否包含敏感关键词
        
        Args:
            content (str): 要检查的内容
            
        Returns:
            bool: True表示包含敏感词，False表示不包含
            
        Raises:
            ValueError: 如果包含敏感词
        """
        if not content:
            return False
            
        # 转换为小写进行检查（不区分大小写）
        content_lower = content.lower()
        
        for keyword in self.sensitive_words:
            if keyword.lower() in content_lower:
                raise ValueError(f"Content contains sensitive word")
                
        return False
    
    def get_all_memos(self):
        """获取所有备忘录"""
        try:
            # 表已在初始化时创建，无需重复操作
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM memos ORDER BY id DESC')
                memos = cursor.fetchall()
                return [dict(memo) for memo in memos]
        except sqlite3.Error as e:
            # 记录详细错误日志，但只向用户返回通用错误信息
            logger.error(f"Database read error: {str(e)}")
            raise Exception("Database operation failed. Please try again later.")
    
    def add_memo(self, content):
        """添加新备忘录
        
        Args:
            content (str): 备忘录内容
            
        Returns:
            dict: 包含新创建备忘录信息的字典
            
        Raises:
            ValueError: 如果内容为空、过长或包含敏感词
            Exception: 如果数据库操作失败
        """
        try:
            # 1. 输入验证
            if not content:
                raise ValueError("Memo content cannot be empty")
                
            # 去除首尾空白字符
            trimmed_content = content.strip()
            if not trimmed_content:
                raise ValueError("Memo content cannot be empty or just whitespace")
            
            # 对内容进行HTML转义，防止XSS攻击
            sanitized_content = html.escape(trimmed_content)
                
            # 内容长度限制（防止过长）
            MAX_LENGTH = 1000
            if len(trimmed_content) > MAX_LENGTH:
                raise ValueError(f"Memo content is too long (maximum {MAX_LENGTH} characters)")
            
            # 2. 检查敏感词（使用原始内容进行检查）
            self._check_sensitive_words(trimmed_content)
            
            # 表已在初始化时创建，无需重复操作
            
            # 4. 获取北京时间
            utc_time = timezone.now()
            beijing_time = utc_time.astimezone(timezone.get_current_timezone())
            created_at = beijing_time.strftime('%Y-%m-%d %H:%M:%S')
            
            # 5. 数据库操作
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO memos (content, created_at) VALUES (?, ?)',
                    (sanitized_content, created_at)
                )
                conn.commit()
                memo_id = cursor.lastrowid
                return {
                    "id": memo_id, 
                    "content": sanitized_content, 
                    "created_at": created_at
                }
        except ValueError as e:
            # 输入验证或敏感词检查失败
            raise e
        except sqlite3.Error as e:
            # 数据库操作失败
            logger.error(f"Database write error when adding memo: {str(e)}")
            raise Exception("Failed to add memo. Please try again later.")
        except Exception as e:
            # 其他未知错误
            logger.error(f"Unexpected error when adding memo: {str(e)}")
            raise Exception("Failed to add memo. Please try again later.")
    
    def delete_memo(self, memo_id):
        """删除备忘录
        
        Args:
            memo_id (int): 备忘录ID
            
        Returns:
            bool: True表示删除成功，False表示未找到该备忘录
            
        Raises:
            ValueError: 如果memo_id无效
        """
        try:
            # 输入验证：确保memo_id是有效的正整数
            try:
                # 检查是否为字符串类型的数字（避免浮点数转换问题）
                if isinstance(memo_id, str):
                    # 检查字符串是否只包含数字
                    if not memo_id.isdigit():
                        raise ValueError("Memo ID must be a positive integer")
                    memo_id = int(memo_id)
                else:
                    # 检查是否为整数类型
                    if not isinstance(memo_id, int):
                        raise ValueError("Memo ID must be a positive integer")
                    if memo_id <= 0:
                        raise ValueError("Memo ID must be a positive integer")
            except (TypeError, ValueError):
                raise ValueError("Memo ID must be a positive integer")
            
            # 表已在初始化时创建，无需重复操作
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM memos WHERE id = ?', (memo_id,))
                conn.commit()
                return cursor.rowcount > 0
        except ValueError as e:
            raise e
        except sqlite3.Error as e:
            logger.error(f"Database delete error: {str(e)}")
            raise Exception("Database operation failed. Please try again later.")
        except Exception as e:
            logger.error(f"Unexpected error when deleting memo: {str(e)}")
            raise Exception("Failed to delete memo. Please try again later.")
    
    def search_memos(self, keyword):
        """搜索备忘录
        
        Args:
            keyword (str): 搜索关键词
            
        Returns:
            list: 匹配的备忘录列表
            
        Raises:
            ValueError: 如果关键词无效
        """
        try:
            # 输入验证：确保关键词有效
            if not isinstance(keyword, str):
                raise ValueError("Keyword must be a string")
            
            # 去除首尾空白字符
            keyword = keyword.strip()
            
            # 长度限制：防止过长的关键词导致性能问题
            MAX_KEYWORD_LENGTH = 100
            if len(keyword) > MAX_KEYWORD_LENGTH:
                raise ValueError(f"Keyword is too long (maximum {MAX_KEYWORD_LENGTH} characters)")
            
            # 如果关键词为空，返回所有备忘录
            if not keyword:
                return self.get_all_memos()
            
            # 表已在初始化时创建，无需重复操作
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(
                    'SELECT * FROM memos WHERE content LIKE ? ORDER BY id DESC',
                    (f'%{keyword}%',)
                )
                memos = cursor.fetchall()
                return [dict(memo) for memo in memos]
        except ValueError as e:
            raise e
        except sqlite3.Error as e:
            logger.error(f"Database search error: {str(e)}")
            raise Exception("Database operation failed. Please try again later.")
        except Exception as e:
            logger.error(f"Unexpected error when searching memo: {str(e)}")
            raise Exception("Failed to search memo. Please try again later.")

# 创建全局实例
memo_service = MemoService()