# 音频录音功能设计文档

## 1. 技术架构

### 1.1 前端架构
- **技术栈**：HTML5, CSS3, JavaScript
- **核心 API**：MediaRecorder API, Web Audio API
- **界面框架**：自定义 CSS（响应式设计）
- **文件格式**：webm（浏览器原生支持的音频格式）

### 1.2 后端架构
- **技术栈**：Django
- **核心模块**：文件上传处理
- **存储方式**：文件系统（staticfiles/recordings 目录）
- **API 接口**：/api/save_recording/（POST）

## 2. 页面设计

### 2.1 页面结构
- **顶部**：标题和操作说明
- **中部**：录音控制区域
  - 状态指示器
  - 时间计时器
  - 操作按钮
- **底部**：录音记录列表

### 2.2 界面元素
- **状态指示器**：显示当前状态（准备就绪/正在录音）
- **计时器**：显示录音时长（时:分:秒）
- **开始按钮**：开始录音
- **停止按钮**：停止录音
- **消息提示**：操作结果反馈
- **录音列表**：显示已保存的录音

### 2.3 交互流程
1. 用户访问录音页面
2. 点击「开始录音」按钮
3. 浏览器请求麦克风权限
4. 开始录音，状态变为「正在录音」，计时器开始计时
5. 点击「停止录音」按钮
6. 停止录音，状态变为「准备就绪」，计时器停止
7. 录音文件自动上传到服务器
8. 显示上传结果
9. 录音记录列表更新

## 3. 后端设计

### 3.1 API 设计

#### 3.1.1 保存录音接口
- **URL**：/api/save_recording/
- **方法**：POST
- **参数**：
  - recording：录音文件（multipart/form-data）
- **返回格式**：JSON
- **成功响应**：
  ```json
  {
    "code": 200,
    "data": {
      "filename": "recording_1234567890.webm",
      "file_url": "/static/recordings/recording_1234567890.webm",
      "file_size": 123456
    },
    "message": "success"
  }
  ```
- **失败响应**：
  ```json
  {
    "code": 400,
    "data": null,
    "message": "缺少录音文件"
  }
  ```

### 3.2 文件存储设计
- **存储目录**：staticfiles/recordings/
- **文件名格式**：recording_{timestamp}.webm
- **文件权限**：可读

### 3.3 错误处理
- 文件不存在：400 错误
- 文件保存失败：500 错误
- 其他服务器错误：500 错误

## 4. 前端实现细节

### 4.1 录音核心逻辑
```javascript
// 请求麦克风权限
stream = await navigator.mediaDevices.getUserMedia({ audio: true });

// 创建 MediaRecorder 实例
mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });

// 开始录音
mediaRecorder.start();

// 停止录音
mediaRecorder.stop();

// 处理录音数据
mediaRecorder.addEventListener('dataavailable', function(event) {
  if (event.data.size > 0) {
    audioChunks.push(event.data);
  }
});

// 上传录音
const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
const formData = new FormData();
formData.append('recording', audioBlob, `recording_${Date.now()}.webm`);

fetch('/apipy/api/save_recording/', {
  method: 'POST',
  body: formData
});
```

### 4.2 计时器实现
- 使用 setInterval 实现实时计时
- 格式化为 HH:MM:SS 格式
- 录音开始时启动，停止时暂停

### 4.3 状态管理
- 录音状态：未录音/录音中
- 按钮状态：开始按钮（可用/禁用）、停止按钮（可用/禁用）
- 状态文本和指示器：根据录音状态更新

## 5. 安全性考虑

### 5.1 前端安全
- 只请求必要的麦克风权限
- 不存储敏感信息
- 合理处理用户隐私

### 5.2 后端安全
- 验证文件类型
- 限制文件大小
- 防止路径遍历攻击
- 确保文件存储安全

## 6. 性能优化

### 6.1 前端优化
- 使用流式录音，减少内存占用
- 优化文件上传速度
- 响应式设计，提高用户体验

### 6.2 后端优化
- 高效文件处理
- 合理的错误处理
- 优化存储结构

## 7. 扩展性考虑

### 7.1 功能扩展
- 支持更多音频格式
- 添加录音编辑功能
- 实现录音分享功能
- 增加录音分类管理

### 7.2 技术扩展
- 支持云存储
- 实现音频转文字
- 添加音频分析功能

## 8. 测试计划

### 8.1 功能测试
- 录音功能测试
- 文件上传测试
- 错误处理测试

### 8.2 兼容性测试
- 主流浏览器兼容性
- 不同设备兼容性

### 8.3 性能测试
- 录音时长测试
- 文件大小测试
- 上传速度测试