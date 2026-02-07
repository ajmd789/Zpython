# Requirements: 复刻登录注册样式

## 1. 背景
当前 Taro 前端项目 (`frontend`) 的登录和注册页面样式较为基础，未适配移动端与 PC 端的差异。
参考项目 (`v0dev/login-and-register-pages`) 实现了基于 Shadcn UI 的现代化样式，并具备良好的响应式设计。
目标是将参考项目的 Input 组件样式及整体页面布局复刻到 Taro 项目中。

## 2. 核心需求

### 2.1 Input 组件样式复刻
- **外观**：复刻 Shadcn UI Input 的圆角 (`rounded-md`)、边框颜色、背景色、字体大小。
- **状态**：
    - Default: 灰色边框 (`border-input`).
    - Focus: 黑色/主色边框，带有 Ring 效果 (`focus-visible:ring`).
    - Disabled: 透明度降低，禁止点击。
- **图标支持**：支持 Input 内部左侧 (Prefix) 和右侧 (Suffix) 图标（如用户名图标、密码锁图标、显示/隐藏密码眼睛图标）。

### 2.2 响应式适配
- **Mobile First**：默认样式适配移动端。
    - 字体大小：`text-base` (16px) 防止 iOS 缩放。
    - 高度：`h-10` (40px) 或 `h-11` (44px) 便于触控。
- **PC 适配**：
    - 当屏幕宽度大于 768px (md) 时，调整字体为 `text-sm` (14px)。
    - 调整容器宽度和布局，确保在宽屏下显示协调（居中卡片式布局）。

### 2.3 页面范围
- 登录页 (`src/pages/login`)
- 注册页 (`src/pages/register`)

### 2.4 技术约束
- 使用 Taro 组件 (`View`, `Input`, `Text`, `Button`, `Image`)。
- 使用 SCSS 进行样式编写（遵循现有项目规范）。
- 尽量提取公共样式或变量，保持代码可维护性。
- 需要手动引入或使用 SVG 图标（类似 Lucide React）。

## 3. 交付物
- 更新后的登录页和注册页代码。
- 适配后的 SCSS 样式文件。
- 必要的全局样式变量（如果需要）。
