import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# CẤU HÌNH
TARGET_URL = "https://xaydungchinhsach.chinhphu.vn/diem-chuan-truong-dai-hoc-quoc-te-dhqg-tphcm-2024-119240817204647572.htm"
OUTPUT_EXCEL = "Diem_Chuan_IU_2024.xlsx"


def crawl_iu_data_final():
    print(f"--- Đang kết nối tới: {TARGET_URL} ---")

    options = Options()
    options.add_argument("--headless")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get(TARGET_URL)
        time.sleep(3)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        table = soup.find('table', class_='VCCTable')

        if not table:
            print(" Không tìm thấy bảng dữ liệu HTML. Đang kiểm tra cấu trúc dự phòng...")
            table = soup.find('table')

        if not table:
            return None

        data = []
        rows = table.find_all('tr')

        for row in rows[1:]:
            cols = row.find_all('td')
            if len(cols) >= 4:
                stt = cols[0].get_text(strip=True)
                ma_nganh = cols[1].get_text(strip=True)
                ten_nganh = cols[2].get_text(strip=True)
                diem_raw = cols[3].get_text(strip=True)

                data.append({
                    "STT": stt,
                    "Mã ngành": ma_nganh,
                    "Tên ngành": ten_nganh,
                    "Điểm chuẩn": diem_raw
                })

        return data

    except Exception as e:
        print(f" Lỗi: {e}")
        return None
    finally:
        driver.quit()


# THỰC THI
if __name__ == "__main__":
    results = crawl_iu_data_final()

    if results:
        df = pd.DataFrame(results)

        # Lưu file Excel
        df.to_excel(OUTPUT_EXCEL, index=False)
        print(f" THÀNH CÔNG! Đã lưu {len(df)} hàng vào: {OUTPUT_EXCEL}")
        print("-" * 30)
        print(df.head(10))
    else:
        print(" Thất bại: Không lấy được dữ liệu.")