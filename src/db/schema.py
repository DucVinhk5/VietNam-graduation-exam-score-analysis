from db.connection import get_connection


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.execute("PRAGMA synchronous=NORMAL;")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER,
            edu TEXT,
            sbd TEXT,
            subject TEXT,
            score REAL,
            UNIQUE(sbd, subject)
        )
    """)

    conn.commit()
    conn.close()
