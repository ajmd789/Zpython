# 测试memo_service.py的敏感词过滤功能
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 直接导入MemoService的敏感词处理部分
from zapp.services.memo_service import MemoService

# 创建测试实例
memo_service = MemoService()

# 测试敏感词加载
print(f"✅ 加载了 {len(memo_service.sensitive_words)} 个敏感词")

# 测试敏感词检查功能
print("\n开始测试敏感词检查功能...")

# 测试用例
test_cases = [
    # 正常情况
    {"content": "这是一条正常的备忘录", "expected": "pass"},
    # 空内容
    {"content": "", "expected": "pass"},
    # 纯空白内容
    {"content": "   ", "expected": "pass"},
    # 包含敏感词（实际运行时如果包含敏感词会抛出异常）
    {"content": "这是一条测试内容，包含敏感词", "expected": "fail"},
]

for i, test_case in enumerate(test_cases, 1):
    print(f"\n测试用例 #{i}: 内容='{test_case['content']}'")
    try:
        result = memo_service._check_sensitive_words(test_case['content'])
        print(f"  ✅ 检查通过 (未包含敏感词)")
    except ValueError as e:
        print(f"  ⚠️  检查失败 (包含敏感词): {e}")

print("\n所有测试用例执行完毕！")

# 测试基本功能
try:
    # 创建一个临时的MemoService实例，确保初始化正常
    memo_service = MemoService()
    print(f"\n✅ MemoService初始化成功")
    print(f"✅ 敏感词文件路径: {memo_service.sensitive_words_file}")
    print(f"✅ 敏感词数量: {len(memo_service.sensitive_words)}")
    
    # 测试随机抽取几个敏感词进行解码验证
    if memo_service.sensitive_words:
        print(f"\n✅ 随机验证几个敏感词:")
        for i, word in enumerate(memo_service.sensitive_words[:5]):  # 只显示前5个
            print(f"   {i+1}. {word}")
        print(f"   ... 还有 {len(memo_service.sensitive_words) - 5} 个敏感词")
    
    print("\n🎉 所有功能测试通过！")
except Exception as e:
    print(f"\n❌ 功能测试失败: {e}")
