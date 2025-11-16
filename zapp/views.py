from django.shortcuts import render

def chat_page(request):
    return render(request, 'zapp/chat.html')  # 渲染测试页面