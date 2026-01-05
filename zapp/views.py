from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render  # 关键：必须导入render！
from django.conf import settings
import time
import os
from .services.file_service import get_directory_contents, read_file
from .services.memo_service import memo_service
from .services.stock_code_service import stock_code_service
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


def duanlian(request):
    """锻炼计时器页面"""
    return render(request, 'zapp/duanlian.html')


def timestamp(request):
    """时间戳转换页面"""
    return render(request, 'zapp/timestamp.html')

@require_GET
def static_file_access(request, file_path):
    """
    静态文件访问接口，支持二进制和base64格式返回
    :param request: HTTP请求对象
    :param file_path: 文件路径（相对于静态文件目录）
    :return: 静态文件内容或错误响应
    """
    try:
        # 确定静态文件目录
        static_dirs = [settings.STATIC_ROOT] + list(settings.STATICFILES_DIRS)
        
        # 查找文件在哪个静态目录中
        found_file = None
        for static_dir in static_dirs:
            full_path = os.path.join(static_dir, file_path)
            if os.path.exists(full_path) and os.path.isfile(full_path):
                found_file = full_path
                break
        
        if not found_file:
            return JsonResponse({"code": 404, "data": None, "message": "文件不存在"}, status=404)
        
        # 获取返回格式
        return_type = request.GET.get('format', 'binary')
        
        # 读取文件
        result = read_file(found_file, return_type)
        
        if result["code"] != 200:
            return JsonResponse(result, status=result["code"])
        
        data = result["data"]
        
        # 根据返回格式构建响应
        if return_type == 'base64':
            return JsonResponse({
                "code": 200,
                "data": {
                    "content": data["content"],
                    "mime_type": data["mime_type"],
                    "encoding": data["encoding"]
                },
                "message": "success"
            })
        else:
            # 返回二进制文件
            response = HttpResponse(data["content"], content_type=data["mime_type"])
            response["Content-Disposition"] = f"inline; filename*=utf-8''{os.path.basename(file_path)}"
            return response
    
    except Exception as e:
            return JsonResponse({"code": 500, "data": None, "message": f"服务器错误：{str(e)}"}, status=500)


