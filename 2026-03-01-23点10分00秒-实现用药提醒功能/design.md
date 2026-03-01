# 设计文档：用药提醒与记录功能

## 1. 系统架构
本功能将作为一个新的 Django App 模块集成在 `zapp` 中，主要包括后端 Models、Service 逻辑层以及前端 H5 页面。

### 1.1 模块划分
- **Models**: `Medication` (药品), `MedicationSchedule` (计划), `MedicationRecord` (记录)
- **Service**: `MedicationService` (处理 CRUD、打卡逻辑、统计计算)
- **View**: `MedicationView` (页面渲染), `MedicationAPIView` (数据交互)
- **Template**: `medication_tracker.html`

## 2. 数据库设计

### 2.1 Medication (药品表)
| 字段名 | 类型 | 描述 |
| :--- | :--- | :--- |
| id | AutoField | 主键 |
| name | CharField | 药品名称 (如: 阿莫西林) |
| description | TextField | 描述/备注 (可选) |
| total_quantity | IntegerField | 初始总量 (如: 24) |
| current_quantity | IntegerField | 当前剩余量 (如: 20) |
| unit | CharField | 单位 (如: 片, 粒, ml) |
| created_at | DateTime | 创建时间 |

### 2.2 MedicationSchedule (服药计划表)
| 字段名 | 类型 | 描述 |
| :--- | :--- | :--- |
| id | AutoField | 主键 |
| medication | ForeignKey | 关联药品 |
| time_type | CharField | 类型: MORNING(早), NOON(中), EVENING(晚), CUSTOM(自定义) |
| custom_time | TimeField | 自定义具体时间 (可选) |
| dosage_amount | IntegerField | 每次服用数量 (如: 2，用于扣减库存) |
| is_active | Boolean | 是否启用 |

### 2.3 MedicationRecord (服药记录表)
| 字段名 | 类型 | 描述 |
| :--- | :--- | :--- |
| id | AutoField | 主键 |
| schedule | ForeignKey | 关联计划 |
| date | DateField | 记录日期 |
| status | CharField | 状态: TAKEN(已服), MISSED(未服), SKIPPED(跳过) |
| taken_at | DateTime | 实际服用时间 |

## 3. 接口设计 (API)
- `GET /api/medications/`: 获取药品列表
- `POST /api/medications/`: 添加药品
- `GET /api/schedules/daily/?date=YYYY-MM-DD`: 获取某日的服药计划及状态
- `POST /api/records/checkin/`: 打卡 (参数: schedule_id, date, status)
- `GET /api/stats/weekly/?start_date=YYYY-MM-DD`: 获取周统计数据

## 4. UI 设计稿 (Mockup)

### 4.1 页面布局 (H5 移动端风格)

```text
+--------------------------------------------------+
|  < 返回          用药小助手          [+] 添加药品  |
+--------------------------------------------------+
|                                                  |
|  [ < ]      2026年03月01日 (今天)      [ > ]      |
|                                                  |
+--------------------------------------------------+
|  早晨 (Morning)                                  |
|  [x] 阿莫西林 (2片)                    08:00     |
|      Status: 已服 (08:05) | 剩: 18片             |
|  [ ] 维生素C (1片)                     08:00     |
|      Status: 未服 [打卡] | 剩: 90片              |
+--------------------------------------------------+
|  中午 (Noon)                                     |
|  [ ] 布洛芬 (1片)                      12:30     |
|      Status: 未服 [打卡] | 剩: 10粒              |
+--------------------------------------------------+
|  ...                                             |
+--------------------------------------------------+
|  [统计报表]                                      |
|                                                  |
|  本周一览表 (Week 9):                            |
|  药品       | Mon | Tue | Wed | Thu | Fri | ...  |
|  阿莫西林   |  √  |  √  |  !  |  √  |  .  | ...  |
|  维生素C    |  √  |  √  |  √  |  √  |  .  | ...  |
|                                                  |
|  库存核对:                                       |
|  阿莫西林: 理论剩余 18片 (请核对药盒)            |
|                                                  |
+--------------------------------------------------+
|  [底部导航: 首页 | 药品管理 | 统计]                |
+--------------------------------------------------+
```

### 4.2 交互说明
1. **日期切换**: 点击顶部日期的左右箭头 `[ < ]` `[ > ]` 切换查看其他日期的记录。
2. **打卡操作**: 
   - 点击 `[打卡]` 按钮，状态变为 `[x] 已服`，并显示时间。
   - 再次点击已服状态，可撤销为未服。
3. **添加药品**: 点击右上角 `[+]` 弹出模态框或跳转页面添加新药品。
4. **统计展示**: 底部简单展示本周打卡情况，`[ok]` 绿色代表全勤，`[!!]` 红色代表有漏服，`[..]` 灰色代表未来。

### 4.3 样式风格
- **主色调**: 医疗蓝/绿色，给人安全、健康的心理暗示。
- **字体**: 清晰易读，大号字体显示药品名和时间。
- **状态**: 
  - 未服: 灰色/空心圆圈
  - 已服: 绿色/实心对勾
  - 漏服 (过期未服): 红色警告色

## 5. 实现计划
1. 定义 Models 并迁移数据库。
2. 编写 Service 层处理逻辑。
3. 开发 API 接口。
4. 编写 HTML 模板与 JS 交互逻辑。
5. 调试与验证。
