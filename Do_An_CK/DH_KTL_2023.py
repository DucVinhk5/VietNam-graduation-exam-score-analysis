import time
import pandas as pd
import requests
import easyocr
import cv2
import numpy as np
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# CẤU HÌNH
TARGET_URL = "https://tuoitre.vn/diem-chuan-8-truong-thanh-vien-dai-hoc-quoc-gia-tp-hcm-20230822103303492.htm"
OUTPUT_EXCEL = "Diem_Chuan_UEL_2023_Final.xlsx"
IMAGE_URL_UEL = "https://cdn2.tuoitre.vn/471584752817336320/2023/8/22/dh-kinh-te-luat-1692692840641872831206.png"


def run_scraper_uel():
    print(f"--- Đang kết nối và cào dữ liệu ĐH Kinh tế - Luật ---")
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get(TARGET_URL)
        time.sleep(3)
        print(" Đã kết nối tới bài báo bằng Selenium.")

        # 2. Tải ảnh trực tiếp để xử lý OCR chất lượng cao
        resp = requests.get(IMAGE_URL_UEL)
        img_arr = np.asarray(bytearray(resp.content), dtype=np.uint8)
        img = cv2.imdecode(img_arr, cv2.IMREAD_COLOR)

        # 3. OCR nhận diện văn bản Tiếng Việt
        print(" Đang chạy OCR nhận diện dữ liệu...")
        reader = easyocr.Reader(['vi'])
        result = reader.readtext(img, detail=1)

        # Gom nhóm các mảnh chữ theo tọa độ Y (hàng)
        points = []
        for (bbox, text, prob) in result:
            y_center = (bbox[0][1] + bbox[2][1]) / 2
            x_left = bbox[0][0]
            points.append({'x': x_left, 'y': y_center, 'text': text.strip()})

        df_ocr = pd.DataFrame(points).sort_values('y')
        # Ngưỡng Y = 12 pixel để tách các hàng sát nhau
        df_ocr['row_id'] = (df_ocr['y'].diff() > 12).cumsum()

        final_rows = []
        for _, group in df_ocr.groupby('row_id'):
            group = group.sort_values('x')
            # Gộp toàn bộ văn bản trong 1 hàng để xử lý bằng Regex
            full_text = " ".join(group['text'].tolist())

            # Mã ngành UEL có dạng 7 chữ số, đôi khi kèm theo gạch dưới và mã chương trình (vd: 7340101_201)
            ma_match = re.search(r'(\d{7}_\d{3}|\d{7})', full_text)

            if ma_match:
                ma_nganh = ma_match.group(1)

                # Tìm Điểm chuẩn (con số ở cuối dòng, giữ nguyên dấu phẩy)
                diem_match = re.findall(r'(\d+[\.,]\d+|\d+)$', full_text)
                diem_chuan = diem_match[-1] if diem_match else ""

                # Tìm STT (con số ở đầu dòng)
                stt_match = re.match(r'^(\d+)', full_text)
                stt = stt_match.group(1) if stt_match else ""

                # Tên ngành là phần nằm giữa Mã ngành và Điểm chuẩn
                parts = full_text.split(ma_nganh)
                after_ma = parts[1].strip() if len(parts) > 1 else ""

                # Loại bỏ Điểm chuẩn khỏi chuỗi để lấy Tên ngành sạch
                ten_nganh_raw = after_ma.replace(diem_chuan, "").strip()

                # Loại bỏ mã tổ hợp (A00, A01...) nếu còn sót
                ten_nganh = re.sub(r'\b[A-D]\d{2}\b', '', ten_nganh_raw).strip()
                ten_nganh = ten_nganh.strip('- ').strip()

                if ten_nganh and ma_nganh:
                    # THỨ TỰ CỘT YÊU CẦU: STT -> TÊN NGÀNH -> MÃ NGÀNH -> ĐIỂM CHUẨN
                    final_rows.append([stt, ten_nganh, ma_nganh, diem_chuan])

        # 4. Xuất file Excel 4 cột
        if final_rows:
            df_final = pd.DataFrame(final_rows, columns=["STT", "TÊN NGÀNH", "MÃ NGÀNH", "ĐIỂM CHUẨN"])
            df_final.to_excel(OUTPUT_EXCEL, index=False)
            print(f"--- THÀNH CÔNG! Đã lưu {len(df_final)} hàng vào: {OUTPUT_EXCEL} ---")
            print(df_final.head(10))
        else:
            print(" Không tìm thấy dữ liệu phù hợp trong ảnh.")

    except Exception as e:
        print(f" Lỗi hệ thống: {e}")
    finally:
        driver.quit()


if __name__ == "__main__":
    run_scraper_uel()