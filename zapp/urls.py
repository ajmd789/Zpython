# zapp/urls.py
from django.urls import path
from . import views  # 导入应用的视图

# 定义应用的HTTP路由（暂时只需要一个空的路由列表，后续再添加视图）
urlpatterns = [
    # 后续添加的路由会放在这里，比如之前计划的 chat 页面路由
    path('chat/', views.chat_page, name='chat_page'),
    path('api/timestamp/', views.timestamp_api, name='timestamp_api'),
    path('getAllCodes/', views.get_all_codes, name='get_all_codes'),
    path('api/fetch_stock/', views.fetch_stock, name='fetch_stock'),
    path('index/', views.index, name='index'),
]