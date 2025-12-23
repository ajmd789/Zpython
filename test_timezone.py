# test_timezone.py
import os
import sys

# 添加Django项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 设置Django环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zproject.settings')

# 导入Django并初始化
import django
django.setup()

# 测试时区功能
from django.utils import timezone
from datetime import datetime

def test_timezone():
    print("=== Django Timezone Test ===")
    print(f"Django TIME_ZONE setting: {django.conf.settings.TIME_ZONE}")
    print(f"USE_TZ setting: {django.conf.settings.USE_TZ}")
    
    # 使用Django的timezone.now()
    django_time = timezone.now()
    print(f"\nDjango timezone.now(): {django_time}")
    print(f"Django timezone.now() timezone: {django_time.tzinfo}")
    
    # 获取当前时区（北京时间）
    current_tz = timezone.get_current_timezone()
    print(f"\nCurrent timezone from Django: {current_tz}")
    
    # 转换为北京时间
    beijing_time = django_time.astimezone(current_tz)
    print(f"Converted to Beijing time: {beijing_time}")
    print(f"Beijing time timezone: {beijing_time.tzinfo}")
    
    # 格式化显示（北京时间）
    beijing_time_str = beijing_time.strftime('%Y-%m-%d %H:%M:%S')
    print(f"Formatted Beijing time: {beijing_time_str}")
    
    # 对比Python原生datetime.now()
    native_time = datetime.now()
    print(f"\nPython native datetime.now(): {native_time}")
    print(f"Python native datetime.now() timezone: {native_time.tzinfo}")
    
    return beijing_time_str

if __name__ == "__main__":
    test_timezone()