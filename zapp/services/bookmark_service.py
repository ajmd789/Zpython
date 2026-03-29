# zapp/services/bookmark_service.py
import sqlite3
import os
import logging
import requests
import re
import unicodedata
from urllib.parse import urlparse
from datetime import datetime
from django.utils import timezone

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, 'accounting.db')

class BookmarkService:
    def __init__(self):
        self.db_path = DB_PATH
        self._create_table()
        
    def _create_table(self):
        """创建bookmarks表（如果不存在）"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS bookmarks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        url TEXT NOT NULL,
                        title TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    )
                ''')
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Database table creation error: {str(e)}")
            raise Exception("Database operation failed. Please try again later.")

    def _get_current_time(self):
        """获取当前北京时间的字符串"""
        utc_time = timezone.now()
        beijing_time = utc_time.astimezone(timezone.get_current_timezone())
        return beijing_time.strftime('%Y-%m-%d %H:%M:%S')

    def _truncate_title(self, title, max_width=12):
        """截断标题以适应图标宽度：中文字符宽度计2，英文字符宽度计1，最多6个汉字或12个英文字符"""
        if not title:
            return title
            
        current_width = 0
        result = []
        for char in title:
            if unicodedata.east_asian_width(char) in ('F', 'W', 'A'):
                current_width += 2
            else:
                current_width += 1
            
            if current_width > max_width:
                break
            result.append(char)
            
        return ''.join(result).strip()

    def _fetch_title_from_url(self, url):
        """从网页抓取title标签内容"""
        fallback_title = url
        try:
            parsed = urlparse(url if url.startswith(('http://', 'https://')) else 'http://' + url)
            fallback_title = parsed.netloc or url
        except Exception:
            pass

        try:
            if not url.startswith(('http://', 'https://')):
                url = 'http://' + url
                
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            # 设置较短的超时时间，避免阻塞
            response = requests.get(url, headers=headers, timeout=5)
            response.encoding = response.apparent_encoding or 'utf-8'
            
            match = re.search(r'<title.*?>(.*?)</title>', response.text, re.IGNORECASE | re.DOTALL)
            if match:
                title = match.group(1).strip()
                # 简单清理可能含有的换行和多余空格
                title = re.sub(r'\s+', ' ', title)
                if title:
                    return self._truncate_title(title)
            return self._truncate_title(fallback_title)
        except Exception as e:
            logger.warning(f"Failed to fetch title for {url}: {str(e)}")
            return self._truncate_title(fallback_title)

    def get_all_bookmarks(self):
        """获取所有书签"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM bookmarks ORDER BY id ASC')
                bookmarks = cursor.fetchall()
                return [dict(bm) for bm in bookmarks]
        except sqlite3.Error as e:
            logger.error(f"Database read error: {str(e)}")
            raise Exception("Database operation failed.")

    def add_bookmark(self, url, title=None):
        """添加新书签"""
        try:
            if not url:
                raise ValueError("URL cannot be empty")
            
            url = url.strip()
            if not title or not title.strip():
                title = self._fetch_title_from_url(url)
            else:
                title = title.strip()
                
            current_time = self._get_current_time()
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO bookmarks (url, title, created_at, updated_at) VALUES (?, ?, ?, ?)',
                    (url, title, current_time, current_time)
                )
                conn.commit()
                bm_id = cursor.lastrowid
                return {
                    "id": bm_id, 
                    "url": url,
                    "title": title, 
                    "created_at": current_time,
                    "updated_at": current_time
                }
        except ValueError as e:
            raise e
        except sqlite3.Error as e:
            logger.error(f"Database write error when adding bookmark: {str(e)}")
            raise Exception("Failed to add bookmark.")

    def update_bookmark(self, bm_id, url, title):
        """更新书签"""
        try:
            if not url or not url.strip():
                raise ValueError("URL cannot be empty")
            if not title or not title.strip():
                title = self._fetch_title_from_url(url.strip())
            else:
                title = title.strip()
                
            url = url.strip()
            current_time = self._get_current_time()
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'UPDATE bookmarks SET url = ?, title = ?, updated_at = ? WHERE id = ?',
                    (url, title, current_time, bm_id)
                )
                conn.commit()
                if cursor.rowcount == 0:
                    raise ValueError("Bookmark not found")
                return True
        except ValueError as e:
            raise e
        except sqlite3.Error as e:
            logger.error(f"Database update error: {str(e)}")
            raise Exception("Failed to update bookmark.")

    def delete_bookmark(self, bm_id):
        """删除书签"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM bookmarks WHERE id = ?', (bm_id,))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            logger.error(f"Database delete error: {str(e)}")
            raise Exception("Failed to delete bookmark.")

bookmark_service = BookmarkService()
