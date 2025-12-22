# Linux服务器部署修复指南

## 问题分析

在Linux服务器上运行部署脚本时，静态文件收集失败，错误信息：
```
django.core.exceptions.ImproperlyConfigured: You're using the staticfiles app without having set the STATIC_ROOT setting to a filesystem path.
```

这是因为Django项目的`settings.py`文件中缺少`STATIC_ROOT`配置，该配置用于指定静态文件收集的目标目录。

## 修复步骤

### 1. 登录到Linux服务器

```bash
ssh ubuntu@VM-24-8-ubuntu
```

### 2. 进入项目目录

```bash
cd /var/codes/deploy/backend/backendCodes/zp1
```

### 3. 修改settings.py文件

使用编辑器打开settings.py文件：

```bash
nano zproject/settings.py
```

找到静态文件配置部分（通常在文件末尾）：

```python
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
```

在`STATIC_URL`配置下方添加`STATIC_ROOT`配置：

```python
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
```

### 4. 保存并退出编辑器

在nano编辑器中，按`Ctrl+O`保存文件，然后按`Ctrl+X`退出。

### 5. 重新运行部署脚本

```bash
python3 scripts/package.py
```

## 验证修复

成功运行部署脚本后，应该能看到以下输出：
```
2025-12-22 23:56:21 - INFO - 收集静态文件...
2025-12-22 23:56:21 - INFO - 静态文件收集成功
```

## 其他注意事项

1. 确保虚拟环境已激活
2. 确保所有依赖已正确安装
3. 检查服务器上的Python版本是否与项目要求一致

如果修复后仍然遇到问题，请查看详细日志文件：
```bash
cat logs/package.log
```