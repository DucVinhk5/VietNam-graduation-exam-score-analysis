import threading
from queue import Queue

from core.driver import setup_driver
from core.sbd import sbd_generator
from logger import logger
from services.fetcher import fetcher
from services.monitor import monitor_input
from services.saver import saver


def orchestrator_system(num_driver, start_tinh, end_tinh):
    assert end_tinh > start_tinh and end_tinh > 0, ValueError

    NUM_TINH = end_tinh - start_tinh + 1
    if NUM_TINH < num_driver:
        num_driver = NUM_TINH

    drivers = [setup_driver() for _ in range(num_driver)]
    result_queue = Queue(maxsize=1000)

    base = NUM_TINH // num_driver
    remainder = NUM_TINH % num_driver

    threads = []
    current = start_tinh

    for i, driver in enumerate(drivers, 1):
        size = base + (1 if i <= remainder else 0)
        start, end = current, current + size - 1
        current = end + 1

        gen = sbd_generator(start, end)
        t = threading.Thread(
            target=fetcher, args=(i, driver, gen, result_queue), daemon=True
        )
        t.start()
        threads.append(t)

    save_thread = threading.Thread(
        target=saver, args=(result_queue, num_driver), daemon=True
    )
    save_thread.start()
    monitor_thread = threading.Thread(target=monitor_input, daemon=True)
    monitor_thread.start()
    for t in threads:
        t.join()

    save_thread.join()

    logger.info("🎉 HOÀN THÀNH")
