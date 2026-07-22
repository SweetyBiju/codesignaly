import sqlite3
import os
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(__file__), "data.db")

def init_db():
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS problems (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                slug TEXT UNIQUE,
                title TEXT,
                difficulty TEXT,
                pattern_tags TEXT,
                fetched_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                problem_id INTEGER,
                pattern TEXT,
                started_at DATETIME,
                ended_at DATETIME,
                time_taken_seconds INTEGER,
                hints_used INTEGER DEFAULT 0,
                outcome TEXT,
                FOREIGN KEY (problem_id) REFERENCES problems (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pattern_mastery (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_name TEXT UNIQUE,
                problems_attempted INTEGER DEFAULT 0,
                problems_succeeded INTEGER DEFAULT 0,
                mastery_score REAL DEFAULT 0.0,
                last_practiced DATETIME
            )
        ''')
        conn.commit()

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()
