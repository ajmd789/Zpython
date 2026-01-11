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
    # 静态文件访问接口
    path('static/<path:file_path>', views.static_file_access, name='static_file_access'),
    # 股票代码管理API
    path('api/noUseCode/', views.noUseCode, name='noUseCode'),
    path('api/addTodayCode/', views.addTodayCode, name='addTodayCode'),
    path('api/getCodeInfo/', views.getCodeInfo, name='getCodeInfo'),
    path('api/getAllUsedCodes/', views.getAllUsedCodes, name='getAllUsedCodes'),
    path('api/getUsedCodeList/', views.getUsedCodeList, name='getUsedCodeList'),
    path('api/downloadCodeData/', views.download_code_data, name='download_code_data'),
    path('usedcodes', views.used_codes_page, name='used_codes_page'),
]