import threading
import time
from random import uniform
from enum import Enum, auto
from queue import Queue
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from logger import logger
import csv

URL = "https://vietnamnet.vn/giao-duc/diem-thi/tra-cuu-diem-thi-tot-nghiep-thpt"
NUM_TINH = 64
stop_event = threading.Event()

# ================= ENUM =================
class Feedback(Enum):
    STOP = auto()
    SKIP = auto()
    NEXT = auto()

# ================= SBD =================
def format_sbd(tinh, cum, so):
    return f"{tinh:02d}{cum:02d}{so:04d}"

def sbd_generator(start_tinh, end_tinh):
    for tinh in range(start_tinh, end_tinh + 1):
        skip_tinh = False
        for cum in range(20):
            for so in range(10000):
                feedback = yield format_sbd(tinh, cum, so)
                if feedback is Feedback.STOP:
                    return
                elif feedback is Feedback.SKIP:
                    skip_tinh = True
                    break
            if skip_tinh:
                break

# ================= DRIVER =================
def setup_driver():
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-extensions")
    opts.add_argument("--disable-notifications")
    opts.add_argument("--disable-background-networking")
    opts.add_argument("--blink-settings=imagesEnabled=false")
    return webdriver.Chrome(options=opts)

# ================= FETCH =================
def fetch_data(thread_id, driver, sbd, retry=3):
    for attempt in range(1, retry + 1):
        try:
            wait = WebDriverWait(driver, 5)
            search_input = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input.input-search"))
            )
            search_button = driver.find_element(By.CSS_SELECTOR, "button.btn-submit")

            search_input.clear()
            search_input.send_keys(sbd)
            search_button.submit()
            time.sleep(uniform(0.3, 0.6))
            
            popup = driver.find_elements(By.CSS_SELECTOR, "img.close__popupMessage")
            if popup:
                popup[0].click()
                logger.warning(f"[SKIP] {sbd}")
                return None, Feedback.SKIP
            
            # đợi year
            year_elem = wait.until(EC.presence_of_element_located((By.ID, "year")))
            year = year_elem.get_attribute("year")

            # đợi edu
            edu_elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "p.edu-institution")))
            edu = edu_elem.text

            tbody = driver.find_element(By.TAG_NAME, "tbody")
            rows = tbody.find_elements(By.TAG_NAME, "tr")
            data = [
                [year, edu, sbd] + [td.text for td in row.find_elements(By.XPATH, "./*")]
                for row in rows
            ]

            logger.info(f"[OK] {sbd}")
            return data, Feedback.NEXT

        except Exception as e:
            logger.error(f"[Thread-{thread_id}] [Retry {attempt}/{retry}] {sbd} - {e}")
            time.sleep(uniform(0.5, 1))

    return None, Feedback.STOP

# ================= FETCHER =================
def fetcher(thread_id, driver, gen_sbd, result_queue):
    print(f"🚀 Thread {thread_id:02d} đã được khởi động")  # thông báo khởi động
    driver.get(URL)
    try:
        current_sbd = next(gen_sbd)
        skip_count = 0
        while not stop_event.is_set():
            data, status = fetch_data(thread_id, driver, current_sbd)

            if status is Feedback.NEXT:
                skip_count = 0
                
            if status is Feedback.SKIP:
                skip_count += 1
                status = Feedback.NEXT
            
            if skip_count >= 3:
                status = Feedback.SKIP
                
            current_sbd = gen_sbd.send(status)
            if data:
                result_queue.put(data)
    except StopIteration:
        logger.info(f"[Fetcher-{thread_id}] DONE")
    finally:
        # gửi sentinel báo thread kết thúc
        result_queue.put(None)
        driver.quit()

# ================= SAVER =================
def saver(result_queue, num_fetcher, output_file="results.csv"):
    finished = 0
    first_write = True  # để ghi header CSV lần đầu

    while finished < num_fetcher:
        item = result_queue.get()
        if item is None:
            finished += 1
            continue

        # Ghi dữ liệu vào CSV
        with open(output_file, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            
            if first_write:
                # ghi header từ keys nếu có hoặc tự đặt
                header = ["Year", "Edu", "SBD", "Subject", "Score"]
                writer.writerow(header)
                first_write = False
            
            for row in item:
                writer.writerow(row)
                logger.info(f"[SAVE] {row}")

def monitor_input():

    helper_text = """
HỆ THỐNG GIÁM SÁT LỆNH NGƯỜI DÙNG
---------------------------------
Y       : Dừng toàn bộ hệ thống
N       : Tiếp tục hệ thống
--help  : Hiển thị hướng dẫn này
---------------------------------
"""
    print("Monitor input đang chạy. Nhập '--help' để nhận trợ giúp.")

    while not stop_event.is_set():
        try:
            user_input = input("Nhập lệnh [Y/N]: ").strip().upper()
            
            if user_input == "Y":
                print("Lệnh dừng hệ thống được kích hoạt!")
                stop_event.set()
                break
            elif user_input == "N":
                print("Hệ thống tiếp tục hoạt động.")
            elif user_input == "--HELP":
                print(helper_text)
            else:
                print("Lệnh không hợp lệ. Nhập '--help' để được hướng dẫn.")
        
        except EOFError:
            # Trường hợp terminal bị đóng hoặc Ctrl+D
            print("\nInput bị gián đoạn, tự động dừng hệ thống.")
            stop_event.set()
            break
        except KeyboardInterrupt:
            # Ctrl+C
            print("\nKeyboardInterrupt: Dừng hệ thống ngay lập tức.")
            stop_event.set()
            break


# ================= ORCHESTRATOR =================
def orchestrator_system(num_driver):
    drivers = [setup_driver() for _ in range(num_driver)]
    result_queue = Queue(maxsize=1000)

    base = NUM_TINH // num_driver
    remainder = NUM_TINH % num_driver

    threads = []
    current = 1

    # tạo fetcher thread
    for i, driver in enumerate(drivers, 1):
        size = base + (1 if i <= remainder else 0)
        start = current
        end = current + size - 1
        current = end + 1

        gen = sbd_generator(start, end)
        t = threading.Thread(target=fetcher, args=(i, driver, gen, result_queue), daemon=True)
        t.start()
        
        threads.append(t)
    
    # tạo saver thread
    saver_thread = threading.Thread(target=saver, args=(result_queue, num_driver))
    saver_thread.start()

    stop_thread = threading.Thread(target=monitor_input, daemon=True)
    stop_thread.start()

    # chờ tất cả fetcher xong
    for t in threads:
        t.join()

    saver_thread.join()
    logger.info("🎉 HOÀN THÀNH TOÀN BỘ")

# ================= MAIN =================
if __name__ == "__main__":
    orchestrator_system(num_driver=4)
