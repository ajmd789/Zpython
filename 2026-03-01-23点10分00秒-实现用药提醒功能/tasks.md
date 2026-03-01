# 任务列表：用药提醒与记录功能

- [ ] Task 1: 创建项目文档与目录
  - [x] SubTask 1.1: 创建目录 `2026-03-01-23点10分00秒-实现用药提醒功能`.
  - [x] SubTask 1.2: 创建 `requirements.md` (需求文档).
  - [x] SubTask 1.3: 创建 `design.md` (设计文档，含UI草图).
  - [x] SubTask 1.4: 创建 `tasks.md` (本任务列表).

- [ ] Task 2: Backend Implementation - Models
  - [ ] SubTask 2.1: Define `Medication` (add quantity/unit), `MedicationSchedule` (add dosage_amount), `MedicationRecord`.
  - [ ] SubTask 2.2: Create and run migrations.

- [ ] Task 3: Backend Implementation - Service Layer
  - [ ] SubTask 3.1: Create `zapp/services/medication_service.py`.
  - [ ] SubTask 3.2: Implement `get_daily_schedule(date)` with inventory check.
  - [ ] SubTask 3.3: Implement `mark_taken` (deduct inventory) & `undo_taken` (restore inventory).
  - [ ] SubTask 3.4: Implement `get_weekly_report(start_date, end_date)` for the overview table.
  - [ ] SubTask 3.5: Implement CRUD for Medications and Schedules.

- [ ] Task 4: Backend Implementation - Views & URLs
  - [ ] SubTask 4.1: Create API views in `zapp/views.py`.
  - [ ] SubTask 4.2: Add URL patterns in `zapp/urls.py`.

- [ ] Task 5: Frontend Implementation
  - [ ] SubTask 5.1: Create `zapp/templates/zapp/medication_tracker.html`.
  - [ ] SubTask 5.2: UI for adding medications (inc. total quantity/unit).
  - [ ] SubTask 5.3: UI for daily checklist (display remaining stock).
  - [ ] SubTask 5.4: UI for weekly overview table (grid view).
  - [ ] SubTask 5.5: Implement JS logic.

- [ ] Task 6: Verification
  - [ ] SubTask 6.1: Verify inventory deduction logic.
  - [ ] SubTask 6.2: Verify weekly report display.
