import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

TARGET_URL = "https://xaydungchinhsach.chinhphu.vn/diem-chuan-truong-dai-hoc-quoc-te-dai-hoc-quoc-gia-tphcm-nam-2023-119230822171213016.htm"
OUTPUT_EXCEL = "Diem_Chuan_IU_2023.xlsx"


def crawl_iu_table():
    print(f"--- Đang cào dữ liệu IU ---")

    # Cấu hình Chrome chạy ẩn (headless)
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get(TARGET_URL)
        time.sleep(5)  # Chờ trang tải đầy đủ

        # 1. Tìm bảng chứa điểm chuẩn (dựa trên class bạn cung cấp)
        # Nếu trang có nhiều bảng, ta tìm bảng có class 'VCCTable'
        table = driver.find_element(By.CSS_SELECTOR, "table.VCCTable")

        # 2. Lấy tất cả các hàng trong body của bảng
        rows = table.find_elements(By.TAG_NAME, "tr")

        data = []

        # Duyệt qua từng hàng (bỏ qua hàng tiêu đề nếu cần, hoặc xử lý linh hoạt)
        for row in rows:
            cols = row.find_elements(By.TAG_NAME, "td")

            # Kiểm tra xem hàng có đủ cột không (Bảng này có 5 cột)
            if len(cols) >= 5:
                # Trích xuất text từ các ô
                stt = cols[0].text.strip()
                ma_nganh = cols[1].text.strip()
                ten_nganh = cols[2].text.strip()
                to_hop = cols[3].text.strip()
                diem = cols[4].text.strip()

                # Loại bỏ hàng tiêu đề bằng cách kiểm tra nếu ma_nganh không phải là số
                if ma_nganh.isdigit() or "_" in ma_nganh:
                    data.append([stt, ten_nganh, ma_nganh, diem])
                    print(f" [+] Đã lấy: {ma_nganh} - {ten_nganh}")

        # 3. Tạo DataFrame và xuất ra Excel
        if data:
            df = pd.DataFrame(data, columns=["STT", "TÊN NGÀNH", "MÃ NGÀNH", "ĐIỂM CHUẨN"])
            df.to_excel(OUTPUT_EXCEL, index=False)
            print("-" * 30)
            print(f" THÀNH CÔNG! Đã lưu {len(df)} hàng vào file: {OUTPUT_EXCEL}")
        else:
            print(" Không tìm thấy dữ liệu trong bảng.")

    except Exception as e:
        print(f" Lỗi trong quá trình cào: {e}")
    finally:
        driver.quit()


if __name__ == "__main__":
    crawl_iu_table()