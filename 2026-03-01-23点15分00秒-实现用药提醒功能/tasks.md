# Tasks

- [x] Task 1: Create Project Documentation (Compliance)
  - [x] SubTask 1.1: Create directory `2026-03-01-23点15分00秒-实现用药提醒功能`.
  - [x] SubTask 1.2: Create `requirements.md` in that directory.
  - [x] SubTask 1.3: Create `design.md` in that directory.
  - [x] SubTask 1.4: Create `tasks.md` (project level) in that directory.

- [ ] Task 2: Backend Implementation - Models
  - [ ] SubTask 2.1: Define `Medication`, `MedicationSchedule`, `MedicationRecord` in `zapp/models.py`.
  - [ ] SubTask 2.2: Create and run migrations (`makemigrations`, `migrate`).

- [ ] Task 3: Backend Implementation - Service Layer
  - [ ] SubTask 3.1: Create `zapp/services/medication_service.py`.
  - [ ] SubTask 3.2: Implement `get_daily_schedule(date)`.
  - [ ] SubTask 3.3: Implement `mark_taken(schedule_id, date, status)`.
  - [ ] SubTask 3.4: Implement `get_stats(start_date, end_date)`.
  - [ ] SubTask 3.5: Implement CRUD for Medications and Schedules.

- [ ] Task 4: Backend Implementation - Views & URLs
  - [ ] SubTask 4.1: Create API views in `zapp/views.py` using `medication_service`.
  - [ ] SubTask 4.2: Add URL patterns in `zapp/urls.py`.

- [ ] Task 5: Frontend Implementation
  - [ ] SubTask 5.1: Create `zapp/templates/zapp/medication_tracker.html`.
  - [ ] SubTask 5.2: Implement UI for adding medications and setting schedules.
  - [ ] SubTask 5.3: Implement UI for daily checklist (mark as taken).
  - [ ] SubTask 5.4: Implement UI for statistics (weekly/monthly view).
  - [ ] SubTask 5.5: Implement JS logic using `fetch` and `response.json()` (referencing `timestamp.html`).

- [ ] Task 6: Verification
  - [ ] SubTask 6.1: Verify adding a medication.
  - [ ] SubTask 6.2: Verify scheduling.
  - [ ] SubTask 6.3: Verify marking as taken.
  - [ ] SubTask 6.4: Verify statistics display.
