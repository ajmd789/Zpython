# Medication Reminder Design

## Architecture Changes

### Database Models (`zapp/models.py`)
1.  **Medication**
    -   `name`: CharField (max_length=255)
    -   `description`: TextField (blank=True)
    -   `dosage`: CharField (max_length=100)
    -   `user`: ForeignKey to User (if user-specific)

2.  **MedicationSchedule**
    -   `medication`: ForeignKey to Medication
    -   `time`: TimeField
    -   `frequency_type`: CharField (choices: 'morning', 'noon', 'evening', 'custom')
    -   `days_of_week`: CharField (optional, e.g., "1,2,3,4,5,6,7" for daily)

3.  **MedicationRecord**
    -   `schedule`: ForeignKey to MedicationSchedule
    -   `date`: DateField
    -   `status`: CharField (choices: 'taken', 'missed', 'skipped')
    -   `taken_at`: DateTimeField (null=True, blank=True)

### Service Layer (`zapp/services/medication_service.py`)
-   `create_medication(data)`
-   `update_medication(id, data)`
-   `delete_medication(id)`
-   `create_schedule(medication_id, time, type)`
-   `get_daily_schedule(date)`: Returns list of schedules for the date, joined with any existing records.
-   `mark_taken(schedule_id, date)`: Creates or updates a MedicationRecord.
-   `get_stats(start_date, end_date)`: Aggregates taken vs. missed counts.

### API/Views (`zapp/views.py`)
-   `medication_tracker_view(request)`: Renders the main page.
-   `api_get_medications(request)`: GET list of medications.
-   `api_save_medication(request)`: POST to create/update.
-   `api_get_daily_schedule(request)`: GET schedules for a specific date (default today).
-   `api_mark_taken(request)`: POST to update status.
-   `api_get_stats(request)`: GET stats for chart.

### URL Routing (`zapp/urls.py`)
-   `path('medication/', views.medication_tracker_view, name='medication_tracker')`
-   `path('api/medication/list/', views.api_get_medications, name='api_get_medications')`
-   `path('api/medication/save/', views.api_save_medication, name='api_save_medication')`
-   `path('api/medication/schedule/daily/', views.api_get_daily_schedule, name='api_get_daily_schedule')`
-   `path('api/medication/record/update/', views.api_mark_taken, name='api_mark_taken')`
-   `path('api/medication/stats/', views.api_get_stats, name='api_get_stats')`

### Frontend (`zapp/templates/zapp/medication_tracker.html`)
-   **Layout**:
    -   Header: "Medication Tracker"
    -   Tabs/Sections: "Today's Schedule", "Manage Medications", "History/Stats".
    -   "Today's Schedule": List of items with checkboxes or "Take" buttons.
    -   "Manage Medications": Form to add name, dosage, and set times.
    -   "History/Stats": Simple bar chart or table showing adherence.
-   **Interaction**:
    -   Use `fetch` for all actions to avoid page reloads.
    -   Update DOM dynamically upon success.
