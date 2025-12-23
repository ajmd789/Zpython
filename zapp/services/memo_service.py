# zapp/services/memo_service.py
import sqlite3
import os
import base64
from datetime import datetime
from django.utils import timezone

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
        # 不在初始化时创建表，而是在实际操作时尝试
        
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
            raise Exception(f"Database error: {str(e)}")
    
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
            self._create_table()  # 先尝试创建表
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM memos ORDER BY id DESC')
                memos = cursor.fetchall()
                return [dict(memo) for memo in memos]
        except sqlite3.Error as e:
            raise Exception(f"Database error: {str(e)}")
    
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
                
            # 内容长度限制（防止过长）
            MAX_LENGTH = 1000
            if len(trimmed_content) > MAX_LENGTH:
                raise ValueError(f"Memo content is too long (maximum {MAX_LENGTH} characters)")
            
            # 2. 检查敏感词
            self._check_sensitive_words(trimmed_content)
            
            # 3. 创建表（如果不存在）
            self._create_table()
            
            # 4. 获取北京时间
            utc_time = timezone.now()
            beijing_time = utc_time.astimezone(timezone.get_current_timezone())
            created_at = beijing_time.strftime('%Y-%m-%d %H:%M:%S')
            
            # 5. 数据库操作
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO memos (content, created_at) VALUES (?, ?)',
                    (trimmed_content, created_at)
                )
                conn.commit()
                memo_id = cursor.lastrowid
                
                return {
                    "id": memo_id, 
                    "content": trimmed_content, 
                    "created_at": created_at
                }
        except ValueError as e:
            # 输入验证或敏感词检查失败
            raise e
        except sqlite3.Error as e:
            # 数据库操作失败
            raise Exception(f"Database error: {str(e)}")
        except Exception as e:
            # 其他未知错误
            raise Exception(f"Failed to add memo: {str(e)}")
    
    def delete_memo(self, memo_id):
        """删除备忘录"""
        try:
            self._create_table()  # 先尝试创建表
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM memos WHERE id = ?', (memo_id,))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            raise Exception(f"Database error: {str(e)}")
    
    def search_memos(self, keyword):
        """搜索备忘录"""
        try:
            self._create_table()  # 先尝试创建表
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(
                    'SELECT * FROM memos WHERE content LIKE ? ORDER BY id DESC',
                    (f'%{keyword}%',)
                )
                memos = cursor.fetchall()
                return [dict(memo) for memo in memos]
        except sqlite3.Error as e:
            raise Exception(f"Database error: {str(e)}")

# 创建全局实例
memo_service = MemoService()