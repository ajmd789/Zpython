#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试股票代码服务的get_unused_code方法
"""

import sys
import os

# 将项目根目录添加到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 配置Django设置
import django
from django.conf import settings

if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY='test-secret-key',
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_accounting.db'),
            }
        },
        INSTALLED_APPS=[
            'zapp',
        ],
        ASSETS_DIR=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets'),
        STATIC_ROOT=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static'),
        STATICFILES_DIRS=[
            os.path.join(os.path.dirname(os.path.abspath(__file__)), 'staticfiles'),
        ],
        USE_TZ=True,
        TIME_ZONE='Asia/Shanghai',
    )
    django.setup()

from zapp.services.stock_code_service import stock_code_service

def test_randomness():
    """
    测试get_unused_code是否返回随机的代码
    """
    print("测试get_unused_code方法的随机性...")
    
    # 重置所有代码为未使用状态，以便进行测试
    print("重置所有代码为未使用状态...")
    stock_code_service.reset_code_usage()
    
    # 连续调用10次，检查返回的代码是否有随机性
    codes = set()
    for i in range(10):
        code = stock_code_service.get_unused_code()
        if code:
            code_value = code['code']
            codes.add(code_value)
            print(f"第{i+1}次调用返回: {code_value}")
        else:
            print(f"第{i+1}次调用返回: None")
    
    print(f"\n10次调用中返回了{len(codes)}个不同的代码")
    if len(codes) > 1:
        print("✅ 测试通过: 返回的代码具有随机性")
    else:
        print("❌ 测试失败: 返回的代码没有随机性")
    
    return len(codes) > 1

def test_uniqueness():
    """
    测试get_unused_code返回的代码是否唯一
    """
    print("\n测试get_unused_code方法的唯一性...")
    
    # 重置所有代码为未使用状态，以便进行测试
    print("重置所有代码为未使用状态...")
    stock_code_service.reset_code_usage()
    
    # 调用多次，检查是否有重复的代码返回
    codes = set()
    duplicates = set()
    
    # 调用20次，检查是否有重复
    for i in range(20):
        code = stock_code_service.get_unused_code()
        if code:
            code_value = code['code']
            if code_value in codes:
                duplicates.add(code_value)
            codes.add(code_value)
            print(f"第{i+1}次调用返回: {code_value}")
        else:
            print(f"第{i+1}次调用返回: None (没有更多未使用代码)")
            break
    
    print(f"\n20次调用中返回了{len(codes)}个代码")
    if duplicates:
        print(f"❌ 测试失败: 发现重复代码: {duplicates}")
    else:
        print("✅ 测试通过: 所有返回的代码都是唯一的")
    
    return len(duplicates) == 0

def test_concurrency_safety():
    """
    模拟并发请求，测试get_unused_code的并发安全性
    """
    import threading
    
    print("\n测试get_unused_code方法的并发安全性...")
    
    # 重置所有代码为未使用状态，以便进行测试
    print("重置所有代码为未使用状态...")
    stock_code_service.reset_code_usage()
    
    codes = set()
    duplicates = set()
    lock = threading.Lock()
    
    def worker():
        """并发执行的工作函数"""
        nonlocal codes, duplicates
        for _ in range(5):
            code = stock_code_service.get_unused_code()
            if code:
                code_value = code['code']
                with lock:
                    if code_value in codes:
                        duplicates.add(code_value)
                    codes.add(code_value)
    
    # 创建10个线程，每个线程调用5次
    threads = []
    for _ in range(10):
        t = threading.Thread(target=worker)
        threads.append(t)
        t.start()
    
    # 等待所有线程完成
    for t in threads:
        t.join()
    
    print(f"\n10个线程共调用50次，返回了{len(codes)}个不同的代码")
    if duplicates:
        print(f"❌ 测试失败: 并发调用中发现重复代码: {duplicates}")
    else:
        print("✅ 测试通过: 并发调用中没有发现重复代码")
    
    return len(duplicates) == 0

if __name__ == "__main__":
    print("开始测试stock_code_service的get_unused_code方法\n")
    
    # 运行测试
    results = []
    results.append(test_randomness())
    results.append(test_uniqueness())
    results.append(test_concurrency_safety())
    
    # 总结测试结果
    print("\n" + "="*50)
    print("测试总结:")
    print(f"总测试数: {len(results)}")
    print(f"通过测试数: {sum(results)}")
    
    if all(results):
        print("\n🎉 所有测试通过! get_unused_code方法符合要求")
        sys.exit(0)
    else:
        print("\n⚠️  部分测试失败，请检查代码")
        sys.exit(1)
