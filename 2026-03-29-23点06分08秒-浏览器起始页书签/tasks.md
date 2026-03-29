# 任务分解 (Tasks)

1. [x] 初始化项目结构，建立需求归档文件夹，写入 `requirements.md`, `design.md`, `tasks.md`。
2. [x] 在 `zapp/services/` 中新建 `bookmark_service.py`：
   - 包含连接 `accounting.db` 并建表的代码 (原生 sqlite3)。
   - 提供增删改查方法。
   - 实现提取网页 title 的方法 (使用 requests 和正则表达式)。
3. [x] 在 `zapp/views.py` 中新增：
   - `bookmarks_page(request)` 渲染页面模板。
   - `bookmarks_api(request)` 提供 CRUD REST 接口，标记 `@csrf_exempt` 并处理 GET/POST/PUT/DELETE 请求。
4. [x] 在 `zapp/urls.py` 中增加路由：
   - `path('bookmarks', views.bookmarks_page, name='bookmarks_page')`
   - `path('api/bookmarks/', views.bookmarks_api, name='bookmarks_api')`
5. [x] 新增模板 `zapp/templates/zapp/bookmarks.html`：
   - 编写 HTML/CSS (Grid 或 Flex 布局) 实现每行最多 5 个。
   - 实现加号按钮和模态框逻辑。
   - 编写 localStorage 缓存和请求最新 API 的渲染逻辑。
   - 实现增删改查的 fetch 调用逻辑。
6. [x] 验证所有功能点是否符合预期并符合 R35-R38 规范要求。