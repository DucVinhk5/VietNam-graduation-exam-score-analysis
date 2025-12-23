import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

URL = "https://huongnghiepviet.com/tuyen-sinh/diem-chuan/diem-chuan-nam-2023-qsc-truong-dai-hoc-cong-nghe-thong-tin-dhqg-tp-hcm"
OUTPUT_EXCEL = "Diem_Chuan_UIT_2023.xlsx"


def scrape_uit_2023_selenium():
    print(" Khởi động Selenium...")

    options = Options()
    options.add_argument("--headless")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    try:
        # 1. Mở trang
        driver.get(URL)
        time.sleep(3)

        # 2. Lấy bảng HTML
        table = driver.find_element(By.TAG_NAME, "table")
        rows = table.find_elements(By.TAG_NAME, "tr")

        data = []

        for row in rows[1:]:  # bỏ header
            cols = [c.text.strip() for c in row.find_elements(By.TAG_NAME, "td")]

            if len(cols) == 4:
                data.append(cols)

        # 3. DataFrame
        df = pd.DataFrame(
            data,
            columns=["STT", "TÊN NGÀNH", "MÃ NGÀNH", "ĐIỂM CHUẨN"]
        )

        # 4. Chuẩn hóa dữ liệu
        df["STT"] = df["STT"].astype(int)
        df["ĐIỂM CHUẨN"] = (
            df["ĐIỂM CHUẨN"]
            .str.replace(",", ".")
            .astype(float)
        )

        # 5. Xuất Excel
        df.to_excel(OUTPUT_EXCEL, index=False)

        print(f" HOÀN TẤT: {len(df)} ngành → {OUTPUT_EXCEL}")
        print(df)

    except Exception as e:
        print(" Lỗi:", e)

    finally:
        driver.quit()


if __name__ == "__main__":
    scrape_uit_2023_selenium()
