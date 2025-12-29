from db.connection import get_connection
from db.repository import insert_results
from db.schema import init_db
from logger import logger

BATCH_SIZE = 500
VALID_SIZE = 4


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
        items = result_queue.get()

        if items is None:
            finished += 1
            continue

        valid_items = [item for item in items if len(item) == VALID_SIZE]
        if not valid_items:
            logger.warning("[DATA WARNING] - No valid item")
            continue
        
        if len(valid_items) < len(items):
            sbd = valid_items[0][2]
            logger.warning(
                f"[DATA WARNING] {sbd} - Invalid item size: {len(items)}, expected {VALID_SIZE}"
            )
        buffer.extend(valid_items)

        if len(buffer) >= BATCH_SIZE:
            flush()

    flush()
    conn.close()
    logger.info("SQLite closed")
