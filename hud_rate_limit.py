import sqlite3
import time

DB = "hud_limits.db"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS limits (
            avatar TEXT PRIMARY KEY,
            used INTEGER,
            day INTEGER
        )
    """)
    conn.commit()
    conn.close()

init_db()

def get_today():
    return int(time.strftime("%Y%m%d"))

def get_used_today():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    today = get_today()
    c.execute("SELECT SUM(used) FROM limits WHERE day=?", (today,))
    result = c.fetchone()[0]
    conn.close()
    return result or 0

def consume(avatar):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    today = get_today()

    c.execute("SELECT used, day FROM limits WHERE avatar=?", (avatar,))
    row = c.fetchone()

    if not row:
        c.execute("INSERT INTO limits VALUES (?, ?, ?)", (avatar, 1, today))
        conn.commit()
        conn.close()
        return True, 29

    used, day = row

    if day != today:
        c.execute("UPDATE limits SET used=?, day=? WHERE avatar=?", (1, today, avatar))
        conn.commit()
        conn.close()
        return True, 29

    if used >= 30:
        conn.close()
        return False, 0

    used += 1
    c.execute("UPDATE limits SET used=? WHERE avatar=?", (used, avatar))
    conn.commit()
    conn.close()
    return True, 30 - used
