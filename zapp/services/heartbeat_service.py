import datetime
import os
import sqlite3

from django.utils import timezone


def get_db_path():
    env_db_path = os.environ.get('ACCOUNTING_DB_PATH')
    if env_db_path:
        return env_db_path
    project_db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'accounting.db')
    if os.path.exists(project_db_path):
        return project_db_path
    legacy_linux_db_path = '/var/codes/deploy/backend/backendCodes/the-go/accounting.db'
    if os.path.exists(legacy_linux_db_path):
        return legacy_linux_db_path
    return project_db_path


def _normalize_heartbeat_time(raw_timestamp):
    if raw_timestamp is None or raw_timestamp == '':
        return timezone.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        ts = float(raw_timestamp)
        if ts > 10000000000:
            ts = ts / 1000.0
        heartbeat_time_obj = datetime.datetime.fromtimestamp(ts, tz=timezone.get_current_timezone())
        return heartbeat_time_obj.strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        return timezone.now().strftime('%Y-%m-%d %H:%M:%S')


def report_heartbeat(device_name, timestamp=None, ip_address=None):
    if not isinstance(device_name, str):
        raise ValueError("Missing 'device_name'")
    normalized_device_name = device_name.strip()
    if not normalized_device_name:
        raise ValueError("Missing 'device_name'")
    if len(normalized_device_name) > 128:
        raise ValueError("'device_name' too long")
    heartbeat_time = _normalize_heartbeat_time(timestamp)
    ip = (ip_address or '').strip()
    db_path = get_db_path()
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS zapp_device (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                last_heartbeat TEXT,
                ip_address TEXT,
                status TEXT DEFAULT 'offline'
            )
        ''')
        cursor.execute('SELECT id FROM zapp_device WHERE name = ?', (normalized_device_name,))
        row = cursor.fetchone()
        if row:
            cursor.execute(
                '''
                UPDATE zapp_device
                SET last_heartbeat = ?, ip_address = ?, status = 'online'
                WHERE name = ?
                ''',
                (heartbeat_time, ip, normalized_device_name),
            )
        else:
            cursor.execute(
                '''
                INSERT INTO zapp_device (name, last_heartbeat, ip_address, status)
                VALUES (?, ?, ?, 'online')
                ''',
                (normalized_device_name, heartbeat_time, ip),
            )
        conn.commit()
    return {
        "device_name": normalized_device_name,
        "status": "online",
        "last_heartbeat": heartbeat_time,
    }
