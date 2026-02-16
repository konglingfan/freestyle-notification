import sqlite3
from datetime import datetime
import os

DB_NAME = "notifications.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with the sent_logs table."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS sent_logs (
            target_month TEXT PRIMARY KEY,
            sent_at TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def check_if_sent(target_month: str) -> bool:
    """
    Check if a notification has already been sent for the given month.
    target_month format: 'YYYY-MM'
    """
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT 1 FROM sent_logs WHERE target_month = ?', (target_month,))
    result = c.fetchone()
    conn.close()
    return result is not None

def mark_as_sent(target_month: str):
    """
    Mark the notification as sent for the given month.
    """
    conn = get_db_connection()
    c = conn.cursor()
    sent_at = datetime.now().isoformat()
    try:
        c.execute('INSERT INTO sent_logs (target_month, sent_at) VALUES (?, ?)', 
                  (target_month, sent_at))
        conn.commit()
    except sqlite3.IntegrityError:
        # Already exists, which is fine, but strictly shouldn't happen if check_if_sent is called first
        pass
    finally:
        conn.close()
