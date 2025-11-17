from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render  # 关键：必须导入render！
import time
def chat_page(request):
    return render(request, 'zapp/chat.html')  # 渲染测试页面

# 新增POST接口：返回时间戳
@csrf_exempt  # 关键：禁用CSRF验证，否则POST请求会被拦截（适合内部接口）
def timestamp_api(request):
    if request.method == 'POST':
        # 获取当前时间戳（秒级，浮点数），可转为整数
        current_timestamp = int(time.time())  # 例如：1731780000
        # 构造响应结构
        response_data = {
            "code": 200,  # 200表示成功
            "data": current_timestamp,
            "message": "success"
        }
        return JsonResponse(response_data)
    else:
        # 非POST请求返回错误
        return JsonResponse({
            "code": 405,
            "data": None,
            "message": "Method not allowed (仅支持POST)"
        }, status=405)