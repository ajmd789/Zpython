# 股票代码管理API文档

## 接口列表

### 1. 获取未使用的股票代码

**接口地址**：`/api/noUseCode/`

**请求方法**：`GET`

**功能描述**：获取一个未使用的股票代码，返回后该代码仍为未使用状态，需要调用`addTodayCode`接口标记为已使用。

**请求参数**：无

**响应格式**：
```json
{
  "code": 200,
  "data": {
    "code": "股票代码"
  },
  "message": "success"
}
```

**响应字段说明**：
- `code`：响应状态码，200表示成功，其他表示失败
- `data`：返回的数据对象
  - `code`：未使用的股票代码
- `message`：响应消息，成功时为"success"，失败时为错误信息

**示例请求**：
```
curl http://127.0.0.1:8000/api/noUseCode/
```

**示例响应**：
```json
{
  "code": 200,
  "data": {
    "code": "000598"
  },
  "message": "success"
}
```

**错误响应示例**：
```json
{
  "code": 404,
  "data": null,
  "message": "没有可用的未使用股票代码"
}
```

---

### 2. 标记股票代码为已使用

**接口地址**：`/api/addTodayCode/`

**请求方法**：`POST`

**功能描述**：标记指定股票代码为已使用状态，并可存储相关的自定义数据。

**请求参数**：

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| code   | String | 是 | 要标记为已使用的股票代码 |
| codeData | String | 是 | 自定义字符串数据，允许为空字符串 |

**响应格式**：
```json
{
  "code": 200,
  "data": null,
  "message": "success"
}
```

**响应字段说明**：
- `code`：响应状态码，200表示成功，其他表示失败
- `data`：返回的数据对象，成功时为null
- `message`：响应消息，成功时为"success"，失败时为错误信息

**示例请求**：
```bash
# 使用curl命令（Linux/Mac）
curl -X POST -d "code=000598&codeData=test_data" http://127.0.0.1:8000/api/addTodayCode/

# 使用PowerShell命令（Windows）
Invoke-WebRequest -Uri http://127.0.0.1:8000/api/addTodayCode/ -Method POST -Body @{code='000598'; codeData='test_data'} -ContentType 'application/x-www-form-urlencoded'
```

**示例响应**：
```json
{
  "code": 200,
  "data": null,
  "message": "success"
}
```

**错误响应示例**：
```json
# 缺少code参数
{
  "code": 400,
  "data": null,
  "message": "缺少code参数"
}

# 缺少codeData参数
{
  "code": 400,
  "data": null,
  "message": "缺少codeData参数"
}

# 股票代码不存在
{
  "code": 404,
  "data": null,
  "message": "股票代码不存在"
}
```

## 数据存储说明

- 股票代码的使用状态存储在SQLite数据库中
- 每个代码有以下状态：
  - `used`：0表示未使用，1表示已使用
  - `used_at`：代码被标记为已使用的时间
  - `codeData`：存储的自定义字符串数据
- 代码使用后不会自动重置，需要通过其他方式重置（如调用`reset_code_usage`方法）

## 调用流程建议

1. 调用`/api/noUseCode/`获取一个未使用的股票代码
2. 使用获取到的股票代码进行相关业务操作
3. 调用`/api/addTodayCode/`标记该代码为已使用，并存储相关数据

## 注意事项

1. 每个代码只能被标记为已使用一次，重复标记不会产生错误
2. `codeData`字段必须传递，即使值为空字符串
3. API调用返回的股票代码需要及时使用并标记，否则可能被其他调用者获取
4. 建议在标记代码为已使用时，将相关业务数据存储在`codeData`字段中，以便后续查询

## 版本信息

- 版本：v1.0
- 更新时间：2026-01-06
- 支持的功能：获取未使用代码、标记代码为已使用、存储自定义数据