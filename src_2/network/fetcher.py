import asyncio
from random import uniform

import aiohttp
from helper.color_map import RESET, STATUS_MAP

RETRY = 3


async def fetch_html(
    session: aiohttp.ClientSession,
    url: str,
    proxies: list[str],
    timeout: aiohttp.ClientTimeout = aiohttp.ClientTimeout(10),
) -> str | None:
    # Tách year và sbd từ URL để hiển thị log
    url_parts = url.split("/")
    sbd = url_parts[-1].split(".")[0]
    year = url_parts[-2]

    for attempt in range(1, RETRY + 1):
        try:
            proxy = next(proxies)
            async with session.get(
                url=url, proxy=f"http://{proxy}", timeout=timeout
            ) as response:
                # Nếu 404, kết thúc ngay
                if response.status == 404:
                    icon, color = STATUS_MAP["Fail"]
                    print(f"Fetch: {year} - {sbd}, {color}Status: {icon} Fail{RESET}")
                    return None

                # Nếu 200, đọc nội dung và trả về
                if response.status == 200:
                    icon, color = STATUS_MAP["Success"]
                    print(
                        f"Fetch: {year} - {sbd}, {color}Status: {icon} Success{RESET}"
                    )
                    return await response.text()

                # Các status khác raise exception
                response.raise_for_status()

        except Exception:
            icon, color = STATUS_MAP["Retry"]
            print(
                f"Retry {attempt}/{RETRY} for {year} - {sbd}, {color}Status: {icon} Retry{RESET}"
            )
            # Sleep ngẫu nhiên trước khi retry
            await asyncio.sleep(uniform(0.2, 0.5))

    # Nếu hết tất cả retry mà vẫn fail
    icon, color = STATUS_MAP["Fail"]
    print(f"Fetch: {year} - {sbd}, {color}Status: {icon} Fail{RESET}")
    return None
