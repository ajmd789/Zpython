# zapp/services/memo_service.py
import sqlite3
import os
from datetime import datetime
from django.utils import timezone

# 数据库路径
DB_PATH = '/var/codes/deploy/backend/backendCodes/the-go/accounting.db'
# Windows路径兼容
WINDOWS_DB_PATH = DB_PATH.replace('/', '\\')

class MemoService:
    def __init__(self):
        self.db_path = WINDOWS_DB_PATH if os.name == 'nt' else DB_PATH
        # 不在初始化时创建表，而是在实际操作时尝试
    
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
        """添加新备忘录"""
        try:
            self._create_table()  # 先尝试创建表
            # 获取UTC时间并转换为北京时间
            utc_time = timezone.now()
            beijing_time = utc_time.astimezone(timezone.get_current_timezone())
            created_at = beijing_time.strftime('%Y-%m-%d %H:%M:%S')
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO memos (content, created_at) VALUES (?, ?)',
                    (content, created_at)
                )
                conn.commit()
                memo_id = cursor.lastrowid
                return {"id": memo_id, "content": content, "created_at": created_at}
        except sqlite3.Error as e:
            raise Exception(f"Database error: {str(e)}")
    
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