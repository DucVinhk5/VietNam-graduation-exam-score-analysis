from db.connection import get_connection
from db.repository import insert_results
from db.schema import init_db
from logger import logger

BATCH_SIZE = 500


def saver(result_queue, num_fetcher):
    finished = 0
    buffer = []

    init_db()
    conn = get_connection()
    cursor = conn.cursor()

    def flush():
        if not buffer:
            return
        try:
            insert_results(cursor, buffer)
            conn.commit()
            logger.info(f"Saved batch: {len(buffer)}")
            buffer.clear()
        except Exception as e:
            logger.error(f"[DB ERROR] {e}")

    while finished < num_fetcher:
        item = result_queue.get()

        if item is None:
            finished += 1
            continue

        buffer.extend(item)

        if len(buffer) >= BATCH_SIZE:
            flush()

    flush()
    conn.close()
    logger.info("SQLite closed")
