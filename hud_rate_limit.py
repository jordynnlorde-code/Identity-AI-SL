import sqlite3
from datetime import datetime

DB_PATH = "hud_limits.db"
DAILY_LIMIT = 30

def _conn():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = _conn()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS limits (
            avatar_id TEXT,
            date TEXT,
            count INTEGER,
            PRIMARY KEY (avatar_id, date)
        )
    """)
    conn.commit()
    conn.close()

def _today():
    return datetime.utcnow().strftime("%Y-%m-%d")

def get_remaining(avatar_id: str) -> int:
    conn = _conn()
    c = conn.cursor()
    c.execute("SELECT count FROM limits WHERE avatar_id=? AND date=?", (avatar_id, _today()))
    row = c.fetchone()
    used = row[0] if row else 0
    conn.close()
    return max(0, DAILY_LIMIT - used)

def consume(avatar_id: str):
    conn = _conn()
    c = conn.cursor()
    date = _today()

    c.execute("SELECT count FROM limits WHERE avatar_id=? AND date=?", (avatar_id, date))
    row = c.fetchone()
    used = row[0] if row else 0

    if used >= DAILY_LIMIT:
        conn.close()
        return False, 0

    new_count = used + 1
    c.execute("""
        INSERT INTO limits (avatar_id, date, count)
        VALUES (?, ?, ?)
        ON CONFLICT(avatar_id, date)
        DO UPDATE SET count=excluded.count
    """, (avatar_id, date, new_count))
    conn.commit()
    conn.close()

    remaining = max(0, DAILY_LIMIT - new_count)
    return True, remaining

init_db()
