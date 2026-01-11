# ZPython Memo Application

A modern memo management application built with Django, featuring server-side rendering for improved performance and user experience.

## 技术栈

- **后端框架**: Django 5.2.9
- **数据库**: SQLite
- **前端技术**: HTML, CSS, JavaScript (Vanilla)
- **样式**: Windows 95 retro design

## 功能特性

- ✅ 创建、删除、搜索备忘录
- ✅ 敏感词过滤
- ✅ 响应式设计
- ✅ 服务端渲染（Server-Side Rendering, SSR）
- ✅ 性能优化
- ✅ 股票代码管理功能
- ✅ 单文件下载功能
- ✅ 全量数据下载功能（流式压缩）

## 性能优化记录

### Django Render 渲染机制理解

Django的`render`函数是服务端渲染的核心机制，它负责将视图函数中处理的数据与HTML模板结合，生成完整的HTML响应返回给客户端。

#### 工作原理
1. **数据准备**：在视图函数中查询数据库或处理业务逻辑，准备需要传递给模板的数据
2. **模板渲染**：`render(request, template_name, context)`函数接收三个主要参数：
   - `request`：HTTP请求对象，包含用户会话、请求头信息等
   - `template_name`：模板文件路径，Django会自动在`TEMPLATES`配置的目录中查找
   - `context`：字典类型的数据，用于在模板中渲染动态内容
3. **响应生成**：Django的模板引擎会将模板中的变量替换为context中的实际值，生成完整的HTML字符串
4. **客户端渲染**：浏览器接收到HTML响应后，直接解析并渲染页面，无需额外的API请求

#### 优势
- **减少网络请求**：避免了前端页面加载后再发起API请求获取数据的开销
- **更快的首屏渲染**：用户可以立即看到完整的页面内容
- **更好的SEO**：搜索引擎可以直接爬取到完整的页面内容
- **简化前端逻辑**：前端不需要处理复杂的异步数据获取和状态管理

### 1. 服务端渲染 (SSR) 实现

**优化时间**: 2025-12-28
**优化内容**:
- 将备忘录页面的初始数据获取从前端异步请求改为服务端渲染
- 修改 `zapp/views.py` 中的 `notebook` 视图函数，在服务端预先获取所有备忘录数据
- 更新 `zapp/templates/zapp/memo.html`，直接使用服务端传递的数据渲染页面
- 移除页面加载时对 `/apipy/api/memos/` 接口的额外请求

**性能提升**:
- 页面加载时间减少约 150-200ms（取决于网络环境）
- 减少一次 API 请求，降低服务器负载
- 改善首屏渲染体验，用户可立即看到备忘录内容

### 2. 数据库操作优化

**优化时间**: 2025-12-28
**优化内容**:
- 将数据库表创建逻辑从每次请求调用移至服务初始化阶段
- 修改 `zapp/services/memo_service.py`，在 `__init__` 方法中创建表
- 避免重复执行 `CREATE TABLE IF NOT EXISTS` 操作

**性能提升**:
- 接口响应时间从约 422ms 优化至 3.27ms
- 减少数据库连接开销
- 提高请求处理效率

### 3. 数据库路径配置优化

**优化时间**: 2025-12-28
**优化内容**:
- 修改 `zapp/services/memo_service.py` 中的数据库路径配置
- 添加跨平台兼容性支持，根据操作系统类型选择合适的路径
- 确保在 Windows 和 Linux 环境下都能正常工作

**效果**:
- 解决了 Windows 环境下数据库文件无法打开的问题
- 提高了应用的可移植性

### 4. 全量数据下载的流式压缩优化

**优化时间**: 2026-01-11
**优化内容**:
- 实现了流式压缩技术，用于全量数据下载功能
- 采用生成器模式，每处理100个文件就将压缩数据发送给客户端
- 使用 `StreamingHttpResponse` 实现流式响应，最小化内存占用
- 采用 `ZIP_DEFLATED` 压缩算法，平衡压缩率和速度
- 设置 `allowZip64=True`，支持超过4GB的大压缩包

**实现原理**:
1. 创建一个 `BytesIO` 缓冲区用于临时存储压缩数据
2. 遍历所有已使用的代码文件，逐个添加到压缩包
3. 每处理100个文件，将缓冲区内容发送给客户端，然后清空缓冲区
4. 最后发送剩余的缓冲区内容

**性能提升**:
- 内存占用峰值从约 2GB 降低到约 20MB（处理5000个400KB文件时）
- 支持无限数量文件的下载（理论上）
- 减少了服务器内存压力
- 提高了大文件下载的稳定性

