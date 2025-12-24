#!/bin/bash
# 服务器端Python路径诊断脚本

echo "=== Python环境诊断 ==="
echo "当前工作目录: $(pwd)"
echo ""

# 检查Python版本和路径
echo "=== Python环境信息 ==="
python -c "
import sys
print('Python版本:', sys.version)
print('Python可执行文件:', sys.executable)
print('当前工作目录:', sys.path[0])
print('Python模块搜索路径:')
for i, path in enumerate(sys.path):
    print(f'  {i}: {path}')
"

echo ""
echo "=== 逐步导入测试 ==="
echo "测试1: 导入zproject"
python -c "
try:
    import zproject
    print('✓ 成功导入zproject')
    print('zproject路径:', zproject.__file__)
except Exception as e:
    print('❌ 导入zproject失败:', e)
    print('当前sys.path:')
    import sys
    for p in sys.path:
        print('  ', p)
"

echo ""
echo "测试2: 导入zproject.wsgi"
python -c "
try:
    import zproject.wsgi
    print('✓ 成功导入zproject.wsgi')
    print('zproject.wsgi路径:', zproject.wsgi.__file__)
    print('WSGI应用:', getattr(zproject.wsgi, 'application', '未找到application'))
except Exception as e:
    print('❌ 导入zproject.wsgi失败:', e)
"

echo ""
echo "=== 文件系统检查 ==="
echo "检查zproject目录是否存在:"
if [ -d "zproject" ]; then
    echo "✓ zproject目录存在"
    echo "zproject目录内容:"
    ls -la zproject/
else
    echo "❌ zproject目录不存在"
fi

echo ""
echo "检查manage.py是否存在:"
if [ -f "manage.py" ]; then
    echo "✓ manage.py存在"
else
    echo "❌ manage.py不存在"
fi

echo ""
echo "=== 虚拟环境检查 ==="
echo "虚拟环境路径: $VIRTUAL_ENV"
if [ -n "$VIRTUAL_ENV" ]; then
    echo "✓ 虚拟环境已激活"
else
    echo "❌ 虚拟环境未激活"
fi