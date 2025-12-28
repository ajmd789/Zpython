from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render  # 关键：必须导入render！
from django.conf import settings
import time
from .services.file_service import get_directory_contents
from .services.memo_service import memo_service
from .stock_api_utils import StockApiUtils
from django.views.decorators.http import require_GET, require_POST
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
    # 直接渲染homepage.html模板，无需传递数据
    return render(request, 'zapp/homepage.html')

def index_with_slash(request):
    # 渲染index.html模板
    return render(request, 'zapp/index.html')

def notebook(request):
    # 在服务端获取所有备忘录数据
    try:
        memos = memo_service.get_all_memos()
    except Exception as e:
        memos = []
    # 将备忘录数据传递给模板
    return render(request, 'zapp/memo.html', {'initial_memos': memos})


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


# 备忘录接口
@csrf_exempt
@require_GET
def get_all_memos(request):
    """获取所有备忘录"""
    try:
        memos = memo_service.get_all_memos()
        return JsonResponse({"code": 200, "data": memos, "message": "success"})
    except Exception as e:
        return JsonResponse({"code": 500, "data": None, "message": str(e)})

@csrf_exempt
@require_POST
def add_memo(request):
    """添加新备忘录"""
    try:
        content = request.POST.get('content', '').strip()
        if not content:
            return JsonResponse({"code": 400, "data": None, "message": "Content cannot be empty"})
        new_memo = memo_service.add_memo(content)
        return JsonResponse({"code": 200, "data": new_memo, "message": "success"})
    except Exception as e:
        return JsonResponse({"code": 500, "data": None, "message": str(e)})

@csrf_exempt
@require_POST
def delete_memo(request):
    """删除备忘录"""
    try:
        memo_id = request.POST.get('id')
        if not memo_id:
            return JsonResponse({"code": 400, "data": None, "message": "ID cannot be empty"})
        success = memo_service.delete_memo(int(memo_id))
        if success:
            return JsonResponse({"code": 200, "data": None, "message": "success"})
        else:
            return JsonResponse({"code": 404, "data": None, "message": "Memo not found"})
    except Exception as e:
        return JsonResponse({"code": 500, "data": None, "message": str(e)})

@csrf_exempt
@require_GET
def search_memos(request):
    """搜索备忘录"""
    try:
        keyword = request.GET.get('keyword', '').strip()
        if not keyword:
            return JsonResponse({"code": 400, "data": None, "message": "Keyword cannot be empty"})
        memos = memo_service.search_memos(keyword)
        return JsonResponse({"code": 200, "data": memos, "message": "success"})
    except Exception as e:
        return JsonResponse({"code": 500, "data": None, "message": str(e)})