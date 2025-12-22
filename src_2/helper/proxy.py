import asyncio
from random import uniform

import aiohttp
import requests
from bs4 import BeautifulSoup

from helper.color_map import RESET, STATUS_MAP


def get_proxies() -> list:
    response = requests.get("https://free-proxy-list.net/")
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find("tbody")

    proxies = []

    for row in table.find_all("tr"):
        columns = row.find_all("td")

        if columns[4].text == "elite proxy":
            proxy = f"{columns[0].text}:{columns[1].text}"
            proxies.append(proxy)

    return proxies


async def _check_proxy(session, proxy, semaphore, timeout=None, retry=3):
    async with semaphore:
        for i in range(retry):
            try:
                async with session.get(
                    "https://httpbin.org/ip", proxy=f"http://{proxy}", timeout=timeout
                ) as response:
                    response.raise_for_status()
                    icon, color = STATUS_MAP["Success"]
                    print(f"Proxy: {proxy:<21} Status: {color}{icon} Success{RESET}")
                    return proxy
            except Exception:
                icon, color = STATUS_MAP["Retry"]
                print(
                    f"Proxy: {proxy:<21} Status: {color}{icon} Retry {i + 1}/{retry}{RESET}"
                )
                await asyncio.sleep(uniform(0.2, 0.5))
        icon, color = STATUS_MAP["Fail"]
        print(f"Proxy: {proxy:<21} Status: {color}{icon} Fail{RESET}")
        return None


async def check_proxies(proxies, concurrent=20):
    # Giới hạn số kết nối đồng thời
    sem = asyncio.Semaphore(concurrent)
    # Giới hạn thời gian kết nối
    timeout = aiohttp.ClientTimeout(total=10)

    async with aiohttp.ClientSession() as session:
        tasks = [_check_proxy(session, proxy, sem, timeout) for proxy in proxies]
        futures = await asyncio.gather(*tasks)
        working_proxies = [p for p in futures if p is not None]

    print("\n========== Proxy hoạt động ==========")
    for i, proxy in enumerate(working_proxies, start=1):
        print(f"{i:02d}. {proxy}")
    print("====================================\n")
    print(f"Tổng proxy hoạt động: {len(working_proxies)}\n")

    return working_proxies
