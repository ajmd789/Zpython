# Design: 复刻登录注册样式

## 1. 样式架构设计

为了高度还原 Shadcn UI 的视觉效果，我们将引入一套 CSS 变量系统，并在 Taro 中通过 SCSS 实现响应式布局和组件样式。

### 1.1 全局样式变量 (Variables)
将参考项目 `globals.css` 中的核心颜色变量移植到 Taro 项目中。
建议在 `frontend/src/app.scss` 中定义，以便全局复用。

```scss
:root {
  --background: #ffffff;
  --foreground: #020817;
  --primary: #2563eb; /* 对应 text-primary / blue-600 */
  --primary-foreground: #ffffff;
  --muted: #f1f5f9;
  --muted-foreground: #64748b;
  --input: #e2e8f0; /* 边框颜色 */
  --ring: #2563eb;  /* Focus ring color */
  --radius: 0.5rem;
}
```

### 1.2 Input 组件复刻方案
由于 Taro 的 `Input` 是原生组件，无法像 Web 那样直接通过 CSS 伪类 `:focus-within` 完美控制父级样式（部分小程序支持，但不统一）。
**方案**：使用 **"容器包裹模式"**。

*   **HTML 结构**:
    ```tsx
    <View className={`input-wrapper ${isFocused ? 'focused' : ''}`}>
      {/* 左侧图标 */}
      <Image src={iconUser} className="input-icon left" />
      
      {/* 核心输入框 */}
      <Input 
        className="taro-input"
        onFocus={() => setIsFocused(true)}
        onBlur={() => setIsFocused(false)}
        placeholderClass="placeholder"
        {...props}
      />
      
      {/* 右侧图标 (如显示密码) */}
      <View className="input-icon right" onClick={togglePassword}>
        <Image src={iconEye} />
      </View>
    </View>
    ```

*   **SCSS 样式**:
    ```scss
    .input-wrapper {
      display: flex;
      align-items: center;
      height: 44px; // Mobile friendly
      padding: 0 12px;
      border: 1px solid var(--input);
      border-radius: var(--radius);
      background-color: transparent;
      transition: all 0.2s;

      &.focused {
        border-color: var(--ring);
        box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2); // Ring effect
        outline: none;
      }
      
      .taro-input {
        flex: 1;
        height: 100%;
        font-size: 16px; // Mobile: 16px
        color: var(--foreground);
      }
    }
    ```

### 1.3 响应式布局策略
利用 CSS Media Queries 实现 PC 端与移动端的差异化展示。

*   **容器 (.login-container)**:
    *   **Default (Mobile)**: `flex-direction: column`, `padding: 20px`, `background: var(--background)`.
    *   **PC (@media min-width: 768px)**: 
        *   `background: #f5f5f5` (区分卡片背景).
        *   内容居中显示。

*   **卡片 (.login-form)**:
    *   **Default (Mobile)**: `width: 100%`, `box-shadow: none`, `background: transparent`.
    *   **PC**: 
        *   `width: 400px`.
        *   `background: var(--background)`.
        *   `border-radius: var(--radius)`.
        *   `box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1)`.
        *   `padding: 40px`.

## 2. 详细实现步骤

### 2.1 资源准备
需要将 SVG 图标（User, Lock, Eye, EyeOff, Loader2）转换为 Base64 字符串或 SVG 文件，存放在 `src/assets/icons` 目录，或者直接以 Base64 常量形式定义在组件文件中（为了简化文件管理，优先推荐 Base64 常量）。

### 2.2 登录页重构 (Login Page)
1.  **引入状态**: 为 Username 和 Password 输入框分别引入 `isFocused` 状态。
2.  **重写 JSX**: 使用上述 `input-wrapper` 结构替换原有的简单 `Input`。
3.  **样式迁移**: 将 `src/pages/login/index.scss` 重写，引入 Shadcn 风格变量和响应式规则。

### 2.3 注册页重构 (Register Page)
1.  复用登录页的样式和逻辑。
2.  确保 `Confirm Password` 字段同样应用新样式。

## 3. 验证计划
1.  **H5 模式验证**:
    *   使用 Chrome 开发者工具模拟 iPhone (Mobile 视图)。
    *   切换至 Desktop 视图 (>768px) 验证卡片布局。
2.  **功能验证**:
    *   输入框 Focus/Blur 样式变化。
    *   密码显示/隐藏切换。
    *   Loading 状态按钮样式。

