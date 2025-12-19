from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import pandas as pd
import time
import os
import sys

# ================= CONFIG =================
BASE_URL = "https://diemthi.vnexpress.net/diem-thi-nam-2024/detail/sbd/{}/year/2024"

AA = 1        # mã tỉnh
BB = 0        # mã cụm
CCCC = 1      # số báo danh

MAX_VALID = 20000          # số SBD hợp lệ cần cào
STOP_NO_DATA = 10          # dừng nếu liên tiếp không có dữ liệu

EXCEL_FILE = "diem_thi_THPTQG_2024.xlsx"
PROGRESS_FILE = "progress.txt"

# ================= LOAD TIẾN TRÌNH =================
if os.path.exists(PROGRESS_FILE):
    with open(PROGRESS_FILE, "r") as f:
        CCCC = int(f.read().strip())
    print(f"▶️ TIẾP TỤC TỪ CCCC = {CCCC}")
else:
    print("▶️ BẮT ĐẦU MỚI")

if os.path.exists(EXCEL_FILE):
    df_old = pd.read_excel(EXCEL_FILE)
    results = df_old.to_dict("records")
    valid_count = len(results)
    print(f"▶️ ĐÃ CÓ {valid_count} DÒNG ĐÃ CÀO")
else:
    results = []
    valid_count = 0

no_data_count = 0

# ================= DRIVER =================
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 20)

print("\n🚀 BẮT ĐẦU CÀO\n")

# ================= MAIN LOOP =================
try:
    while valid_count < MAX_VALID and no_data_count < STOP_NO_DATA:
        sbd_query = f"{AA:02d}{BB:02d}{CCCC:04d}"
        url = BASE_URL.format(sbd_query)

        print(f"🔍 TRA CỨU: {sbd_query}")
        driver.get(url)

        try:
            row = wait.until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, "o-detail-thisinh")
                )
            )

            # ===== SBD =====
            sbd = row.find_element(
                By.CSS_SELECTOR,
                "h2.o-detail-thisinh__sbd strong"
            ).text.strip()

            # ===== CỤM THI =====
            cum_thi = row.find_element(
                By.CLASS_NAME,
                "o-detail-thisinh__cumthi"
            ).text.replace("Cụm thi:", "").strip()

            # ===== ĐIỂM =====
            scores = {}
            trs = row.find_elements(
                By.CSS_SELECTOR,
                ".o-detail-thisinh__diemthi tbody tr"
            )

            for tr in trs:
                tds = tr.find_elements(By.TAG_NAME, "td")
                if len(tds) == 2:
                    scores[tds[0].text.strip()] = tds[1].text.strip()

            record = {
                "SBD": sbd,
                "Cụm thi": cum_thi,
                "Toán": scores.get("Toán", ""),
                "Ngữ văn": scores.get("Ngữ văn", ""),
                "Ngoại ngữ": scores.get("Ngoại ngữ", ""),
                "Vật lý": scores.get("Vật lý", ""),
                "Hóa học": scores.get("Hóa học", ""),
                "Sinh học": scores.get("Sinh học", ""),
                "Lịch sử": scores.get("Lịch sử", ""),
                "Địa lý": scores.get("Địa lý", ""),
                "Giáo dục công dân": scores.get("Giáo dục công dân", "")

            }

            results.append(record)
            valid_count += 1
            no_data_count = 0

            print(f"✅ OK ({valid_count}): {sbd}")

            # ===== LƯU NGAY =====
            pd.DataFrame(results).to_excel(EXCEL_FILE, index=False)
            with open(PROGRESS_FILE, "w") as f:
                f.write(str(CCCC))

        except TimeoutException:
            print("❌ KHÔNG CÓ DỮ LIỆU")
            no_data_count += 1

            with open(PROGRESS_FILE, "w") as f:
                f.write(str(CCCC))

        CCCC += 1
        time.sleep(1.5)

except KeyboardInterrupt:
    print("\n⛔ DỪNG BẰNG CTRL + C (AN TOÀN)")

finally:
    driver.quit()
    pd.DataFrame(results).to_excel(EXCEL_FILE, index=False)
    with open(PROGRESS_FILE, "w") as f:
        f.write(str(CCCC))

    print("\n📁 ĐÃ LƯU DỮ LIỆU")
    print(f"➡ File: {EXCEL_FILE}")
    print(f"➡ Tiếp tục từ CCCC = {CCCC}")
