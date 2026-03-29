# 设计文档 (Design)

## 架构选型
- **后端框架**: Django (Zpython)
- **数据库**: 原生 SQLite (`sqlite3` 库)，连接文件为 `accounting.db`。自动建表 `bookmarks`。
- **前端页面**: 基于原生 HTML/JS (可以借用 Bootstrap 类似类或者简单 CSS 实现 5列网格)，存放在 `zapp/templates/zapp/bookmarks.html`。
- **API 路径**: 遵循前缀规范 `/apipy/api/bookmarks/`。

## 数据库设计
**表名**: `bookmarks`
- `id`: INTEGER PRIMARY KEY AUTOINCREMENT
- `url`: TEXT NOT NULL
- `title`: TEXT NOT NULL
- `created_at`: DATETIME DEFAULT CURRENT_TIMESTAMP
- `updated_at`: DATETIME DEFAULT CURRENT_TIMESTAMP

## API 设计
所有的 API 返回格式为: `{"code": 200, "data": ..., "message": "..."}`。

### GET /apipy/api/bookmarks/
- 获取所有的书签列表。
- 响应:
  ```json
  {
      "code": 200,
      "data": [{"id": 1, "url": "https://...", "title": "...", "created_at": "..."}],
      "message": "success"
  }
  ```

### POST /apipy/api/bookmarks/
- 增加一个书签。如果 `title` 未提供，服务端抓取对应 URL 的网页 `<title>`。
- Body (JSON): `{"url": "...", "title": "..."}`
- 响应: `{"code": 200, "data": {"id": 2, ...}, "message": "created"}`

### PUT /apipy/api/bookmarks/
- 修改书签。
- Body (JSON): `{"id": 1, "url": "...", "title": "..."}`
- 响应: `{"code": 200, "data": null, "message": "updated"}`

### DELETE /apipy/api/bookmarks/
- 删除书签。
- Body (JSON): `{"id": 1}`
- 响应: `{"code": 200, "data": null, "message": "deleted"}`

## 页面逻辑
1. `localStorage` 键值: `bookmarkCache`
2. 初始化时，先读取 `localStorage.getItem('bookmarkCache')`，如果有则渲染。
3. 同时使用 `fetch` 访问 `GET /apipy/api/bookmarks/`。拿到数据后，对比或直接覆盖 `localStorage`，然后重新渲染列表。
4. 渲染时使用 CSS Flexbox 或 Grid 实现 `grid-template-columns: repeat(5, 1fr)` 保证每行最多 5 个。
5. 列表末尾固定一个带有加号 (`+`) 的块，点击弹出模态框（或者输入框）录入 URL 和 Title。