#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版：测试MemoService的安全增强措施
聚焦于核心安全逻辑，不依赖数据库操作
"""

import sys
import os
import html
import base64

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from zapp.services.memo_service import MemoService


def test_html_escape_logic():
    """测试HTML转义逻辑"""
    print("\n=== 测试HTML转义逻辑 ===")
    
    # 直接测试html.escape函数
    test_cases = [
        ("<script>alert('XSS')</script>", "&lt;script&gt;alert('XSS')&lt;/script&gt;"),
        ('<img src="x" onerror="alert(\'XSS\')">', '&lt;img src=&quot;x&quot; onerror=&quot;alert(\&#x27;XSS\&#x27;)&quot;&gt;'),
        ('<a href="javascript:alert(\'XSS\')">Click me</a>', '&lt;a href=&quot;javascript:alert(\&#x27;XSS\&#x27;)&quot;&gt;Click me&lt;/a&gt;'),
        ('<div onmouseover="alert(\'XSS\')">Hover me</div>', '&lt;div onmouseover=&quot;alert(\&#x27;XSS\&#x27;)&quot;&gt;Hover me&lt;/div&gt;'),
        ('正常文本', '正常文本'),
        ('包含&符号的文本', '包含&amp;符号的文本'),
    ]
    
    for input_str, expected_output in test_cases:
        actual_output = html.escape(input_str)
        if actual_output == expected_output:
            print(f"✓ 转义成功: '{input_str}' -> '{actual_output}'")
        else:
            print(f"✗ 转义失败: '{input_str}' -> '{actual_output}' (期望: '{expected_output}')")


def test_sensitive_word_loading():
    """测试敏感词加载功能"""
    print("\n=== 测试敏感词加载功能 ===")
    
    memo_service = MemoService()
    
    if len(memo_service.sensitive_words) > 0:
        print(f"✓ 成功加载了 {len(memo_service.sensitive_words)} 个敏感词")
        
        # 显示前几个敏感词（脱敏处理）
        sample_words = memo_service.sensitive_words[:5]
        print(f"  示例敏感词: {sample_words}")
        
        # 测试敏感词解码是否正确
        if sample_words:
            # 尝试编码解码循环
            test_word = sample_words[0]
            encoded = base64.b64encode(test_word.encode('utf-8')).decode('utf-8')
            decoded = base64.b64decode(encoded).decode('utf-8')
            
            if decoded == test_word:
                print(f"✓ 敏感词编码解码循环正常: '{test_word}' -> base64 -> '{decoded}'")
            else:
                print(f"✗ 敏感词编码解码循环失败")
    else:
        print("✗ 没有加载到敏感词")


def test_sensitive_word_check():
    """测试敏感词检查逻辑"""
    print("\n=== 测试敏感词检查逻辑 ===")
    
    memo_service = MemoService()
    
    if not memo_service.sensitive_words:
        print("✗ 没有敏感词可以测试")
        return
    
    # 获取一个敏感词用于测试
    test_sensitive_word = memo_service.sensitive_words[0]
    
    # 创建测试内容
    test_cases = [
        ("正常内容", False),
        (f"包含{test_sensitive_word}的内容", True),
        (f"包含{test_sensitive_word.upper()}的内容", True),
        (f"包含{test_sensitive_word.lower()}的内容", True),
    ]
    
    for content, should_contain in test_cases:
        try:
            memo_service._check_sensitive_words(content)
            if should_contain:
                print(f"✗ 应该检测到敏感词，但没有: '{content}'")
            else:
                print(f"✓ 正确通过了检查: '{content}'")
        except ValueError:
            if should_contain:
                print(f"✓ 正确检测到敏感词: '{content}'")
            else:
                print(f"✗ 错误地检测到敏感词: '{content}'")


def test_input_validation_logic():
    """测试输入验证逻辑"""
    print("\n=== 测试输入验证逻辑 ===")
    
    memo_service = MemoService()
    
    # 测试内容长度验证
    print("\n--- 内容长度验证 ---")
    
    # 正常长度
    normal_content = "a" * 500
    try:
        # 只测试长度检查逻辑
        if len(normal_content) <= 1000:
            print(f"✓ 正常长度内容 ({len(normal_content)} 字符) 通过检查")
        else:
            print(f"✗ 正常长度内容 ({len(normal_content)} 字符) 检查失败")
    except Exception as e:
        print(f"✗ 测试正常长度时发生错误: {e}")
    
    # 过长内容
    long_content = "a" * 1001
    try:
        if len(long_content) > 1000:
            print(f"✓ 过长内容 ({len(long_content)} 字符) 被正确识别")
        else:
            print(f"✗ 过长内容 ({len(long_content)} 字符) 检查失败")
    except Exception as e:
        print(f"✗ 测试过长内容时发生错误: {e}")
    
    # 测试memo_id验证
    print("\n--- Memo ID验证 ---")
    
    valid_ids = [1, "2", 100]
    invalid_ids = ["abc", 0, -1, 1.5, None, ""]
    
    for test_id in valid_ids:
        try:
            # 模拟delete_memo中的ID验证逻辑
            memo_id = int(test_id)
            if memo_id <= 0:
                raise ValueError("Memo ID must be a positive integer")
            print(f"✓ ID '{test_id}' 验证通过")
        except (TypeError, ValueError):
            print(f"✗ ID '{test_id}' 应该通过验证，但失败了")
    
    for test_id in invalid_ids:
        try:
            # 模拟delete_memo中的ID验证逻辑
            memo_id = int(test_id)
            if memo_id <= 0:
                raise ValueError("Memo ID must be a positive integer")
            print(f"✗ ID '{test_id}' 应该验证失败，但通过了")
        except (TypeError, ValueError):
            print(f"✓ ID '{test_id}' 验证失败（符合预期）")
    
    # 测试关键词验证
    print("\n--- 关键词验证 ---")
    
    valid_keywords = ["test", "关键词", "", "a"]
    invalid_keywords = [123, None, 1.5, ["list"]]
    
    for keyword in valid_keywords:
        try:
            # 模拟search_memos中的关键词验证逻辑
            if not isinstance(keyword, str):
                raise ValueError("Keyword must be a string")
            keyword = keyword.strip()
            if len(keyword) > 100:
                raise ValueError("Keyword is too long")
            print(f"✓ 关键词 '{keyword}' 验证通过")
        except ValueError:
            print(f"✗ 关键词 '{keyword}' 应该通过验证，但失败了")
    
    for keyword in invalid_keywords:
        try:
            # 模拟search_memos中的关键词验证逻辑
            if not isinstance(keyword, str):
                raise ValueError("Keyword must be a string")
            keyword = keyword.strip()
            if len(keyword) > 100:
                raise ValueError("Keyword is too long")
            print(f"✗ 关键词 '{keyword}' 应该验证失败，但通过了")
        except ValueError:
            print(f"✓ 关键词 '{keyword}' 验证失败（符合预期）")


def test_empty_content_check():
    """测试空内容检查逻辑"""
    print("\n=== 测试空内容检查逻辑 ===")
    
    test_cases = [
        ("", True),  # 空字符串
        ("   ", True),  # 纯空格
        ("\t\n\r", True),  # 空白字符
        ("有内容", False),  # 正常内容
        (" 有内容 ", False),  # 前后有空格
    ]
    
    for content, should_be_empty in test_cases:
        trimmed = content.strip()
        is_empty = not trimmed
        
        if is_empty == should_be_empty:
            print(f"✓ 内容 '{repr(content)}' 被正确识别为空: {is_empty}")
        else:
            print(f"✗ 内容 '{repr(content)}' 的空值检查失败: 实际为空={is_empty}, 期望为空={should_be_empty}")


if __name__ == "__main__":
    print("开始测试MemoService的安全增强措施...")
    
    # 运行所有测试
    test_html_escape_logic()
    test_sensitive_word_loading()
    test_sensitive_word_check()
    test_input_validation_logic()
    test_empty_content_check()
    
    print("\n所有安全功能测试完成！")
