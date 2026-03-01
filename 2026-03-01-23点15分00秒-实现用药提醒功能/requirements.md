# Medication Reminder Requirements

## Overview
The user needs a way to track daily medication intake, set reminders (morning, noon, evening), customize medication names and times, and view statistics (taken vs. missed) on a weekly or monthly basis. This helps in adhering to medication schedules and maintaining health records.

## Requirements

### 1. Medication Management
The system SHALL allow users to add, edit, and delete medications.
- **Scenario: Add Medication**
  - **WHEN** user enters a medication name and dosage
  - **THEN** the medication is saved to the database.

### 2. Schedule Management
The system SHALL allow users to set specific times for medication (Morning, Noon, Evening or custom time).
- **Scenario: Set Schedule**
  - **WHEN** user assigns a time to a medication
  - **THEN** a schedule entry is created.

### 3. Daily Tracking & Reminder
The system SHALL display a daily list of medications to be taken and allow marking them as taken.
- **Scenario: Mark as Taken**
  - **WHEN** user clicks "Taken" on a scheduled medication for today
  - **THEN** the record is updated to "Taken" with the current timestamp.

### 4. Statistics & History
The system SHALL provide a weekly/monthly view of medication history and statistics (taken vs. missed).
- **Scenario: View Stats**
  - **WHEN** user selects "Weekly Report"
  - **THEN** the system displays a chart or list of taken/missed counts for the week.
