import asyncio
import aiohttp
from network.fetcher import fetch_html
from tasks.parser import parser_html
from random import uniform

MAX_MISSING = 5
RANGE_SO = range(0, 1000)


def format_sbd(ma_tinh, ma_cum, ma_so):
    return f"{ma_tinh:02d}{ma_cum:02d}{ma_so:04d}"


async def scan_sbd_cluster(
    session: aiohttp.ClientSession,
    base_url: str,
    ma_tinh: int,
    ma_cum: int,
    proxy_cycle,
    semaphore: asyncio.Semaphore,
    result_queue: asyncio.Queue,
):
    """
    Producer: scan một cluster SBD, fetch HTML, parse và đẩy kết quả vào queue
    """
    missing_count = 0

    for ma_so in RANGE_SO:
        sbd = format_sbd(ma_tinh, ma_cum, ma_so)
        url = f"{base_url}/{sbd}.html"

        async with semaphore:
            page_source = await fetch_html(session=session, url=url, proxies=proxy_cycle)

            if page_source:
                rows = parser_html(page_source, ma_tinh, sbd)
                if rows:
                    for row in rows:
                        await result_queue.put(row)
                    missing_count = 0  # reset nếu có dữ liệu
                else:
                    missing_count += 1
            else:
                missing_count += 1

        # Nếu quá nhiều SBD liên tiếp không có dữ liệu, dừng cluster
        if missing_count >= MAX_MISSING:
            print(f"Cluster {ma_tinh}-{ma_cum}: too many missing SBD, stop scanning")
            break

        # Sleep ngẫu nhiên để tránh bị rate-limit
        await asyncio.sleep(uniform(0.1, 0.3))
