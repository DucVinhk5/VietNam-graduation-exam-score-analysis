import time
import pandas as pd
import requests
import easyocr
import cv2
import numpy as np
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

# --- CẤU HÌNH ---
TARGET_URL = "https://tuoitre.vn/diem-chuan-8-truong-thanh-vien-dai-hoc-quoc-gia-tp-hcm-20230822103303492.htm"
OUTPUT_EXCEL = "Diem_Chuan_KHTN_2023.xlsx"
IMAGE_URL = "https://cdn2.tuoitre.vn/471584752817336320/2023/8/22/photo-1692695521030-1692695521271947647444.jpg"


def run_scraper_khtn():
    print(f"--- Bắt đầu quy trình cào dữ liệu KHTN---")

    # 1. Khởi tạo Selenium
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get(TARGET_URL)
        time.sleep(3)
        print(" Đã kết nối tới trang web.")

        # 2. Tải ảnh mục tiêu về để xử lý OCR
        print(f" Đang tải ảnh từ: {IMAGE_URL}")
        resp = requests.get(IMAGE_URL)
        img_arr = np.asarray(bytearray(resp.content), dtype=np.uint8)
        img = cv2.imdecode(img_arr, cv2.IMREAD_COLOR)

        # 3. Chạy OCR nhận diện văn bản tiếng Việt
        print(" Đang nhận diện văn bản (OCR)...")
        reader = easyocr.Reader(['vi'])
        result = reader.readtext(img, detail=1)

        # 4. Gom nhóm dữ liệu theo tọa độ hàng (Y)
        points = []
        for (bbox, text, prob) in result:
            y_center = (bbox[0][1] + bbox[2][1]) / 2
            x_left = bbox[0][0]
            points.append({'x': x_left, 'y': y_center, 'text': text.strip()})

        df_ocr = pd.DataFrame(points).sort_values('y')

        # Ngưỡng Y = 15 pixel để xác định hàng mới
        df_ocr['row_id'] = (df_ocr['y'].diff() > 15).cumsum()

        final_rows = []
        for _, group in df_ocr.groupby('row_id'):
            group = group.sort_values('x')
            row_items = []

            # Gom các mảnh chữ trong cùng 1 ô dữ liệu theo tọa độ X
            if not group.empty:
                temp_text = group.iloc[0]['text']
                last_x = group.iloc[0]['x'] + 20
                for i in range(1, len(group)):
                    if group.iloc[i]['x'] - last_x < 40:
                        temp_text += " " + group.iloc[i]['text']
                    else:
                        row_items.append(temp_text)
                        temp_text = group.iloc[i]['text']
                    last_x = group.iloc[i]['x'] + 20
                row_items.append(temp_text)

            # --- XỬ LÝ ĐỂ LẤY ĐÚNG 4 CỘT ---
            if len(row_items) >= 3:
                # Tách số thứ tự nếu bị dính vào mã ngành (VD: "1 7440102")
                first_cell = row_items[0]
                if ' ' in first_cell and first_cell.split(' ')[0].isdigit():
                    parts = first_cell.split(' ', 1)
                    row_items = [parts[0], parts[1]] + row_items[1:]

                # Cấu trúc: STT, Mã ngành, Tên ngành, Điểm chuẩn (bỏ qua cột Tổ hợp môn)
                if len(row_items) >= 4:
                    stt = row_items[0]
                    ma_nganh = row_items[1]
                    # Ghép các ô giữa lại nếu tên ngành bị tách nhỏ
                    ten_nganh = " ".join(row_items[2:-1])
                    # Lấy cột cuối cùng bên phải làm Điểm chuẩn
                    diem_chuan = row_items[-1]

                    # Lọc bỏ các dòng tiêu đề rác của bảng
                    if ma_nganh.isdigit() or any(char.isdigit() for char in ma_nganh):
                        final_rows.append([stt, ma_nganh, ten_nganh, diem_chuan])

        # 5. Lưu vào Excel
        df_final = pd.DataFrame(final_rows, columns=["STT", "MÃ NGÀNH", "TÊN NGÀNH", "ĐIỂM CHUẨN"])
        df_final.to_excel(OUTPUT_EXCEL, index=False)

        print(f"--- THÀNH CÔNG! Đã xuất file: {OUTPUT_EXCEL} ---")
        print(df_final.head(10))

    except Exception as e:
        print(f" Lỗi: {e}")
    finally:
        driver.quit()


# Thực thi hàm
if __name__ == "__main__":
    run_scraper_khtn()