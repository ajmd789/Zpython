# 服务器端部署修复指南 - Python3版本

## 重要说明
在Linux服务器上，请使用 `python3` 而不是 `python` 来运行脚本：
```bash
# 正确 ✅
python3 scripts/package_server.py --generate-only

# 错误 ❌  
python scripts/package_server.py --generate-only
```

## 快速修复步骤

### 1. 在服务器上生成新的部署文件
```bash
cd /var/codes/deploy/backend/backendCodes/zp1

# 使用Python3生成部署文件
python3 scripts/package_server.py --generate-only
```

### 2. 运行诊断脚本检查问题
```bash
# 运行诊断脚本
bash dist/diagnose_server.sh
```

### 3. 手动测试修复
```bash
# 使用手动调试脚本
bash dist/manual_start_debug.sh
```

### 4. 如果手动测试成功，重新安装systemd服务
```bash
# 停止现有服务
sudo systemctl stop zpython zpython-monitor
pkill -f gunicorn

# 重新安装服务
sudo ./dist/install_systemd_service.sh

# 启动服务
sudo systemctl start zpython zpython-monitor

# 检查状态
sudo systemctl status zpython --no-pager
```

## 关键修复内容

### 启动脚本修复 (`dist/start_production.sh`)
```bash
# 计算项目根目录
PROJECT_ROOT=$(cd "$(dirname "$(dirname "$0")")" && pwd)
echo "项目根目录: $PROJECT_ROOT"

# 设置PYTHONPATH环境变量
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"
echo "PYTHONPATH: $PYTHONPATH"

# 使用gunicorn启动（包含pythonpath和chdir参数）
gunicorn zproject.wsgi:application \
    --bind 0.0.0.0:5555 \
    --workers 2 \
    --timeout 30 \
    --log-level debug \
    --pythonpath "$PROJECT_ROOT" \
    --chdir "$PROJECT_ROOT"
```

### Systemd服务修复 (`dist/zpython.service`)
```ini
[Service]
ExecStart=bash -c 'export PYTHONPATH=PLACEHOLDER_PROJECT_ROOT:$PYTHONPATH && cd PLACEHOLDER_PROJECT_ROOT && PLACEHOLDER_PROJECT_ROOT/venv/bin/gunicorn zproject.wsgi:application --bind 0.0.0.0:5555 --workers 2 --timeout 30 --log-level debug --access-logfile access.log --error-logfile error.log --pythonpath PLACEHOLDER_PROJECT_ROOT --chdir PLACEHOLDER_PROJECT_ROOT'
```

## 备用手动修复方法

如果自动修复不成功，可以尝试：

### 方法A: 直接设置PYTHONPATH
```bash
cd /var/codes/deploy/backend/backendCodes/zp1
export PYTHONPATH=/var/codes/deploy/backend/backendCodes/zp1:$PYTHONPATH
source venv/bin/activate
gunicorn zproject.wsgi:application --bind 0.0.0.0:5555 --workers 1 --timeout 30 --log-level debug --pythonpath /var/codes/deploy/backend/backendCodes/zp1 --chdir /var/codes/deploy/backend/backendCodes/zp1
```

### 方法B: 逐步调试
```bash
# 1. 停止现有服务
sudo systemctl stop zpython zpython-monitor
pkill -f gunicorn

# 2. 激活虚拟环境
cd /var/codes/deploy/backend/backendCodes/zp1
source venv/bin/activate

# 3. 设置PYTHONPATH
export PYTHONPATH=/var/codes/deploy/backend/backendCodes/zp1:$PYTHONPATH

# 4. 测试Python导入
python3 -c "import zproject; print('✓ 成功导入zproject')"

# 5. 启动Gunicorn
gunicorn zproject.wsgi:application --bind 0.0.0.0:5555 --workers 1 --timeout 30 --log-level debug --pythonpath /var/codes/deploy/backend/backendCodes/zp1 --chdir /var/codes/deploy/backend/backendCodes/zp1
```

## 验证修复效果

### 检查服务状态
```bash
sudo systemctl status zpython
sudo systemctl status zpython-monitor
```

### 检查日志
```bash
# 查看应用日志
tail -f /var/codes/deploy/backend/backendCodes/zp1/access.log
tail -f /var/codes/deploy/backend/backendCodes/zp1/error.log

# 查看系统日志
sudo journalctl -u zpython -f
```

### 测试访问
```bash
# 本地测试
curl http://localhost:5555

# 远程测试（替换your-server-ip）
curl http://your-server-ip:5555
```

## 常见问题

### Q: 运行python3命令提示未找到？
A: 安装Python3：
```bash
sudo apt update
sudo apt install python3 python3-pip
```

### Q: 虚拟环境激活失败？
A: 检查虚拟环境是否存在：
```bash
ls -la venv/
# 如果不存在，重新创建
python3 -m venv venv
```

### Q: Gunicorn启动仍然失败？
A: 检查详细错误日志：
```bash
tail -n 50 /var/codes/deploy/backend/backendCodes/zp1/error.log
tail -n 50 /var/codes/deploy/backend/backendCodes/zp1/gunicorn_start.log
```

## 总结

这个修复方案专门针对Linux服务器环境，确保：
1. ✅ 使用Python3正确运行脚本
2. ✅ PYTHONPATH环境变量正确设置
3. ✅ Gunicorn参数正确配置
4. ✅ Systemd服务正确安装

按照上述步骤操作，应该能彻底解决 `ModuleNotFoundError: No module named 'zproject'` 的问题。