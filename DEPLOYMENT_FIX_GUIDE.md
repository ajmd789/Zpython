# Django项目部署修复方案

## 问题分析
部署到Linux服务器时出现 `ModuleNotFoundError: No module named 'zproject'` 错误，原因是Python无法找到项目根目录中的zproject模块。

## 根本原因
1. Gunicorn启动时的工作目录不正确
2. Python模块搜索路径(PYTHONPATH)未包含项目根目录
3. Systemd服务配置缺少PYTHONPATH设置

## 修复方案

### 1. 已完成的代码修复

#### package.py 修改内容：
- **启动脚本**: 添加了PYTHONPATH环境变量设置和pythonpath参数
- **Systemd服务**: 使用bash shell包装器设置PYTHONPATH
- **调试日志**: 增加了debug级别的日志输出

#### 生成的关键文件：
- `dist/start_production.sh` - 包含PYTHONPATH的启动脚本
- `dist/zpython.service` - 修复后的systemd服务配置

### 2. 服务器端操作步骤

#### 步骤1: 上传新的部署文件
```bash
# 在本地重新生成部署文件
python scripts/package.py --generate-only

# 上传到服务器（替换现有文件）
scp -r dist/* user@server:/var/codes/deploy/backend/backendCodes/zp1/dist/
```

#### 步骤2: 诊断当前环境
```bash
# 进入项目目录
cd /var/codes/deploy/backend/backendCodes/zp1

# 运行诊断脚本
python scripts/diagnose_server.py
```

#### 步骤3: 手动测试修复
```bash
# 使用手动调试脚本
bash scripts/manual_start_debug.py
```

#### 步骤4: 重新安装systemd服务
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

### 3. 验证修复效果

#### 检查服务状态：
```bash
sudo systemctl status zpython
sudo systemctl status zpython-monitor
```

#### 检查日志文件：
```bash
tail -f /var/codes/deploy/backend/backendCodes/zp1/access.log
tail -f /var/codes/deploy/backend/backendCodes/zp1/error.log
```

#### 测试应用访问：
```bash
curl http://localhost:5555
curl http://your-server-ip:5555
```

### 4. 关键配置说明

#### 启动脚本关键配置：
```bash
# 计算项目根目录
PROJECT_ROOT=$(cd "$(dirname "$(dirname "$0")")" && pwd)

# 设置PYTHONPATH环境变量
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# 使用gunicorn启动（包含pythonpath和chdir参数）
gunicorn zproject.wsgi:application \
    --bind 0.0.0.0:5555 \
    --workers 2 \
    --timeout 30 \
    --log-level debug \
    --pythonpath "$PROJECT_ROOT" \
    --chdir "$PROJECT_ROOT"
```

#### Systemd服务关键配置：
```ini
[Service]
ExecStart=bash -c 'export PYTHONPATH=PLACEHOLDER_PROJECT_ROOT:$PYTHONPATH && cd PLACEHOLDER_PROJECT_ROOT && PLACEHOLDER_PROJECT_ROOT/venv/bin/gunicorn zproject.wsgi:application --bind 0.0.0.0:5555 --workers 2 --timeout 30 --log-level debug --access-logfile access.log --error-logfile error.log --pythonpath PLACEHOLDER_PROJECT_ROOT --chdir PLACEHOLDER_PROJECT_ROOT'
```

### 5. 备用修复方法

如果自动修复不成功，可以尝试：

#### 方法A: 直接修改环境变量
```bash
export PYTHONPATH=/var/codes/deploy/backend/backendCodes/zp1:$PYTHONPATH
```

#### 方法B: 使用绝对路径启动
```bash
cd /var/codes/deploy/backend/backendCodes/zp1
source venv/bin/activate
export PYTHONPATH=/var/codes/deploy/backend/backendCodes/zp1:$PYTHONPATH
gunicorn zproject.wsgi:application --bind 0.0.0.0:5555 --workers 1 --timeout 30 --log-level debug --pythonpath /var/codes/deploy/backend/backendCodes/zp1 --chdir /var/codes/deploy/backend/backendCodes/zp1
```

#### 方法C: 修改Python路径配置
在`zproject/__init__.py`中添加：
```python
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
```

### 6. 监控和维护

#### 设置日志轮转：
```bash
# 创建日志轮转配置
sudo tee /etc/logrotate.d/zpython << EOF
/var/codes/deploy/backend/backendCodes/zp1/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644 Archimedes Archimedes
}
EOF
```

#### 监控服务状态：
```bash
# 查看服务日志
sudo journalctl -u zpython -f
sudo journalctl -u zpython-monitor -f

# 检查端口监听
netstat -tlnp | grep 5555
```

## 总结

这个修复方案通过多层保护确保Python能够正确找到zproject模块：
1. 设置PYTHONPATH环境变量
2. 使用gunicorn的pythonpath参数
3. 使用gunicorn的chdir参数确保正确的工作目录
4. 在systemd服务中使用bash包装器确保环境变量生效

这样应该能够彻底解决`ModuleNotFoundError: No module named 'zproject'`的问题。