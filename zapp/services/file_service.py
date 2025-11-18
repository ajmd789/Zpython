# zapp/services/file_service.py
import os

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
                "directory": target_dir,
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