#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试MemoService的安全增强措施
"""

import sys
import os
import html
import tempfile

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from zapp.services.memo_service import MemoService


def test_xss_protection():
    """测试XSS防护功能"""
    print("\n=== 测试XSS防护功能 ===")
    
    # 创建临时数据库文件
    temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    temp_db_path = temp_db.name
    temp_db.close()
    
    try:
        memo_service = MemoService()
        memo_service.db_path = temp_db_path

        # 测试用例：包含XSS攻击的内容
        xss_test_cases = [
            "<script>alert('XSS')</script>",
            '<img src="x" onerror="alert(\'XSS\')">',
            '<a href="javascript:alert(\'XSS\')">Click me</a>',
            '<div onmouseover="alert(\'XSS\')">Hover me</div>',
        ]
        
        for test_content in xss_test_cases:
            try:
                result = memo_service.add_memo(test_content)
                stored_content = result['content']
                
                # 检查内容是否被正确转义
                if stored_content == html.escape(test_content):
                    print(f"✓ XSS内容 '{test_content}' 被正确转义为: '{stored_content}'")
                else:
                    print(f"✗ XSS内容 '{test_content}' 转义失败，存储为: '{stored_content}'")
                    
                # 清理测试数据
                memo_service.delete_memo(result['id'])
                
            except Exception as e:
                # 忽略数据库错误，因为我们主要测试转义功能
                if "database" in str(e).lower():
                    print(f"⚠ 数据库错误，跳过XSS测试: {e}")
                else:
                    print(f"✗ 测试XSS内容 '{test_content}' 时发生错误: {e}")
    finally:
        # 清理临时文件
        if os.path.exists(temp_db_path):
            os.unlink(temp_db_path)


def test_input_validation():
    """测试输入验证功能"""
    print("\n=== 测试输入验证功能 ===")
    
    memo_service = MemoService()
    
    # 测试空内容
    try:
        memo_service.add_memo("")
        print("✗ 空内容应该被拒绝")
    except ValueError as e:
        print(f"✓ 空内容被正确拒绝: {e}")
    
    # 测试纯空格内容
    try:
        memo_service.add_memo("   ")
        print("✗ 纯空格内容应该被拒绝")
    except ValueError as e:
        print(f"✓ 纯空格内容被正确拒绝: {e}")
    
    # 测试过长内容
    try:
        long_content = "a" * 1001
        memo_service.add_memo(long_content)
        print("✗ 过长内容应该被拒绝")
    except ValueError as e:
        print(f"✓ 过长内容被正确拒绝: {e}")
    
    # 测试delete_memo的输入验证
    invalid_ids = ["abc", 0, -1, 1.5, None]
    for invalid_id in invalid_ids:
        try:
            memo_service.delete_memo(invalid_id)
            print(f"✗ 无效ID '{invalid_id}' 应该被拒绝")
        except ValueError as e:
            print(f"✓ 无效ID '{invalid_id}' 被正确拒绝: {e}")
    
    # 测试search_memos的输入验证
    try:
        memo_service.search_memos(123)
        print("✗ 非字符串关键词应该被拒绝")
    except ValueError as e:
        print(f"✓ 非字符串关键词被正确拒绝: {e}")
    
    try:
        long_keyword = "a" * 101
        memo_service.search_memos(long_keyword)
        print("✗ 过长关键词应该被拒绝")
    except ValueError as e:
        print(f"✓ 过长关键词被正确拒绝: {e}")


def test_sensitive_word_filtering():
    """测试敏感词过滤功能"""
    print("\n=== 测试敏感词过滤功能 ===")
    
    memo_service = MemoService()
    
    # 检查是否加载了敏感词
    if len(memo_service.sensitive_words) == 0:
        print("✗ 没有加载到敏感词")
        return
    
    print(f"✓ 成功加载了 {len(memo_service.sensitive_words)} 个敏感词")
    
    # 测试用例：包含敏感词的内容
    if memo_service.sensitive_words:
        # 取第一个敏感词进行测试
        test_sensitive_word = memo_service.sensitive_words[0]
        
        # 测试不同大小写的敏感词
        test_cases = [
            f"包含敏感词: {test_sensitive_word}",
            f"包含大写敏感词: {test_sensitive_word.upper()}",
            f"包含小写敏感词: {test_sensitive_word.lower()}",
        ]
        
        for test_content in test_cases:
            try:
                memo_service.add_memo(test_content)
                print(f"✗ 包含敏感词的内容 '{test_content}' 应该被拒绝")
            except ValueError as e:
                if "sensitive" in str(e).lower():
                    print(f"✓ 包含敏感词的内容 '{test_content}' 被正确拒绝")
                else:
                    print(f"✗ 拒绝了包含敏感词的内容，但错误信息不明确: {e}")


def test_error_handling():
    """测试错误处理功能"""
    print("\n=== 测试错误处理功能 ===")
    
    memo_service = MemoService()
    
    # 测试无效的数据库路径（需要修改db_path）
    original_db_path = memo_service.db_path
    memo_service.db_path = "/invalid/path/to/database.db"
    
    try:
        memo_service.get_all_memos()
        print("✗ 无效的数据库路径应该抛出异常")
    except Exception as e:
        # 检查错误信息是否不包含敏感信息
        if "invalid" not in str(e).lower() and "path" not in str(e).lower():
            print(f"✓ 无效的数据库路径正确处理，返回通用错误信息: {e}")
        else:
            print(f"✗ 错误信息包含敏感信息: {e}")
    
    # 恢复原始数据库路径
    memo_service.db_path = original_db_path


def test_normal_operations():
    """测试正常操作功能"""
    print("\n=== 测试正常操作功能 ===")
    
    memo_service = MemoService()
    
    # 测试添加正常内容
    normal_content = "这是一条正常的备忘录内容"
    try:
        result = memo_service.add_memo(normal_content)
        print(f"✓ 成功添加正常内容: {result}")
        
        # 测试获取所有备忘录
        all_memos = memo_service.get_all_memos()
        if all_memos:
            print(f"✓ 成功获取所有备忘录，共 {len(all_memos)} 条")
        else:
            print("✗ 获取所有备忘录失败")
            
        # 测试搜索功能
        search_result = memo_service.search_memos("正常")
        if search_result:
            print(f"✓ 成功搜索到内容: {search_result}")
        else:
            print("✗ 搜索功能失败")
            
        # 测试删除功能
        delete_result = memo_service.delete_memo(result['id'])
        if delete_result:
            print(f"✓ 成功删除备忘录")
        else:
            print("✗ 删除备忘录失败")
            
    except Exception as e:
        print(f"✗ 正常操作失败: {e}")


if __name__ == "__main__":
    print("开始测试MemoService的安全增强措施...")
    
    # 运行所有测试
    test_xss_protection()
    test_input_validation()
    test_sensitive_word_filtering()
    test_error_handling()
    test_normal_operations()
    
    print("\n所有测试完成！")
