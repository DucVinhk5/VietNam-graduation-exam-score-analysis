import asyncio
import aiohttp
from tasks.sbd_worker import scan_sbd_cluster
from helper.proxy import get_proxies, check_proxies
from itertools import cycle

RANGE_CUM = range(0, 100)
RANGE_TINH = range(1, 65)

async def orchestrate_scan(base_url):
    # Lấy danh sách proxy
    proxies = get_proxies()
    working_proxies = await check_proxies(proxies)

    if not working_proxies:
        print("No working proxies available. Exiting.")
        return


    proxy_gen = cycle(proxies)

    # Semaphore giới hạn số kết nối đồng thời
    semaphore = asyncio.Semaphore(20)
    result_queue = asyncio.Queue(maxsize=1000)

    async with aiohttp.ClientSession() as session:
        tasks = []

        # Tạo các task scan cho từng tỉnh và cụm
        for ma_tinh in RANGE_TINH:
            for ma_cum in RANGE_CUM:
                tasks.append(
                    scan_sbd_cluster(
                        session=session,
                        base_url=base_url,
                        ma_tinh=ma_tinh,
                        ma_cum=ma_cum,
                        proxy_cycle=proxy_gen,
                        semaphore=semaphore,
                        result_queue=result_queue,
                    )
                )

        # Tạo consumer task ghi dữ liệu vào CSV
        consumer_task = asyncio.create_task(save_results(result_queue, "results.csv"))

        # Chạy tất cả các producer
        await asyncio.gather(*tasks)

        # Gửi tín hiệu dừng cho consumer
        await result_queue.put(None)
        await consumer_task


async def save_results(queue: asyncio.Queue, file_path: str):
    """Consumer: lấy dữ liệu từ queue và ghi ra CSV"""
    import csv

    with open(file_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        while True:
            row = await queue.get()
            if row is None:  # Stop signal
                break
            writer.writerow(row)
            queue.task_done()
