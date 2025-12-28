# zapp/services/file_service.py
import os
import base64
import mimetypes

def get_directory_contents(target_dir):
    """
    读取目标目录的内容，若为txt文件则额外返回文件内容
    :param target_dir: 目标目录路径
    :return: 包含状态码、数据、消息的字典
    """
    try:
        # 检查目录是否存在
        if not os.path.exists(target_dir):
            return {
                "code": 404,
                "data": None,
                "message": f"目录不存在：{target_dir}"
            }
        
        # 检查是否为目录
        if not os.path.isdir(target_dir):
            return {
                "code": 400,
                "data": None,
                "message": f"不是目录：{target_dir}"
            }
        
        # 读取目录内容并构造详细信息
        items = os.listdir(target_dir)
        items_detail = []
        for item in items:
            item_path = os.path.join(target_dir, item)
            item_type = "file" if os.path.isfile(item_path) else "directory"
            modify_time = int(os.path.getmtime(item_path))  # 最后修改时间戳
            
            # 新增：读取txt文件内容（非txt文件或目录则content为None）
            content = None
            if item_type == "file" and item.lower().endswith(".txt"):
                try:
                    # 读取txt文件内容（处理编码问题，Windows常见gbk/utf-8）
                    with open(item_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()  # 读取全部内容（大文件可考虑限制长度）
                except Exception as e:
                    content = f"读取失败：{str(e)}"  # 记录读取错误，不中断整体流程
            
            items_detail.append({
                "name": item,
                "type": item_type,
                "modify_time": modify_time,
                "path": item_path,
                "content": content  # 新增：文件内容（仅txt文件可能有值）
            })
        
        # 返回成功结果
        return {
            "code": 200,
            "data": {
                "directory": str(target_dir),
                "count": len(items_detail),
                "items": items_detail
            },
            "message": "success"
        }
    
    except Exception as e:
        # 捕获目录级别的异常（如权限不足）
        return {
            "code": 500,
            "data": None,
            "message": f"读取目录失败：{str(e)}"
        }

def read_file(file_path, return_type='binary'):
    """
    读取文件内容，支持二进制和base64格式
    :param file_path: 文件路径
    :param return_type: 返回格式，'binary'或'base64'
    :return: 包含状态码、数据、消息的字典
    """
    try:
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return {
                "code": 404,
                "data": None,
                "message": f"文件不存在：{file_path}"
            }
        
        # 检查是否为文件
        if not os.path.isfile(file_path):
            return {
                "code": 400,
                "data": None,
                "message": f"不是文件：{file_path}"
            }
        
        # 获取文件的MIME类型
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            mime_type = 'application/octet-stream'  # 默认MIME类型
        
        # 读取文件内容
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # 根据返回类型处理内容
        if return_type == 'base64':
            # 转换为base64格式
            base64_content = base64.b64encode(content).decode('utf-8')
            return {
                "code": 200,
                "data": {
                    "content": base64_content,
                    "mime_type": mime_type,
                    "encoding": "base64"
                },
                "message": "success"
            }
        else:
            # 返回二进制内容
            return {
                "code": 200,
                "data": {
                    "content": content,
                    "mime_type": mime_type,
                    "encoding": "binary"
                },
                "message": "success"
            }
    
    except Exception as e:
        # 捕获文件读取异常
        return {
            "code": 500,
            "data": None,
            "message": f"读取文件失败：{str(e)}"
        }