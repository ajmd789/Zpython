#!/bin/bash
# Django项目生产环境启动脚本

# 进入脚本所在目录
cd "$(dirname "$0")"

echo "=== 启动Django生产服务器（Gunicorn） ==="
echo "监听地址: 0.0.0.0:5555"
echo "Worker数量: 2"
echo "超时时间: 30秒"
echo ""

# 使用gunicorn启动生产服务器
./zpython_django gunicorn zproject.wsgi:application     --bind 0.0.0.0:5555     --workers 2     --timeout 30     --log-level info     --access-logfile access.log     --error-logfile error.log

echo ""
echo "=== 服务已启动 ==="
echo "访问地址: http://$(hostname -I | awk '{print $1}'):5555"
echo ""
echo "若要设置开机自启，请运行："
echo "sudo ./install_systemd_service.sh"
