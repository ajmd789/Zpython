# Tasks: 复刻登录注册样式

- [ ] Task 1: 定义全局样式变量与图标资源
    - [ ] 修改 `frontend/src/app.scss`，添加 Shadcn UI 风格的 CSS 变量（`--background`, `--foreground`, `--primary`, `--input`, `--ring` 等）。
    - [ ] 在 `frontend/src/assets` 下（或新建 `utils/icons.ts`）准备 User, Lock, Eye, EyeOff, Loader2 的 Base64 SVG 图标常量。

- [ ] Task 2: 重构登录页 (`frontend/src/pages/login`)
    - [ ] 修改 `index.tsx`：
        - [ ] 引入图标资源。
        - [ ] 增加 `isFocused` 状态管理。
        - [ ] 重构 JSX 结构，使用 `View` 包裹 `Input` 实现自定义样式容器。
        - [ ] 添加密码显示/隐藏交互逻辑。
    - [ ] 修改 `index.scss`：
        - [ ] 实现 Mobile First 的基础样式。
        - [ ] 添加 `@media (min-width: 768px)` 响应式规则，实现 PC 端卡片布局。
        - [ ] 确保 Input 的 Focus Ring 效果与设计一致。

- [ ] Task 3: 重构注册页 (`frontend/src/pages/register`)
    - [ ] 修改 `index.tsx`：
        - [ ] 复用登录页的 Input 组件逻辑。
        - [ ] 确保表单验证逻辑与新 UI 兼容。
    - [ ] 修改 `index.scss`：
        - [ ] 复用登录页的响应式样式规则。

- [ ] Task 4: 验证与微调
    - [ ] 启动开发服务器。
    - [ ] 验证移动端视图下的布局和交互。
    - [ ] 验证 PC 端视图下的卡片样式和响应式表现。
