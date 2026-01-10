import sqlite3
import os

# 确定数据库路径
db_path = os.path.join(os.path.dirname(__file__), 'accounting.db')

print(f"检查数据库: {db_path}")
print(f"数据库是否存在: {os.path.exists(db_path)}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 检查stock_codes表结构
    print("\nStock Codes Table Structure:")
    cursor.execute('PRAGMA table_info(stock_codes);')
    columns = cursor.fetchall()
    for col in columns:
        print(col)
    
    # 检查是否有codeData列
    column_names = [col[1] for col in columns]
    print(f"\n表中是否有codeData列: {'codeData' in column_names}")
    
    conn.close()
except Exception as e:
    print(f"错误: {e}")
