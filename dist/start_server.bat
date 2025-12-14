@echo off
REM Django项目启动脚本

cd /d "%~dp0"

echo === 启动Django服务器 ===
echo 监听地址: 0.0.0.0:5555
echo.

REM 使用Django开发服务器（Windows环境）
zpython_django.exe runserver 0.0.0.0:5555 --noreload

echo.
echo === 服务已启动 ===
