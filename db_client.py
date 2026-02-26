import sqlite3
from datetime import datetime
import os

# Use absolute path for DB to avoid CWD issues
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "notifications.db")

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with the notified_sessions table."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS notified_sessions (
            event_id TEXT PRIMARY KEY,
            notified_at TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def check_new_sessions(session_ids: list[str]) -> bool:
    """
    Returns True if there is any session_id in the list that is not in the DB.
    """
    if not session_ids:
        return False
    
    conn = get_db_connection()
    c = conn.cursor()
    
    placeholders = ','.join('?' for _ in session_ids)
    c.execute(f'SELECT event_id FROM notified_sessions WHERE event_id IN ({placeholders})', session_ids)
    existing_ids = {row['event_id'] for row in c.fetchall()}
    conn.close()
    
    return len(set(session_ids) - existing_ids) > 0

def mark_sessions_as_notified(session_ids: list[str]):
    """
    Mark the given sessions as notified.
    """
    if not session_ids:
        return
        
    conn = get_db_connection()
    c = conn.cursor()
    notified_at = datetime.now().isoformat()
    
    for sid in session_ids:
        try:
            c.execute('INSERT INTO notified_sessions (event_id, notified_at) VALUES (?, ?)', 
                      (sid, notified_at))
        except sqlite3.IntegrityError:
            pass
            
    conn.commit()
    conn.close()
