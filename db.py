# db.py
import sqlite3

DB_NAME = "cars.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            link TEXT UNIQUE
        )
    """)
    conn.commit()
    conn.close()

def ad_exists(link: str) -> bool:
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM ads WHERE link = ?", (link,))
    exists = cur.fetchone() is not None
    conn.close()
    return exists

def add_ad(link: str):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO ads (link) VALUES (?)", (link,))
        conn.commit()
    except sqlite3.IntegrityError:
        pass  # уже есть
    conn.close()
