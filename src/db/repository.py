def insert_results(cursor, rows):
    cursor.executemany(
        """
        INSERT OR IGNORE INTO results
        (year, edu, sbd, subject, score)
        VALUES (?, ?, ?, ?, ?)
    """,
        rows,
    )
