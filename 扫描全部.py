import os
import sys
import datetime

def combine_all_files(project_dir, output_file, excluded_dirs=None, excluded_exts=None):
    """
    将整个项目目录下的所有代码文件合并到output_file中（排除指定目录和文件类型）
    格式：文件名 + 内容（用分隔线包围）
    """
    try:
        # 设置默认排除项
        if excluded_dirs is None:
            excluded_dirs = ['node_modules', '.git', '__pycache__', 'dist', 'build']
        if excluded_exts is None:
            excluded_exts = ['.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg', 
                            '.ttf', '.woff', '.eot', '.woff2', '.pdf', '.zip', 
                            '.rar', '.exe', '.dll', '.so', '.bin', '.pyc']
        
        # 确保项目目录存在
        if not os.path.exists(project_dir):
            raise FileNotFoundError(f"项目目录不存在: {project_dir}")
        
        # 创建输出文件的目录（如果不存在）
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 统计处理的文件数量
        file_count = 0
        skipped_count = 0
        
        with open(output_file, 'w', encoding='utf-8') as out_f:
            # 写入文件头信息
            out_f.write(f"项目扫描报告\n")
            out_f.write(f"项目目录: {os.path.abspath(project_dir)}\n")
            out_f.write(f"生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            out_f.write(f"{'=' * 70}\n\n")
            
            # 遍历整个项目目录
            for root, dirs, files in os.walk(project_dir):
                # 从遍历列表中移除排除的目录
                dirs[:] = [d for d in dirs if d not in excluded_dirs]
                
                # 处理每个文件
                for file in files:
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, project_dir)
                    
                    # 跳过排除的文件类型
                    if any(file.lower().endswith(ext) for ext in excluded_exts):
                        skipped_count += 1
                        continue
                    
                    # 写入文件名标题
                    out_f.write(f"\n{'=' * 70}\n")
                    out_f.write(f"文件名: {relative_path}\n")
                    out_f.write(f"{'=' * 70}\n\n")
                    
                    # 读取并写入文件内容
                    try:
                        # 尝试多种编码
                        encodings = ['utf-8', 'latin-1', 'cp1252', 'gbk', 'utf-16']
                        content_written = False
                        for encoding in encodings:
                            try:
                                with open(file_path, 'r', encoding=encoding) as in_f:
                                    content = in_f.read()
                                    # 检查内容是否可读（避免写入二进制文件）
                                    if '\0' not in content and len(content) > 0:
                                        out_f.write(content)
                                        file_count += 1
                                        content_written = True
                                        break
                            except UnicodeDecodeError:
                                continue
                            except Exception:
                                continue
                        
                        if not content_written:
                            out_f.write(f"[文件内容无法解码或为空]\n")
                            skipped_count += 1
                    except Exception as e:
                        out_f.write(f"[文件读取错误: {str(e)}]\n")
                        skipped_count += 1
                    
                    out_f.write("\n\n")
        
        print(f"扫描完成！")
        print(f"成功合并 {file_count} 个文件")
        print(f"跳过 {skipped_count} 个文件（排除类型或读取失败）")
        print(f"输出文件: {os.path.abspath(output_file)}")
        return True
    
    except Exception as e:
        print(f"处理过程中出错: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # 配置参数 - 通过设置TARGET_DIR变量指定要扫描的目录
    TARGET_DIR = r"C:\Users\Archimedes\Desktop\codes\java-desktop-data-analysis\src"  # 修改此路径为你要扫描的目录
    OUTPUT_FILE = "project_codes.txt"  # 输出文件名
    
    # 可选：自定义排除项
    EXCLUDED_DIRS = ['node_modules', '.git', 'dist', 'build', '__pycache__', '.webpack']
    EXCLUDED_EXTS = ['.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg', '.ttf', 
                    '.woff', '.eot', '.woff2', '.pdf', '.zip', '.rar', '.exe', 
                    '.dll', '.so', '.bin', '.pyc', '.log', '.DS_Store', '.json']
    
    # 执行合并操作
    success = combine_all_files(
        TARGET_DIR, 
        OUTPUT_FILE,
        excluded_dirs=EXCLUDED_DIRS,
        excluded_exts=EXCLUDED_EXTS
    )
    sys.exit(0 if success else 1)