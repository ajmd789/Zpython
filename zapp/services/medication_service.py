import sqlite3
import os
import logging
from datetime import timedelta, datetime
from django.utils import timezone

logger = logging.getLogger(__name__)

# Database path (same as memo_service.py)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, 'accounting.db')

class MedicationService:
    def __init__(self):
        self.db_path = DB_PATH
        self._create_tables()

    def _create_tables(self):
        """Create necessary tables if they don't exist"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Medications table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS medications (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        name TEXT NOT NULL,
                        description TEXT,
                        dosage TEXT,
                        total_quantity INTEGER DEFAULT 0,
                        current_quantity INTEGER DEFAULT 0,
                        unit TEXT DEFAULT '片',
                        created_at TEXT NOT NULL
                    )
                ''')
                # Schedules table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS medication_schedules (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        medication_id INTEGER NOT NULL,
                        time TEXT NOT NULL,
                        frequency_type TEXT,
                        days_of_week TEXT DEFAULT '1,2,3,4,5,6,7',
                        dosage_amount INTEGER DEFAULT 1,
                        created_at TEXT NOT NULL,
                        FOREIGN KEY (medication_id) REFERENCES medications (id) ON DELETE CASCADE
                    )
                ''')
                # Records table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS medication_records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        schedule_id INTEGER NOT NULL,
                        date TEXT NOT NULL,
                        status TEXT DEFAULT 'missed',
                        taken_at TEXT,
                        created_at TEXT NOT NULL,
                        FOREIGN KEY (schedule_id) REFERENCES medication_schedules (id) ON DELETE CASCADE,
                        UNIQUE(schedule_id, date)
                    )
                ''')
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Database table creation error: {str(e)}")
            raise Exception("Database operation failed.")

    def _get_conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def get_user_medications(self, user_id):
        """Get all medications for a user"""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM medications WHERE user_id = ? ORDER BY id DESC', (str(user_id),))
            return [dict(row) for row in cursor.fetchall()]

    def create_medication(self, user_id, data):
        """Create a new medication"""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('''
                INSERT INTO medications (user_id, name, description, dosage, total_quantity, current_quantity, unit, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                str(user_id),
                data.get('name'),
                data.get('description', ''),
                data.get('dosage', ''),
                data.get('total_quantity', 0),
                data.get('current_quantity', 0),
                data.get('unit', '片'),
                now
            ))
            conn.commit()
            return cursor.lastrowid

    def update_medication(self, user_id, medication_id, data):
        """Update an existing medication"""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE medications 
                SET name = ?, description = ?, dosage = ?, total_quantity = ?, current_quantity = ?, unit = ?
                WHERE id = ? AND user_id = ?
            ''', (
                data.get('name'),
                data.get('description', ''),
                data.get('dosage', ''),
                data.get('total_quantity', 0),
                data.get('current_quantity', 0),
                data.get('unit', '片'),
                medication_id,
                str(user_id)
            ))
            conn.commit()
            return cursor.rowcount > 0

    def delete_medication(self, user_id, medication_id):
        """Delete a medication"""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM medications WHERE id = ? AND user_id = ?', (medication_id, str(user_id)))
            conn.commit()
            return cursor.rowcount > 0

    def create_schedule(self, user_id, data):
        """Create a schedule for a medication"""
        # Verify medication belongs to user
        medication_id = data.get('medication_id')
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM medications WHERE id = ? AND user_id = ?', (medication_id, str(user_id)))
            if not cursor.fetchone():
                raise Exception("Medication not found or access denied")
            
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('''
                INSERT INTO medication_schedules (medication_id, time, frequency_type, days_of_week, dosage_amount, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                medication_id,
                data.get('time'),
                data.get('frequency_type', 'custom'),
                data.get('days_of_week', '1,2,3,4,5,6,7'),
                data.get('dosage_amount', 1),
                now
            ))
            conn.commit()
            return cursor.lastrowid

    def delete_schedule(self, user_id, schedule_id):
        """Delete a schedule"""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            # Verify ownership via medication
            cursor.execute('''
                DELETE FROM medication_schedules 
                WHERE id = ? AND medication_id IN (SELECT id FROM medications WHERE user_id = ?)
            ''', (schedule_id, str(user_id)))
            conn.commit()
            return cursor.rowcount > 0

    def get_daily_schedule(self, user_id, date_obj):
        """Get daily schedule for a specific date"""
        weekday = str(date_obj.isoweekday())
        date_str = date_obj.strftime('%Y-%m-%d')
        
        with self._get_conn() as conn:
            cursor = conn.cursor()
            # Join medications and schedules
            cursor.execute('''
                SELECT s.id, s.time, s.frequency_type, s.dosage_amount, s.days_of_week,
                       m.name as medication_name, m.unit as medication_unit, m.dosage,
                       m.current_quantity, m.total_quantity,
                       r.status, r.taken_at
                FROM medication_schedules s
                JOIN medications m ON s.medication_id = m.id
                LEFT JOIN medication_records r ON s.id = r.schedule_id AND r.date = ?
                WHERE m.user_id = ?
            ''', (date_str, str(user_id)))
            
            rows = cursor.fetchall()
            daily_schedules = []
            
            for row in rows:
                if weekday in row['days_of_week'].split(','):
                    status = row['status'] if row['status'] else 'missed'
                    if date_obj > timezone.now().date() and not row['status']:
                        status = 'pending'
                        
                    daily_schedules.append({
                        'id': row['id'],
                        'medication_name': row['medication_name'],
                        'medication_unit': row['medication_unit'],
                        'dosage': row['dosage'],
                        'dosage_amount': row['dosage_amount'],
                        'time': row['time'], # Assumes time is stored as HH:MM string
                        'time_type': row['frequency_type'],
                        'current_quantity': row['current_quantity'],
                        'total_quantity': row['total_quantity'],
                        'status': status,
                        'taken_at': row['taken_at']
                    })
            
            daily_schedules.sort(key=lambda x: x['time'])
            return daily_schedules

    def mark_taken(self, schedule_id, date_str):
        """Mark a schedule as taken"""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            
            # Check if already taken
            cursor.execute('SELECT status FROM medication_records WHERE schedule_id = ? AND date = ?', (schedule_id, date_str))
            record = cursor.fetchone()
            if record and record['status'] == 'taken':
                return {'success': False, 'message': 'Already taken'}
            
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Insert or update record
            if record:
                cursor.execute('UPDATE medication_records SET status = ?, taken_at = ? WHERE schedule_id = ? AND date = ?', 
                               ('taken', now, schedule_id, date_str))
            else:
                cursor.execute('''
                    INSERT INTO medication_records (schedule_id, date, status, taken_at, created_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (schedule_id, date_str, 'taken', now, now))
            
            # Deduct inventory
            cursor.execute('SELECT dosage_amount, medication_id FROM medication_schedules WHERE id = ?', (schedule_id,))
            schedule = cursor.fetchone()
            if schedule:
                dosage = schedule['dosage_amount']
                med_id = schedule['medication_id']
                cursor.execute('UPDATE medications SET current_quantity = current_quantity - ? WHERE id = ?', (dosage, med_id))
                
                # Get updated quantity
                cursor.execute('SELECT current_quantity FROM medications WHERE id = ?', (med_id,))
                new_quantity = cursor.fetchone()['current_quantity']
                
                conn.commit()
                return {'success': True, 'current_quantity': new_quantity}
            
            conn.commit()
            return {'success': True}

    def undo_taken(self, schedule_id, date_str):
        """Undo taken status"""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            
            # Check if marked as taken
            cursor.execute('SELECT status FROM medication_records WHERE schedule_id = ? AND date = ?', (schedule_id, date_str))
            record = cursor.fetchone()
            
            if not record or record['status'] != 'taken':
                return {'success': False, 'message': 'Not marked as taken'}
            
            # Update record
            cursor.execute('UPDATE medication_records SET status = ?, taken_at = NULL WHERE schedule_id = ? AND date = ?', 
                           ('missed', schedule_id, date_str))
            
            # Restore inventory
            cursor.execute('SELECT dosage_amount, medication_id FROM medication_schedules WHERE id = ?', (schedule_id,))
            schedule = cursor.fetchone()
            if schedule:
                dosage = schedule['dosage_amount']
                med_id = schedule['medication_id']
                cursor.execute('UPDATE medications SET current_quantity = current_quantity + ? WHERE id = ?', (dosage, med_id))
                
                # Get updated quantity
                cursor.execute('SELECT current_quantity FROM medications WHERE id = ?', (med_id,))
                new_quantity = cursor.fetchone()['current_quantity']
                
                conn.commit()
                return {'success': True, 'current_quantity': new_quantity}
                
            conn.commit()
            return {'success': True}

    def get_weekly_report(self, user_id, start_date_obj):
        """Get weekly report"""
        end_date_obj = start_date_obj + timedelta(days=6)
        
        with self._get_conn() as conn:
            cursor = conn.cursor()
            
            # Get all medications
            cursor.execute('SELECT * FROM medications WHERE user_id = ?', (str(user_id),))
            medications = [dict(row) for row in cursor.fetchall()]
            
            report = []
            
            for med in medications:
                med_data = {
                    'name': med['name'],
                    'current_quantity': med['current_quantity'],
                    'total_quantity': med['total_quantity'],
                    'unit': med['unit'],
                    'daily_status': []
                }
                
                # Get schedules for this medication
                cursor.execute('SELECT * FROM medication_schedules WHERE medication_id = ?', (med['id'],))
                schedules = [dict(row) for row in cursor.fetchall()]
                
                current_day = start_date_obj
                while current_day <= end_date_obj:
                    weekday = str(current_day.isoweekday())
                    date_str = current_day.strftime('%Y-%m-%d')
                    
                    status_list = []
                    has_schedule = False
                    
                    for schedule in schedules:
                        if weekday in schedule['days_of_week'].split(','):
                            has_schedule = True
                            # Check record
                            cursor.execute('SELECT status FROM medication_records WHERE schedule_id = ? AND date = ?', (schedule['id'], date_str))
                            record = cursor.fetchone()
                            
                            if record:
                                status_list.append(record['status'])
                            else:
                                if current_day <= timezone.now().date():
                                    status_list.append('missed')
                                else:
                                    status_list.append('pending')
                    
                    final_status = 'none'
                    if has_schedule:
                        if 'missed' in status_list:
                            final_status = 'missed'
                        elif 'taken' in status_list:
                            if all(s == 'taken' for s in status_list):
                                final_status = 'taken'
                            else:
                                final_status = 'partial'
                        elif 'pending' in status_list:
                            final_status = 'pending'
                            
                    med_data['daily_status'].append({
                        'date': date_str,
                        'status': final_status
                    })
                    
                    current_day += timedelta(days=1)
                
                report.append(med_data)
                
            return report

# Create global instance
medication_service = MedicationService()
