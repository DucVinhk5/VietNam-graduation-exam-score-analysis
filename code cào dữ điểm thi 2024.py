from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import pandas as pd
import time

# CẤU HÌNH 
BASE_URL = "https://diemthi.vnexpress.net/diem-thi-nam-2024/detail/sbd/{}/year/2024"

AA, BB, CCCC = 1, 0, 1      # 01 00 0001
MAX_VALID = 200              # cào 5 SBD hợp lệ
STOP_NO_DATA = 5

valid_count = 0
no_data_count = 0
results = []

# DRIVER
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 20)

print("cào\n")

#  VÒNG LẶP
while valid_count < MAX_VALID and no_data_count < STOP_NO_DATA:
    sbd_query = f"{AA:02d}{BB:02d}{CCCC:04d}"
    url = BASE_URL.format(sbd_query)
    print(f" TRA CỨU: {sbd_query}")

    driver.get(url)

    try:
        # CHỜ KHỐI THÍ SINH LOAD XONG
        row = wait.until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, "o-detail-thisinh")
            )
        )

        # ===== SỐ BÁO DANH =====
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
                mon = tds[0].text.strip()
                diem = tds[1].text.strip()
                scores[mon] = diem

        # ===== GÁN MÔN =====
        toan = scores.get("Toán", "")
        van = scores.get("Ngữ văn", "")
        ngoai_ngu = scores.get("Ngoại ngữ", "")
        vat_ly = scores.get("Vật lý", "")
        hoa_hoc = scores.get("Hóa học", "")
        sinh_hoc = scores.get("Sinh học", "")

        print(f"OK: {sbd} | {cum_thi}")

        # ===== LƯU =====
        results.append({
            "SBD": sbd,
            "Cụm thi": cum_thi,
            "Toán": toan,
            "Ngữ văn": van,
            "Ngoại ngữ": ngoai_ngu,
            "Vật lý": vat_ly,
            "Hóa học": hoa_hoc,
            "Sinh học": sinh_hoc
        })

        valid_count += 1
        no_data_count = 0
        CCCC += 1

    except TimeoutException:
        print("KHÔNG CÓ DỮ LIỆU / LOAD CHẬM")
        no_data_count += 1
        CCCC += 1

    time.sleep(2)   #  bắt buộc cho JS render

# ĐÓNG DRIVER 
driver.quit()

#  LƯU EXCEL
df = pd.DataFrame(results)
df.to_excel("diem_thi_thpt_2024.xlsx", index=False)

print("\n HOÀN TẤT")
print(" ĐÃ LƯU FILE: diem_thi_thpt_2024.xlsx")
