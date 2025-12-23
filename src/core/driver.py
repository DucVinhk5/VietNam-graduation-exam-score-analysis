from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def setup_driver():
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--incognito")  # profile mới
    opts.add_argument("--disk-cache-size=0")  # tắt cache
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-extensions")
    opts.add_argument("--disable-notifications")
    opts.add_argument("--disable-background-networking")
    opts.add_argument("--blink-settings=imagesEnabled=false")
    return webdriver.Chrome(options=opts)
