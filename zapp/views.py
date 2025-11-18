from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render  # 关键：必须导入render！
from django.conf import settings
import time
from .services.file_service import get_directory_contents
from .stock_api_utils import StockApiUtils
from django.views.decorators.http import require_GET
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
        
def get_all_codes(request):
    if request.method == 'GET':
        # 调用业务逻辑处理（核心逻辑在file_service中）
        # 使用 Django 设置中的 ASSETS_DIR，避免直接引用未定义的全局变量
        assets_dir = getattr(settings, 'ASSETS_DIR', None)
        if not assets_dir:
            return JsonResponse({
                "code": 500,
                "data": None,
                "message": "Server configuration error: ASSETS_DIR not set"
            }, status=500)

        result = get_directory_contents(assets_dir)
        # 根据业务逻辑的结果返回响应
        return JsonResponse(result, status=result["code"])
    else:
        return JsonResponse({
            "code": 405,
            "data": None,
            "message": "Method not allowed (仅支持GET)"
        }, status=405)

def index(request):
    # 直接渲染index.html模板，无需传递数据（数据通过前端JS获取）
    return render(request, 'zapp/index.html')


@require_GET
def fetch_stock(request):
    """通过 StockApiUtils 获取单只股票的数据并返回 JSON。

    GET 参数:
        code: 股票代码（例如 003029 或 sh600519）
    """
    code = request.GET.get('code')
    if not code:
        return JsonResponse({"code": 400, "data": None, "message": "Missing 'code' parameter"}, status=400)

    # 支持用户传入例如 '003029' 或 'sh003029' 等，如果没有市场前缀，默认尝试原样使用
    stock_api = StockApiUtils(code)
    result = stock_api.fetch_stock_data()

    # 如果 fetch_stock_data 返回 {'success': False, 'error': ...} 则映射为 502
    if isinstance(result, dict) and result.get('success') is False:
        return JsonResponse({"code": 502, "data": None, "message": result.get('error')} , status=502)

    # 否则返回获取到的原始数据（状态码200）
    return JsonResponse({"code": 200, "data": result, "message": "success"})