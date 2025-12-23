import sqlite3

DB_PATH = "results.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    return conn
