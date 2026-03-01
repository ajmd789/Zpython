import os
import django
from datetime import date, time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zproject.settings')
django.setup()

from django.contrib.auth.models import User
from zapp.services import medication_service
from zapp.models import Medication, MedicationSchedule, MedicationRecord

def test_medication_feature():
    print("Testing Medication Feature...")
    
    # 1. Create Test User
    username = 'test_med_user'
    if User.objects.filter(username=username).exists():
        User.objects.filter(username=username).delete()
    user = User.objects.create_user(username=username, password='password')
    print(f"User created: {user.username}")
    
    # 2. Add Medication
    med = medication_service.create_medication(user, 'Vitamin C', '500mg', 'Daily supplement')
    print(f"Medication created: {med.name}")
    assert med.name == 'Vitamin C'
    
    # 3. Add Schedule
    schedule = medication_service.create_schedule(med.id, time(8, 0), 'morning')
    print(f"Schedule created: {schedule.time} - {schedule.frequency_type}")
    assert schedule.frequency_type == 'morning'
    
    # 4. Get Daily Schedule
    today = date.today()
    daily = medication_service.get_daily_schedule(user, today)
    print(f"Daily schedule count: {len(daily)}")
    assert len(daily) == 1
    assert daily[0]['status'] == 'missed'
    
    # 5. Mark as Taken
    record = medication_service.mark_taken(schedule.id, today.strftime('%Y-%m-%d'), 'taken')
    print(f"Marked as taken: {record.status} at {record.taken_at}")
    assert record.status == 'taken'
    
    # 6. Verify Daily Schedule Updated
    daily_updated = medication_service.get_daily_schedule(user, today)
    assert daily_updated[0]['status'] == 'taken'
    print("Daily schedule updated correctly.")
    
    # 7. Get Stats
    stats = medication_service.get_stats(user)
    print(f"Stats: {stats}")
    assert stats['taken'] >= 1
    
    print("All tests passed!")

if __name__ == '__main__':
    test_medication_feature()