@csrf_exempt
@require_POST
def pythongetip(request):
    """
    采集访问者IP的API接口
    只支持POST请求
    """
    import sqlite3
    import os
    from datetime import datetime
    from django.utils import timezone
    
    try:
        # 获取访问者真实IP，增强版，检查多个可能的HTTP头
        ip = None
        
        # 从各种代理头中获取真实IP
        for header in ['HTTP_X_FORWARDED_FOR', 'HTTP_X_REAL_IP', 'HTTP_CLIENT_IP', 'REMOTE_ADDR']:
            if header in request.META:
                potential_ip = request.META[header]
                # 如果是X-Forwarded-For，取第一个IP
                if header == 'HTTP_X_FORWARDED_FOR':
                    potential_ip = potential_ip.split(',')[0].strip()
                # 验证IP格式（简单验证）
                if potential_ip and '.' in potential_ip:
                    ip = potential_ip
                    break
        
        # 如果没有获取到有效IP，使用unknown
        if not ip:
            ip = request.META.get('REMOTE_ADDR', 'unknown')
        
        # 数据库路径，与memo_service保持一致
        if os.name == 'nt':
            db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'accounting.db')
        else:
            db_path = '/var/codes/deploy/backend/backendCodes/the-go/accounting.db'
        
        # 连接数据库并创建表（如果不存在）
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            # 创建ip_visit_records表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ip_visit_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    visit_time TEXT NOT NULL,
                    ip_address TEXT NOT NULL
                )
            ''')
            
            # 获取北京时间
            utc_time = timezone.now()
            beijing_time = utc_time.astimezone(timezone.get_current_timezone())
            visit_time = beijing_time.strftime('%Y-%m-%d %H:%M:%S')
            
            # 插入数据
            cursor.execute(
                'INSERT INTO ip_visit_records (visit_time, ip_address) VALUES (?, ?)',
                (visit_time, ip)
            )
            conn.commit()
        
        # 返回成功响应
        return JsonResponse({
            "code": 200,
            "data": {
                "ip": ip,
                "message": "IP采集成功"
            },
            "message": "success"
        })
    except Exception as e:
        return JsonResponse({
            "code": 500,
            "data": None,
            "message": f"IP采集失败：{str(e)}"
        }, status=500)


@require_GET
def noUseCode(request):
    """
    获取一个未使用的股票代码
    :param request: HTTP请求对象
    :return: 包含未使用股票代码的JSON响应
    """
    try:
        # 获取未使用的股票代码
        unused_code = stock_code_service.get_unused_code()
        
        if not unused_code:
            return JsonResponse({
                "code": 404,
                "data": None,
                "message": "没有可用的未使用股票代码"
            }, status=404)
        
        return JsonResponse({
            "code": 200,
            "data": {
                "code": unused_code["code"]
            },
            "message": "success"
        })
    except Exception as e:
        return JsonResponse({
            "code": 500,
            "data": None,
            "message": f"获取未使用代码失败：{str(e)}"
        }, status=500)


@csrf_exempt
@require_POST
def addTodayCode(request):
    """
    标记股票代码为已使用
    :param request: HTTP请求对象，必须包含code和codeData参数
    :return: 操作结果的JSON响应
    """
    try:
        # 获取要标记的股票代码
        code = request.POST.get('code')
        if not code:
            return JsonResponse({
                "code": 400,
                "data": None,
                "message": "缺少code参数"
            }, status=400)
        
        # 校验codeData字段必须存在（即使值为空）
        if 'codeData' not in request.POST:
            return JsonResponse({
                "code": 400,
                "data": None,
                "message": "缺少codeData参数"
            }, status=400)
        
        # 获取codeData参数
        codeData = request.POST.get('codeData', '')
        
        # 标记代码为已使用
        success = stock_code_service.mark_code_as_used(code, codeData)
        
        if success:
            return JsonResponse({
                "code": 200,
                "data": None,
                "message": "success"
            })
        else:
            return JsonResponse({
                "code": 404,
                "data": None,
                "message": "股票代码不存在"
            }, status=404)
    except Exception as e:
        return JsonResponse({
            "code": 500,
            "data": None,
            "message": f"标记代码为已使用失败：{str(e)}"
        }, status=500)

@require_GET
def getCodeInfo(request):
    """
    获取指定股票代码的详细信息
    :param request: HTTP请求对象，包含code参数
    :return: 代码详细信息的JSON响应
    """
    try:
        # 获取要查询的股票代码
        code = request.GET.get('code')
        if not code:
            return JsonResponse({
                "code": 400,
                "data": None,
                "message": "缺少code参数"
            }, status=400)
        
        # 获取代码信息
        code_info = stock_code_service.get_code_info(code)
        
        if not code_info:
            return JsonResponse({
                "code": 404,
                "data": None,
                "message": "股票代码不存在"
            }, status=404)
        
        return JsonResponse({
            "code": 200,
            "data": code_info,
            "message": "success"
        })
    except Exception as e:
        return JsonResponse({
            "code": 500,
            "data": None,
            "message": f"获取代码信息失败：{str(e)}"
        }, status=500)

@require_GET
def getAllUsedCodes(request):
    """
    获取所有已使用的股票代码及其详细信息
    :param request: HTTP请求对象
    :return: 已使用代码列表的JSON响应
    """
    try:
        # 获取所有已使用的代码
        used_codes = stock_code_service.get_all_used_codes()
        
        return JsonResponse({
            "code": 200,
            "data": used_codes,
            "message": "success"
        })
    except Exception as e:
        return JsonResponse({
            "code": 500,
            "data": None,
            "message": f"获取已使用代码失败：{str(e)}"
        }, status=500)