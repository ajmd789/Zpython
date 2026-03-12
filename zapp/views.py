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


# --- 设备心跳监控相关接口 ---

from .models import Device
import json
from django.utils import timezone
import datetime

@csrf_exempt
@require_POST
def heartbeat_api(request):
    """
    接收设备心跳上报
    参数:
        device_name: 设备名称
        timestamp: 时间戳 (可选，如果不传则使用服务器时间)
    """
    import sqlite3
    import os
    try:
        # 尝试从 JSON body 解析
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                 return JsonResponse({"code": 400, "data": None, "message": "Invalid JSON"})
        else:
            # 尝试从 POST 表单解析
            data = request.POST

        device_name = data.get('device_name')
        if not device_name:
            return JsonResponse({"code": 400, "data": None, "message": "Missing 'device_name'"})

        # 获取IP地址
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')

        # 处理时间戳
        ts = data.get('timestamp')
        if ts:
            try:
                # 支持秒或毫秒
                ts = float(ts)
                if ts > 10000000000: # 大于 100亿，认为是毫秒
                    ts = ts / 1000.0
                
                try:
                    heartbeat_time_obj = datetime.datetime.fromtimestamp(ts, tz=timezone.get_current_timezone())
                except AttributeError:
                    import datetime as dt_module
                    heartbeat_time_obj = dt_module.datetime.fromtimestamp(ts, tz=timezone.get_current_timezone())
                
                heartbeat_time = heartbeat_time_obj.strftime('%Y-%m-%d %H:%M:%S')
            except (ValueError, TypeError):
                heartbeat_time = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        else:
            heartbeat_time = timezone.now().strftime('%Y-%m-%d %H:%M:%S')

        # 数据库路径，与 pythongetip 保持一致
        if os.name == 'nt':
            db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'accounting.db')
        else:
            db_path = '/var/codes/deploy/backend/backendCodes/the-go/accounting.db'

        # 连接数据库并创建表（如果不存在）
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            # 创建 zapp_device 表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS zapp_device (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    last_heartbeat TEXT,
                    ip_address TEXT,
                    status TEXT DEFAULT 'offline'
                )
            ''')
            
            # 检查设备是否存在
            cursor.execute('SELECT id FROM zapp_device WHERE name = ?', (device_name,))
            row = cursor.fetchone()
            
            if row:
                # 更新
                cursor.execute('''
                    UPDATE zapp_device 
                    SET last_heartbeat = ?, ip_address = ?, status = 'online'
                    WHERE name = ?
                ''', (heartbeat_time, ip, device_name))
            else:
                # 插入
                cursor.execute('''
                    INSERT INTO zapp_device (name, last_heartbeat, ip_address, status)
                    VALUES (?, ?, ?, 'online')
                ''', (device_name, heartbeat_time, ip))
            
            conn.commit()

        return JsonResponse({
            "code": 200, 
            "data": {
                "device_name": device_name, 
                "status": "online",
                "last_heartbeat": heartbeat_time
            }, 
            "message": "Heartbeat received"
        })

    except Exception as e:
        return JsonResponse({"code": 500, "data": None, "message": str(e)})


@require_GET
def get_devices_api(request):
    """获取所有设备列表及其在线状态"""
    import sqlite3
    import os
    try:
        # 数据库路径
        if os.name == 'nt':
            db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'accounting.db')
        else:
            db_path = '/var/codes/deploy/backend/backendCodes/the-go/accounting.db'
            
        with sqlite3.connect(db_path) as conn:
            # 以字典形式返回行
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 确保表存在，防止首次查询报错
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS zapp_device (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    last_heartbeat TEXT,
                    ip_address TEXT,
                    status TEXT DEFAULT 'offline'
                )
            ''')
            
            cursor.execute('SELECT * FROM zapp_device ORDER BY last_heartbeat DESC')
            rows = cursor.fetchall()
            
            data = []
            now = timezone.now()
            
            for row in rows:
                last_hb_str = row['last_heartbeat']
                is_online = False
                
                # 计算在线状态 (5分钟内)
                if last_hb_str:
                    try:
                        # 尝试解析时间字符串
                        try:
                            hb_time = datetime.datetime.strptime(last_hb_str, '%Y-%m-%d %H:%M:%S')
                        except AttributeError:
                             import datetime as dt_module
                             hb_time = dt_module.datetime.strptime(last_hb_str, '%Y-%m-%d %H:%M:%S')
                        
                        # 如果存储的是 UTC 时间（简单起见，这里假设存储的是本地时间，因为我们用了 timezone.now()）
                        # 如果需要严谨的时区处理，需要更多逻辑。这里简化处理：
                        # 将 hb_time 视为 naive (无时区)，now 也转为 naive 进行比较，或者都视为 UTC
                        # 由于 timezone.now() 是带时区的，我们把它转为 naive (或者直接比较时间差)
                        
                        # 简单起见，直接用当前时间字符串比较（不推荐，但为了兼容性...）
                        # 更好的做法：将 now 转为 naive
                        if timezone.is_aware(hb_time):
                            hb_time = timezone.make_naive(hb_time)
                        
                        now_naive = timezone.now()
                        if timezone.is_aware(now_naive):
                            now_naive = timezone.make_naive(now_naive)
                            
                        if (now_naive - hb_time).total_seconds() < 300: # 5分钟
                            is_online = True
                    except Exception:
                        pass # 解析失败视为离线
                
                data.append({
                    "name": row['name'],
                    "last_heartbeat": last_hb_str,
                    "ip_address": row['ip_address'],
                    "status": "online" if is_online else "offline"
                })
                
        return JsonResponse({"code": 200, "data": data, "message": "success"})
    except Exception as e:
        return JsonResponse({"code": 500, "data": None, "message": str(e)})