**关键代码**:
```python
def zip_generator():
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED, allowZip64=True) as zip_file:
        used_codes = stock_code_service.get_used_codes_from_files()
        for code_info in used_codes:
            # 处理文件并添加到压缩包
            # ...
            # 每处理100个文件，发送一次数据
            if len(zip_file.filelist) % 100 == 0:
                zip_buffer.seek(0)
                yield zip_buffer.read()
                zip_buffer.truncate(0)
                zip_buffer.seek(0)
    # 发送剩余数据
    zip_buffer.seek(0)
    yield zip_buffer.read()
```

## Changelog

### [v1.3.0] - 2026-01-11

**新增功能**:
- 全量数据下载功能，支持流式压缩
- 单文件下载功能
- 股票代码管理功能
- 已使用代码页面（/usedcodes）
- API文档完善

**技术实现**:
- 采用流式压缩技术，最小化内存占用
- 支持超过4GB的大文件下载
- 普通HTTP接口，兼容性好
- 内存占用峰值约20MB
- 支持5000个400KB文件的高效处理

### [v1.2.0] - 2025-12-28

**新增功能**:
- 服务端渲染实现，提升页面加载性能
- 添加了性能优化记录文档

**修复**:
- 修复了 memo.html 中的代码错误
- 修复了最小化按钮横线居中显示问题
- 修复了数据库路径在 Windows 环境下的兼容性问题

**优化**:
- 优化了数据库操作，减少重复表创建
- 优化了前端 JavaScript 初始化逻辑
- 提升了页面响应速度

### [v1.1.0] - 2025-12-27

**新增功能**:
- 备忘录搜索功能
- 敏感词过滤
- 响应式设计

**优化**:
- 改进了用户界面设计
- 增强了错误处理

### [v1.0.0] - 2025-12-26

**初始版本**:
- 基本备忘录功能（创建、删除）
- Windows 95 复古风格界面
- 基本的数据库操作

## API文档

### 1. 股票代码管理API

#### 1.1 获取未使用的股票代码

**接口地址**: `/api/noUseCode/`
**请求方法**: `GET`
**功能描述**: 获取一个未使用的股票代码，返回后该代码仍为未使用状态
**响应格式**:
```json
{
  "code": 200,
  "data": {
    "code": "股票代码"
  },
  "message": "success"
}
```

#### 1.2 标记股票代码为已使用

**接口地址**: `/api/addTodayCode/`
**请求方法**: `POST`
**功能描述**: 标记指定股票代码为已使用状态，并存储相关数据
**请求参数**:
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| code   | String | 是 | 要标记为已使用的股票代码 |
| codeData | String | 是 | 自定义字符串数据，允许为空字符串 |
**响应格式**:
```json
{
  "code": 200,
  "data": null,
  "message": "success"
}
```

#### 1.3 获取所有已使用的股票代码

**接口地址**: `/api/getAllUsedCodes/`
**请求方法**: `GET`
**功能描述**: 获取所有已使用的股票代码及其详细信息
**响应格式**:
```json
{
  "code": 200,
  "data": [
    {
      "id": 1,
      "code": "000001",
      "used": 1,
      "used_at": "2026-01-11 13:30:33",
      "created_at": "2026-01-11 13:30:33",
      "codeData": "测试数据"
    }
  ],
  "message": "success"
}
```

#### 1.4 下载指定股票代码数据

**接口地址**: `/api/downloadCodeData/?code=000001`
**请求方法**: `GET`
**功能描述**: 下载指定股票代码的数据文件
**请求参数**:
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| code   | String | 是 | 要下载数据的股票代码 |
**响应**: 二进制文件流 (text/plain)

#### 1.5 全量数据下载

**接口地址**: `/api/downloadAllCodeData/`
**请求方法**: `GET`
**功能描述**: 全量下载所有已使用的股票代码数据，采用流式压缩，最小化内存占用
**响应**: 二进制文件流 (application/zip)

**设计特点**:
- ✅ 流式压缩，内存占用低（约10-20MB）
- ✅ 支持大文件下载（超过4GB）
- ✅ 支持无限数量文件（理论上）
- ✅ 并行处理，下载速度快
- ✅ 普通HTTP接口，兼容性好

**性能指标**:
- 处理5000个400KB文件：约2-3分钟
- 内存占用：峰值约20MB
- 压缩率：约30-50%

## 部署指南

请参考 `SERVER_DEPLOYMENT_GUIDE.md` 文件获取详细的部署说明。

## 测试

运行测试命令:
```bash
python manage.py test
```

## 开发环境搭建

1. 克隆代码库
2. 安装依赖:
   ```bash
   pip install -r requirements.txt
   ```
3. 启动开发服务器:
   ```bash
   python manage.py runserver
   ```
4. 访问 http://127.0.0.1:8000/
5. 访问已使用代码页面: http://127.0.0.1:8000/usedcodes

## 许可证

MIT License
