import os
import sys

def combine_code_files(src_dir, output_file):
    """
    将src_dir目录下的所有文件内容合并到output_file中
    格式：文件名 + 内容（用分隔线包围）
    """
    try:
        # 获取当前脚本所在目录
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 处理源目录路径
        src_dir = os.path.join(script_dir, src_dir)
        if not os.path.exists(src_dir):
            raise FileNotFoundError(f"源目录不存在: {src_dir}")
        
        # 处理输出文件路径
        output_file = os.path.join(script_dir, output_file)
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 统计处理的文件数量
        file_count = 0
        
        with open(output_file, 'w', encoding='utf-8') as out_f:
            # 遍历src目录下的所有文件
            for root, dirs, files in os.walk(src_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, src_dir)
                    
                    # 跳过不需要的文件类型
                    if any(file_path.endswith(ext) for ext in ['.png', '.jpg', '.gif', '.ico', '.svg', '.ttf', '.woff', '.eot', '.woff2']):
                        continue
                    
                    # 写入文件名标题
                    out_f.write(f"\n{'=' * 70}\n")
                    out_f.write(f"文件名: {relative_path}\n")
                    out_f.write(f"{'=' * 70}\n\n")
                    
                    # 读取并写入文件内容
                    try:
                        # 尝试多种编码
                        encodings = ['utf-8', 'latin-1', 'cp1252']
                        for encoding in encodings:
                            try:
                                with open(file_path, 'r', encoding=encoding) as in_f:
                                    out_f.write(in_f.read())
                                file_count += 1
                                break
                            except UnicodeDecodeError:
                                continue
                        else:
                            out_f.write(f"[无法解码文件内容，尝试了多种编码]\n")
                    except Exception as e:
                        out_f.write(f"[文件读取错误: {str(e)}]\n")
                    
                    out_f.write("\n\n")
        
        print(f"成功合并 {file_count} 个文件到: {output_file}")
        return True
    
    except Exception as e:
        print(f"处理过程中出错: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # 配置参数
    SOURCE_DIR = "src"          # 要扫描的源代码目录
    OUTPUT_FILE = "combined_codes.txt"  # 输出文件名
    
    # 执行合并操作
    success = combine_code_files(SOURCE_DIR, OUTPUT_FILE)
    sys.exit(0 if success else 1)