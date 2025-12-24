#!/bin/bash
# 手动调试启动脚本 - 服务器端使用

echo "=== 手动调试启动脚本 ==="
echo "当前工作目录: $(pwd)"
echo ""

# 停止现有服务
echo "1. 停止现有服务..."
sudo systemctl stop zpython zpython-monitor 2>/dev/null || true
pkill -f gunicorn 2>/dev/null || true

echo ""
echo "2. 激活虚拟环境..."
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "✓ 虚拟环境已激活"
else
    echo "❌ 虚拟环境不存在"
    exit 1
fi

echo ""
echo "3. 设置环境变量..."
export PYTHONPATH=/var/codes/deploy/backend/backendCodes/zp1:$PYTHONPATH
echo "PYTHONPATH: $PYTHONPATH"

echo ""
echo "4. 测试Python导入..."
python -c "
import sys
print('Python版本:', sys.version)
print('工作目录:', sys.path[0])
try:
    import zproject
    print('✓ 成功导入zproject')
    print('zproject路径:', zproject.__file__)
    
    import zproject.wsgi
    print('✓ 成功导入zproject.wsgi')
    print('WSGI应用:', getattr(zproject.wsgi, 'application', '未找到'))
except Exception as e:
    print('❌ 导入失败:', e)
    import traceback
    traceback.print_exc()
"

echo ""
echo "5. 启动Gunicorn..."
echo "命令:"
echo "gunicorn zproject.wsgi:application \\"
echo "    --bind 0.0.0.0:5555 \\"
echo "    --workers 1 \\"
echo "    --timeout 30 \\"
echo "    --log-level debug \\"
echo "    --pythonpath /var/codes/deploy/backend/backendCodes/zp1 \\"
echo "    --chdir /var/codes/deploy/backend/backendCodes/zp1"

echo ""
echo "正在启动Gunicorn..."
gunicorn zproject.wsgi:application \
    --bind 0.0.0.0:5555 \
    --workers 1 \
    --timeout 30 \
    --log-level debug \
    --pythonpath /var/codes/deploy/backend/backendCodes/zp1 \
    --chdir /var/codes/deploy/backend/backendCodes/zp1

echo ""
echo "=== 启动完成 ==="
echo "如果启动成功，可以访问: http://$(hostname -I | awk '{print $1}'):5555"
echo ""
echo "查看日志:"
echo "tail -f /var/codes/deploy/backend/backendCodes/zp1/access.log"
echo "tail -f /var/codes/deploy/backend/backendCodes/zp1/error.log"