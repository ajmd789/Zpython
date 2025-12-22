#!/bin/bash
# 服务器端Python路径修复脚本

echo "=== Python路径修复脚本 ==="
echo "当前工作目录: $(pwd)"
echo ""

# 方法1: 设置PYTHONPATH并测试
echo "方法1: 设置PYTHONPATH环境变量..."
export PYTHONPATH=/var/codes/deploy/backend/backendCodes/zp1:$PYTHONPATH
echo "PYTHONPATH: $PYTHONPATH"

echo ""
echo "测试导入zproject..."
python -c "
import sys
print('当前sys.path:')
for i, p in enumerate(sys.path):
    print(f'  {i}: {p}')

try:
    import zproject
    print('✓ 成功导入zproject')
    print('zproject路径:', zproject.__file__)
except Exception as e:
    print('❌ 导入zproject失败:', e)
"

echo ""
echo "方法2: 使用pythonpath参数启动Gunicorn..."
echo "命令:"
echo "gunicorn zproject.wsgi:application \\"
echo "    --bind 0.0.0.0:5555 \\"
echo "    --workers 1 \\"
echo "    --timeout 30 \\"
echo "    --log-level debug \\"
echo "    --pythonpath /var/codes/deploy/backend/backendCodes/zp1 \\"
echo "    --chdir /var/codes/deploy/backend/backendCodes/zp1"

echo ""
echo "方法3: 使用完整路径启动..."
echo "命令:"
echo "cd /var/codes/deploy/backend/backendCodes/zp1"
echo "export PYTHONPATH=/var/codes/deploy/backend/backendCodes/zp1:$PYTHONPATH"
echo "source venv/bin/activate"
echo "gunicorn zproject.wsgi:application --bind 0.0.0.0:5555 --workers 1 --timeout 30 --log-level debug"

echo ""
echo "=== 推荐的完整修复步骤 ==="
echo "1. 停止当前服务:"
echo "   sudo systemctl stop zpython zpython-monitor"
echo "   pkill -f gunicorn"
echo ""
echo "2. 手动测试启动:"
echo "   cd /var/codes/deploy/backend/backendCodes/zp1"
echo "   export PYTHONPATH=/var/codes/deploy/backend/backendCodes/zp1:$PYTHONPATH"
echo "   source venv/bin/activate"
echo "   gunicorn zproject.wsgi:application --bind 0.0.0.0:5555 --workers 1 --timeout 30 --log-level debug --pythonpath /var/codes/deploy/backend/backendCodes/zp1 --chdir /var/codes/deploy/backend/backendCodes/zp1"
echo ""
echo "3. 如果手动启动成功，重新部署systemd服务:"
echo "   sudo ./install_systemd_service.sh"