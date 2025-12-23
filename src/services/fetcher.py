import time
from random import uniform

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config.settings import URL
from core.enums import Feedback
from logger import logger
from utils.stop import stop_event


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

            year = wait.until(
                EC.presence_of_element_located((By.ID, "year"))
            ).get_attribute("year")

            edu = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "p.edu-institution"))
            ).text

            rows = driver.find_element(By.TAG_NAME, "tbody").find_elements(
                By.TAG_NAME, "tr"
            )

            data = [
                [year, edu, sbd]
                + [td.text for td in row.find_elements(By.XPATH, "./*")]
                for row in rows
            ]

            logger.info(f"[OK] {sbd}")
            return data, Feedback.NEXT

        except Exception as e:
            logger.error(f"[Thread-{thread_id}] Retry {attempt} {sbd} - {e}")
            time.sleep(uniform(0.5, 1))

    return None, Feedback.STOP


def fetcher(thread_id, driver, gen_sbd, result_queue):
    print(f"🚀 Thread {thread_id} start")
    driver.get(URL)

    try:
        current_sbd = next(gen_sbd)
        skip_count = 0

        while not stop_event.is_set():
            data, status = fetch_data(thread_id, driver, current_sbd)

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
        result_queue.put(None)
        driver.quit()