def device_monitor(request):
    """设备监控页面"""
    return render(request, 'zapp/device_monitor.html')


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
def get_ip_records(request):
    """
    分页查询IP访问记录的API接口
    支持GET请求，参数：
    - page: 当前页码
    - page_size: 每页记录数
    """
    import sqlite3
    import os
    
    try:
        # 获取分页参数
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))
        
        # 验证参数
        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 10
        
        # 计算偏移量
        offset = (page - 1) * page_size
        
        # 数据库路径
        if os.name == 'nt':
            db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'accounting.db')
        else:
            db_path = '/var/codes/deploy/backend/backendCodes/the-go/accounting.db'
        
        # 连接数据库
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # 获取总记录数
            cursor.execute('SELECT COUNT(*) FROM ip_visit_records')
            total_count = cursor.fetchone()[0]
            
            # 获取分页记录
            cursor.execute(
                'SELECT id, visit_time, ip_address FROM ip_visit_records ORDER BY id DESC LIMIT ? OFFSET ?',
                (page_size, offset)
            )
            records = cursor.fetchall()
            
            # 格式化记录
            formatted_records = []
            for record in records:
                formatted_records.append({
                    'id': record[0],
                    'visit_time': record[1],
                    'ip_address': record[2]
                })
        
        # 计算总页数
        total_pages = (total_count + page_size - 1) // page_size
        
        # 返回响应
        return JsonResponse({
            "code": 200,
            "data": {
                "records": formatted_records,
                "total_count": total_count,
                "total_pages": total_pages,
                "current_page": page,
                "page_size": page_size
            },
            "message": "success"
        })
    except Exception as e:
        return JsonResponse({
            "code": 500,
            "data": None,
            "message": f"查询失败：{str(e)}"
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
        import traceback
        # 获取完整的异常堆栈信息
        full_error = traceback.format_exc()
        return JsonResponse({
            "code": 500,
            "data": {
                "error_type": type(e).__name__,
                "error_message": str(e),
                "stack_trace": full_error
            },
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

def used_codes_page(request):
    """
    渲染已使用股票代码列表页面
    :param request: HTTP请求对象
    :return: 已使用股票代码列表页面的HTML响应
    """
    return render(request, 'zapp/used_codes.html')

# WebRTC语音房间相关 - 从webrtc_service导入
from .webrtc_service import room_api

def voice_room(request):
    """
    渲染语音房间页面
    :param request: HTTP请求对象
    :return: 语音房间页面的HTML响应
    """
    return render(request, 'zapp/voice_room.html')


def stopwatch(request):
    """
    秒表功能页面
    """
    return render(request, 'zapp/stopwatch.html')


def ip_records(request):
    """
    IP访问记录查询页面
    """
    return render(request, 'zapp/ip_records.html')


def image_stitch(request):
    """
    图片拼接工具页面
    """
    return render(request, 'zapp/image_stitch.html')


def voice_recorder(request):
    """
    音频录音页面
    """
    return render(request, 'zapp/voice_recorder.html')


@csrf_exempt
@require_POST
def save_recording(request):
    """
    保存录音文件的API接口
    :param request: HTTP请求对象，包含录音文件
    :return: 保存结果的JSON响应
    """
    try:
        # 检查是否有录音文件
        if 'recording' not in request.FILES:
            return JsonResponse({
                "code": 400,
                "data": None,
                "message": "缺少录音文件"
            }, status=400)
        
        # 获取录音文件
        recording_file = request.FILES['recording']
        
        # 确保录音文件目录存在
        recordings_dir = os.path.join(settings.STATIC_ROOT, 'recordings')
        if not os.path.exists(recordings_dir):
            os.makedirs(recordings_dir, exist_ok=True)
        
        # 生成文件名（使用时间戳确保唯一性）
        timestamp = int(time.time())
        filename = f"recording_{timestamp}.webm"
        file_path = os.path.join(recordings_dir, filename)
        
        # 保存文件
        with open(file_path, 'wb') as f:
            for chunk in recording_file.chunks():
                f.write(chunk)
        
        # 构建文件URL，添加/apipy前缀
        file_url = f"/apipy/static/recordings/{filename}"
        
        return JsonResponse({
            "code": 200,
            "data": {
                "filename": filename,
                "file_url": file_url,
                "file_size": os.path.getsize(file_path)
            },
            "message": "success"
        })
    except Exception as e:
        return JsonResponse({
            "code": 500,
            "data": None,
            "message": f"保存录音失败：{str(e)}"
        }, status=500)


@require_GET
def get_recording_list(request):
    """
    获取录音文件列表的API接口
    :param request: HTTP请求对象
    :return: 录音文件列表的JSON响应
    """
    try:
        # 检查录音文件目录是否存在
        recordings_dir = os.path.join(settings.STATIC_ROOT, 'recordings')
        if not os.path.exists(recordings_dir):
            return JsonResponse({
                "code": 200,
                "data": {
                    "recordings": [],
                    "total_count": 0
                },
                "message": "success"
            })
        
        # 获取目录中的所有录音文件
        recording_files = []
        for filename in os.listdir(recordings_dir):
            if filename.endswith('.webm'):
                file_path = os.path.join(recordings_dir, filename)
                if os.path.isfile(file_path):
                    # 获取文件信息
                    file_size = os.path.getsize(file_path)
                    modified_time = os.path.getmtime(file_path)
                    
                    # 构建文件URL，添加/apipy前缀
                    file_url = f"/apipy/static/recordings/{filename}"
                    
                    # 格式化修改时间
                    modified_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(modified_time))
                    
                    # 计算文件大小（转换为MB或KB）
                    if file_size >= 1024 * 1024:
                        size_display = f"{file_size / (1024 * 1024):.2f} MB"
                    else:
                        size_display = f"{file_size / 1024:.2f} KB"
                    
                    # 添加到列表
                    recording_files.append({
                        "filename": filename,
                        "file_url": file_url,
                        "file_size": file_size,
                        "size_display": size_display,
                        "modified_date": modified_date
                    })
        
        # 按修改时间降序排序（最新的在前）
        recording_files.sort(key=lambda x: os.path.getmtime(os.path.join(recordings_dir, x['filename'])), reverse=True)
        
        return JsonResponse({
            "code": 200,
            "data": {
                "recordings": recording_files,
                "total_count": len(recording_files)
            },
            "message": "success"
        })
    except Exception as e:
        return JsonResponse({
            "code": 500,
            "data": None,
            "message": f"获取录音列表失败：{str(e)}"
        }, status=500)

@require_GET
def download_code_data(request):
    """
    下载指定股票代码的数据
    :param request: HTTP请求对象，包含code参数
    :return: 股票数据文件的HTTP响应
    """
    try:
        # 获取股票代码
        code = request.GET.get('code')
        if not code:
            return JsonResponse({
                "code": 400,
                "data": None,
                "message": "缺少code参数"
            }, status=400)
        
        # 获取股票数据
        code_data = stock_code_service.get_code_data(code)
        
        # 设置HTTP头，允许浏览器下载文件
        response = HttpResponse(code_data, content_type='text/plain; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename={code}.txt'
        response['Content-Length'] = len(code_data.encode('utf-8'))
        
        return response
    except FileNotFoundError as e:
        return JsonResponse({
            "code": 404,
            "data": None,
            "message": f"股票数据文件不存在：{str(e)}"
        }, status=404)
    except Exception as e:
        return JsonResponse({
            "code": 500,
            "data": None,
            "message": f"下载股票数据失败：{str(e)}"
        }, status=500)

@require_GET
def download_all_code_data(request):
    """
    全量下载所有已使用的股票代码数据，采用临时文件和流式传输，最小化内存占用
    :param request: HTTP请求对象
    :return: 压缩后的股票数据文件的流式HTTP响应
    """
    from django.http import StreamingHttpResponse
    import zipfile
    import tempfile
    import os
    import time
    from datetime import datetime
    import logging
    
    # 获取日志记录器
    logger = logging.getLogger(__name__)
    start_time = time.time()
    
    try:
        logger.info(f"Start generating zip file for download_all_code_data")
        
        # 生成下载文件名，包含当前日期
        current_date = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'all_stock_codes_{current_date}.zip'
        
        # 创建临时文件，使用指定的临时目录，确保有写入权限
        temp_dir = tempfile.gettempdir()
        logger.info(f"Using temp directory: {temp_dir}")
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip', dir=temp_dir) as temp_zip_file:
            temp_zip_path = temp_zip_file.name
        
        logger.info(f"Created temp zip file: {temp_zip_path}")
        
        # 获取所有已使用的代码信息
        used_codes = stock_code_service.get_used_codes_from_files()
        logger.info(f"Found {len(used_codes)} used codes")
        
        # 创建ZipFile对象，使用临时文件而不是内存缓冲区，使用更快的压缩算法
        with zipfile.ZipFile(temp_zip_path, 'w', zipfile.ZIP_STORED, allowZip64=True) as zip_file:
            # 遍历所有已使用的代码，逐个添加到压缩包
            for i, code_info in enumerate(used_codes):
                code = code_info['code']
                
                try:
                    # 直接将文件添加到压缩包，不读取到内存中
                    file_path = os.path.join(stock_code_service.data_dir, f'{code}.txt')
                    zip_file.write(file_path, arcname=f'{code}.txt')
                    
                    # 每处理100个文件记录一次日志
                    if (i + 1) % 100 == 0:
                        logger.info(f"Processed {i + 1}/{len(used_codes)} files")
                except Exception as e:
                    logger.error(f"Failed to add {code}.txt to zip: {str(e)}")
                    continue
        
        # 获取临时文件大小
        file_size = os.path.getsize(temp_zip_path)
        logger.info(f"Generated zip file size: {file_size} bytes")
        
        # 定义分块读取生成器，使用更大的chunk size提高传输速度
        def file_chunks(file_path, chunk_size=65536):  # 64KB chunk size
            with open(file_path, 'rb') as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    yield chunk
        
        # 创建一个自定义的StreamingHttpResponse子类，用于清理临时文件
        class CleanupStreamingHttpResponse(StreamingHttpResponse):
            def __init__(self, *args, temp_file_path=None, **kwargs):
                super().__init__(*args, **kwargs)
                self.temp_file_path = temp_file_path
            
            def close(self):
                super().close()
                # 清理临时文件
                if self.temp_file_path and os.path.exists(self.temp_file_path):
                    try:
                        os.remove(self.temp_file_path)
                        logger.info(f"Cleaned up temp file: {self.temp_file_path}")
                    except Exception as e:
                        logger.error(f"Failed to delete temp file {self.temp_file_path}: {str(e)}")
        
        # 创建自定义StreamingHttpResponse对象，使用生成器进行流式传输
        response = CleanupStreamingHttpResponse(
            file_chunks(temp_zip_path), 
            content_type='application/zip',
            temp_file_path=temp_zip_path
        )
        
        # 设置HTTP头，允许浏览器下载文件
        response['Content-Disposition'] = f'attachment; filename={filename}'
        response['Content-Length'] = file_size
        response['X-File-Count'] = str(len(used_codes))
        response['X-File-Size'] = str(file_size)
        
        # 添加超时头，防止代理服务器过早关闭连接
        response['X-Accel-Buffering'] = 'no'  # 禁用Nginx缓冲
        
        logger.info(f"Generated response in {time.time() - start_time:.2f} seconds")
        
        return response
    except Exception as e:
        logger.exception(f"Failed to create zip file: {str(e)}")
        # 清理临时文件
        if 'temp_zip_path' in locals() and os.path.exists(temp_zip_path):
            try:
                os.remove(temp_zip_path)
                logger.info(f"Cleaned up temp file after error: {temp_zip_path}")
            except Exception:
                pass
        return JsonResponse({
            "code": 500,
            "data": {
                "error_type": type(e).__name__,
                "error_message": str(e),
                "processing_time": time.time() - start_time
            },
            "message": f"生成压缩文件失败：{str(e)}"
        }, status=500)

@require_GET
def getUsedCodeList(request):
    """
    获取已使用的股票代码列表，返回totalCount和代码列表
    直接从data文件夹读取，确保数据真实可靠
    :param request: HTTP请求对象
    :return: 包含totalCount和代码列表的JSON响应
    """
    try:
        # 直接从文件系统获取已使用的代码信息
        used_codes_from_files = stock_code_service.get_used_codes_from_files()
        
        # 提取代码列表
        code_list = [code_info['code'] for code_info in used_codes_from_files]
        total_count = len(code_list)
        
        # 从数据库获取已使用的代码数量，用于比较
        db_used_count = stock_code_service.get_used_code_count_from_db()
        file_used_count = total_count
        
        # 描述数据库和文件系统之间的差异
        if db_used_count == file_used_count:
            status_desc = f"数据库记录与实际文件数量一致，均为{db_used_count}个"
        else:
            status_desc = f"数据库记录({db_used_count}个)与实际文件数量({file_used_count}个)不一致，以实际文件为准"
        
        return JsonResponse({
            "code": 200,
            "data": {
                "totalCount": total_count,
                "list": code_list,
                "statusDesc": status_desc
            },
            "message": "success"
        })
    except Exception as e:
        return JsonResponse({
            "code": 500,
            "data": None,
            "message": f"获取已使用代码列表失败：{str(e)}"
        }, status=500)


@csrf_exempt
@require_POST
def clear_all_code_data(request):
    """
    移除data目录下的所有文件，并重置数据库中股票代码的使用状态
    :param request: HTTP请求对象
    :return: 操作结果的JSON响应
    """
    try:
        # 获取清理前的文件数量
        used_codes_before = stock_code_service.get_used_codes_from_files()
        files_count_before = len(used_codes_before)
        
        # 从数据库获取清理前的已使用代码数量
        db_used_count_before = stock_code_service.get_used_code_count_from_db()
        
        # 执行清理操作
        affected_rows = stock_code_service.reset_code_usage()
        
        # 获取清理后的文件数量
        used_codes_after = stock_code_service.get_used_codes_from_files()
        files_count_after = len(used_codes_after)
        
        # 从数据库获取清理后的已使用代码数量
        db_used_count_after = stock_code_service.get_used_code_count_from_db()
        
        # 计算清理的文件数量
        deleted_files_count = files_count_before - files_count_after
        
        return JsonResponse({
            "code": 200,
            "data": {
                "deletedFilesCount": deleted_files_count,
                "affectedRows": affected_rows,
                "dbUsedCountBefore": db_used_count_before,
                "dbUsedCountAfter": db_used_count_after,
                "filesCountBefore": files_count_before,
                "filesCountAfter": files_count_after,
                "status": "success"
            },
            "message": f"成功清理了{deleted_files_count}个文件，重置了{affected_rows}条数据库记录"
        })
    except Exception as e:
        return JsonResponse({
            "code": 500,
            "data": None,
            "message": f"清理数据失败：{str(e)}"
        }, status=500)


# 认证相关视图
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import UserProfile, Medication, MedicationSchedule

@csrf_exempt
@require_POST
def register(request):
    """
    用户注册接口
    :param request: HTTP请求对象
    :return: 注册结果的JSON响应
    """
    try:
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        nickname = request.POST.get('nickname', '')
        
        # 验证参数
        if not username or not password:
            return JsonResponse({"code": 400, "data": None, "message": "账号和密码不能为空"}, status=400)
        
        if len(username) < 3 or len(username) > 150:
            return JsonResponse({"code": 400, "data": None, "message": "账号长度应在3-150字符之间"}, status=400)
        
        if len(password) < 6 or len(password) > 128:
            return JsonResponse({"code": 400, "data": None, "message": "密码长度应在6-128字符之间"}, status=400)
        
        # 检查账号是否已存在
        if User.objects.filter(username=username).exists():
            return JsonResponse({"code": 400, "data": None, "message": "账号已存在"}, status=400)
        
        # 检查邮箱是否已存在
        if email and User.objects.filter(email=email).exists():
            return JsonResponse({"code": 400, "data": None, "message": "邮箱已存在"}, status=400)
        
        # 检查手机号是否已存在
        if phone and UserProfile.objects.filter(phone=phone).exists():
            return JsonResponse({"code": 400, "data": None, "message": "手机号已存在"}, status=400)
        
        # 创建用户
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email
        )
        
        # 创建用户扩展信息
        UserProfile.objects.create(
            user=user,
            phone=phone,
            nickname=nickname
        )
        
        return JsonResponse({"code": 200, "data": {"user_id": user.id, "username": user.username}, "message": "success"})
    except Exception as e:
        return JsonResponse({"code": 500, "data": None, "message": f"注册失败：{str(e)}"}, status=500)


@csrf_exempt
@require_POST
def user_login(request):
    """
    用户登录接口
    :param request: HTTP请求对象
    :return: 登录结果的JSON响应
    """
    try:
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # 验证参数
        if not username or not password:
            return JsonResponse({"code": 400, "data": None, "message": "账号和密码不能为空"}, status=400)
        
        # 验证用户
        user = authenticate(request, username=username, password=password)
        if not user:
            return JsonResponse({"code": 401, "data": None, "message": "账号或密码错误"}, status=401)
        
        # 登录用户
        login(request, user)
        
        return JsonResponse({"code": 200, "data": {"user_id": user.id, "username": user.username}, "message": "success"})
    except Exception as e:
        return JsonResponse({"code": 500, "data": None, "message": f"登录失败：{str(e)}"}, status=500)


@csrf_exempt
@require_POST
def user_logout(request):
    """
    用户登出接口
    :param request: HTTP请求对象
    :return: 登出结果的JSON响应
    """
    try:
        logout(request)
        return JsonResponse({"code": 200, "data": None, "message": "success"})
    except Exception as e:
        return JsonResponse({"code": 500, "data": None, "message": f"登出失败：{str(e)}"}, status=500)


@require_GET
def userinfo(request):
    """
    获取用户信息接口
    :param request: HTTP请求对象
    :return: 用户信息的JSON响应
    """
    try:
        if not request.user.is_authenticated:
            return JsonResponse({"code": 401, "data": None, "message": "未登录"}, status=401)
        
        user = request.user
        try:
            profile = user.profile
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=user)
        
        user_info = {
            "user_id": user.id,
            "username": user.username,
            "email": user.email or "",
            "phone": profile.phone or "",
            "nickname": profile.nickname or ""
        }
        
        return JsonResponse({"code": 200, "data": user_info, "message": "success"})
    except Exception as e:
        return JsonResponse({"code": 500, "data": None, "message": f"获取用户信息失败：{str(e)}"}, status=500)


@csrf_exempt
@require_POST
def update_userinfo(request):
    """
    更新用户信息接口
    :param request: HTTP请求对象
    :return: 更新结果的JSON响应
    """
    try:
        if not request.user.is_authenticated:
            return JsonResponse({"code": 401, "data": None, "message": "未登录"}, status=401)
        
        user = request.user
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        nickname = request.POST.get('nickname')
        
        # 检查邮箱是否已存在
        if email and email != user.email and User.objects.filter(email=email).exists():
            return JsonResponse({"code": 400, "data": None, "message": "邮箱已存在"}, status=400)
        
        # 检查手机号是否已存在
        try:
            profile = user.profile
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=user)
        
        if phone and phone != profile.phone and UserProfile.objects.filter(phone=phone).exists():
            return JsonResponse({"code": 400, "data": None, "message": "手机号已存在"}, status=400)
        
        # 更新用户信息
        if email is not None:
            user.email = email
            user.save()
        
        if phone is not None:
            profile.phone = phone
        if nickname is not None:
            profile.nickname = nickname
        profile.save()
        
        user_info = {
            "user_id": user.id,
            "username": user.username,
            "email": user.email or "",
            "phone": profile.phone or "",
            "nickname": profile.nickname or ""
        }
        
        return JsonResponse({"code": 200, "data": user_info, "message": "success"})
    except Exception as e:
        return JsonResponse({"code": 500, "data": None, "message": f"更新用户信息失败：{str(e)}"}, status=500)


@csrf_exempt
@require_POST
def change_password(request):
    """
    修改密码接口
    :param request: HTTP请求对象
    :return: 修改结果的JSON响应
    """
    try:
        if not request.user.is_authenticated:
            return JsonResponse({"code": 401, "data": None, "message": "未登录"}, status=401)
        
        user = request.user
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        
        # 验证参数
        if not old_password or not new_password:
            return JsonResponse({"code": 400, "data": None, "message": "旧密码和新密码不能为空"}, status=400)
        
        if len(new_password) < 6 or len(new_password) > 128:
            return JsonResponse({"code": 400, "data": None, "message": "新密码长度应在6-128字符之间"}, status=400)
        
        # 验证旧密码
        if not user.check_password(old_password):
            return JsonResponse({"code": 400, "data": None, "message": "旧密码错误"}, status=400)
        
        # 修改密码
        user.set_password(new_password)
        user.save()
        
        return JsonResponse({"code": 200, "data": None, "message": "success"})
    except Exception as e:
        return JsonResponse({"code": 500, "data": None, "message": f"修改密码失败：{str(e)}"}, status=500)


# Medication related imports
import json
from .services.medication_service import medication_service
from datetime import datetime, timedelta
from django.utils import timezone

def _get_medication_user_id(request):
    """Helper to get user ID from request (Auth user or Guest header)"""
    if request.user.is_authenticated:
        return str(request.user.id)
    return request.headers.get('X-Guest-ID')

def medication_tracker(request):
    """用药提醒页面"""
    return render(request, 'zapp/medication_tracker.html')

@csrf_exempt
@require_POST
def api_save_medication(request):
    """保存药品信息（新增或修改）"""
    try:
        user_id = _get_medication_user_id(request)
        if not user_id:
            return JsonResponse({'code': 401, 'message': 'Unauthorized'}, status=401)
            
        data = json.loads(request.body) if request.body else request.POST
        medication_id = data.get('id')
        
        # 简单校验
        if not data.get('name'):
             return JsonResponse({'code': 400, 'message': 'Name is required'}, status=400)

        if medication_id:
            # Update
            medication_service.update_medication(user_id, medication_id, data)
            new_id = medication_id
        else:
            # Create
            new_id = medication_service.create_medication(user_id, data)
            
        return JsonResponse({'code': 200, 'data': {'id': new_id}, 'message': 'success'})
    except Exception as e:
        return JsonResponse({'code': 500, 'message': str(e)}, status=500)

@require_GET
def api_get_medications(request):
    """获取用户所有药品"""
    try:
        user_id = _get_medication_user_id(request)
        if not user_id:
            return JsonResponse({'code': 401, 'message': 'Unauthorized'}, status=401)

        medications = medication_service.get_user_medications(user_id)
        return JsonResponse({'code': 200, 'data': medications, 'message': 'success'})
    except Exception as e:
        return JsonResponse({'code': 500, 'message': str(e)}, status=500)

@csrf_exempt
@require_POST
def api_delete_medication(request):
    """删除药品"""
    try:
        user_id = _get_medication_user_id(request)
        if not user_id:
            return JsonResponse({'code': 401, 'message': 'Unauthorized'}, status=401)

        data = json.loads(request.body) if request.body else request.POST
        medication_id = data.get('id')
        medication_service.delete_medication(user_id, medication_id)
        return JsonResponse({'code': 200, 'message': 'success'})
    except Exception as e:
        return JsonResponse({'code': 500, 'message': str(e)}, status=500)

@csrf_exempt
@require_POST
def api_save_schedule(request):
    """保存服药计划"""
    try:
        user_id = _get_medication_user_id(request)
        if not user_id:
            return JsonResponse({'code': 401, 'message': 'Unauthorized'}, status=401)

        data = json.loads(request.body) if request.body else request.POST
        medication_service.create_schedule(user_id, data)
        return JsonResponse({'code': 200, 'message': 'success'})
    except Exception as e:
        return JsonResponse({'code': 500, 'message': str(e)}, status=500)

@csrf_exempt
@require_POST
def api_delete_schedule(request):
    """删除服药计划"""
    try:
        user_id = _get_medication_user_id(request)
        if not user_id:
            return JsonResponse({'code': 401, 'message': 'Unauthorized'}, status=401)

        data = json.loads(request.body) if request.body else request.POST
        schedule_id = data.get('id')
        medication_service.delete_schedule(user_id, schedule_id)
        return JsonResponse({'code': 200, 'message': 'success'})
    except Exception as e:
        return JsonResponse({'code': 500, 'message': str(e)}, status=500)

@require_GET
def api_get_daily_schedule(request):
    """获取每日服药计划"""
    try:
        user_id = _get_medication_user_id(request)
        if not user_id:
            return JsonResponse({'code': 401, 'message': 'Unauthorized'}, status=401)

        date_str = request.GET.get('date')
        if date_str:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            date_obj = timezone.now().date()
            
        schedules = medication_service.get_daily_schedule(user_id, date_obj)
        return JsonResponse({'code': 200, 'data': schedules, 'message': 'success'})
    except Exception as e:
        return JsonResponse({'code': 500, 'message': str(e)}, status=500)

@csrf_exempt
@require_POST
def api_mark_taken(request):
    """打卡"""
    try:
        user_id = _get_medication_user_id(request)
        if not user_id:
            return JsonResponse({'code': 401, 'message': 'Unauthorized'}, status=401)

        data = json.loads(request.body) if request.body else request.POST
        schedule_id = data.get('schedule_id')
        date_str = data.get('date')
        
        result = medication_service.mark_taken(schedule_id, date_str)
        if result['success']:
            return JsonResponse({'code': 200, 'data': result, 'message': 'success'})
        else:
            return JsonResponse({'code': 400, 'message': result.get('message', 'Failed')}, status=400)
    except Exception as e:
        return JsonResponse({'code': 500, 'message': str(e)}, status=500)

@csrf_exempt
@require_POST
def api_undo_taken(request):
    """撤销打卡"""
    try:
        user_id = _get_medication_user_id(request)
        if not user_id:
            return JsonResponse({'code': 401, 'message': 'Unauthorized'}, status=401)

        data = json.loads(request.body) if request.body else request.POST
        schedule_id = data.get('schedule_id')
        date_str = data.get('date')
        
        result = medication_service.undo_taken(schedule_id, date_str)
        if result['success']:
            return JsonResponse({'code': 200, 'data': result, 'message': 'success'})
        else:
            return JsonResponse({'code': 400, 'message': result.get('message', 'Failed')}, status=400)
    except Exception as e:
        return JsonResponse({'code': 500, 'message': str(e)}, status=500)

@require_GET
def api_get_weekly_report(request):
    """获取周报表"""
    try:
        user_id = _get_medication_user_id(request)
        if not user_id:
            return JsonResponse({'code': 401, 'message': 'Unauthorized'}, status=401)

        start_date_str = request.GET.get('start_date')
        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        else:
            # 默认取本周一
            today = timezone.now().date()
            start_date = today - timedelta(days=today.weekday())
            
        report = medication_service.get_weekly_report(user_id, start_date)
        return JsonResponse({'code': 200, 'data': report, 'message': 'success'})
    except Exception as e:
        return JsonResponse({'code': 500, 'message': str(e)}, status=500)
