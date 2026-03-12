# zapp/urls.py
from django.urls import path
from . import views  # 导入应用的视图

# 定义应用的HTTP路由（暂时只需要一个空的路由列表，后续再添加视图）
urlpatterns = [
    # 后续添加的路由会放在这里，比如之前计划的 chat 页面路由
    path('chat/', views.chat_page, name='chat_page'),
    path('api/timestamp/', views.timestamp_api, name='timestamp_api'),
    path('api/getAllCodes/', views.get_all_codes, name='get_all_codes'),
    path('api/fetch_stock/', views.fetch_stock, name='fetch_stock'),
    # IP采集接口
    path('api/pythongetip/', views.pythongetip, name='pythongetip'),
    # IP记录查询接口
    path('api/get_ip_records/', views.get_ip_records, name='get_ip_records'),
    # 备忘录接口
    path('api/memos/', views.get_all_memos, name='get_all_memos'),
    path('api/memos/add/', views.add_memo, name='add_memo'),
    path('api/memos/delete/', views.delete_memo, name='delete_memo'),
    path('api/memos/search/', views.search_memos, name='search_memos'),
    path('index', views.index, name='index'),
    path('index/', views.index_with_slash, name='index_with_slash'),
    path('notebook', views.notebook, name='notebook'),
    # 锻炼计时器页面
    path('duanlian', views.duanlian, name='duanlian'),
    # 时间戳转换页面
    path('timestamp', views.timestamp, name='timestamp'),
    # 秒表功能页面
    path('stopwatch', views.stopwatch, name='stopwatch'),
    # IP访问记录页面
    path('ip_records', views.ip_records, name='ip_records'),
    # 图片拼接工具页面
    path('image_stitch', views.image_stitch, name='image_stitch'),
    # 静态文件访问接口
    path('static/<path:file_path>', views.static_file_access, name='static_file_access'),
    # 股票代码管理API
    path('api/noUseCode/', views.noUseCode, name='noUseCode'),
    path('api/addTodayCode/', views.addTodayCode, name='addTodayCode'),
    path('api/getCodeInfo/', views.getCodeInfo, name='getCodeInfo'),
    path('api/getAllUsedCodes/', views.getAllUsedCodes, name='getAllUsedCodes'),
    path('api/getUsedCodeList/', views.getUsedCodeList, name='getUsedCodeList'),
    path('api/downloadCodeData/', views.download_code_data, name='download_code_data'),
    path('api/downloadAllCodeData/', views.download_all_code_data, name='download_all_code_data'),
    path('api/clearAllCodeData/', views.clear_all_code_data, name='clear_all_code_data'),
    path('usedcodes', views.used_codes_page, name='used_codes_page'),
    # WebRTC语音房间相关路由
    path('voice-room', views.voice_room, name='voice_room'),
    path('api/room/', views.room_api, name='room_api'),
    # 录音功能相关路由
    path('voice_recorder', views.voice_recorder, name='voice_recorder'),
    path('api/save_recording/', views.save_recording, name='save_recording'),
    path('api/recording_list/', views.get_recording_list, name='get_recording_list'),
    # Medication Reminder
    path('medication_tracker', views.medication_tracker, name='medication_tracker'),
    path('api/medication/list/', views.api_get_medications, name='api_get_medications'),
    path('api/medication/save/', views.api_save_medication, name='api_save_medication'),
    path('api/medication/delete/', views.api_delete_medication, name='api_delete_medication'),
    path('api/medication/schedule/save/', views.api_save_schedule, name='api_save_schedule'),
    path('api/medication/schedule/delete/', views.api_delete_schedule, name='api_delete_schedule'),
    path('api/medication/schedule/daily/', views.api_get_daily_schedule, name='api_get_daily_schedule'),
    path('api/medication/record/mark/', views.api_mark_taken, name='api_mark_taken'),
    path('api/medication/record/undo/', views.api_undo_taken, name='api_undo_taken'),
    path('api/medication/stats/weekly/', views.api_get_weekly_report, name='api_get_weekly_report'),
    # 认证相关路由
    path('auth/register', views.register, name='register'),
    path('auth/login', views.user_login, name='login'),
    path('auth/logout', views.user_logout, name='logout'),
    path('auth/userinfo', views.userinfo, name='userinfo'),
    path('auth/update', views.update_userinfo, name='update_userinfo'),
    path('auth/changepassword', views.change_password, name='change_password'),
    # 设备心跳监控
    path('api/heartbeat/', views.heartbeat_api, name='heartbeat_api'),
    path('api/devices/', views.get_devices_api, name='get_devices_api'),
    path('device_monitor', views.device_monitor, name='device_monitor'),
    path('heartbeat_docs', views.heartbeat_docs, name='heartbeat_docs'),
]