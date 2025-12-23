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

# CẤU HÌNH
TARGET_URL = "https://tuoitre.vn/diem-chuan-8-truong-thanh-vien-dai-hoc-quoc-gia-tp-hcm-20230822103303492.htm"
OUTPUT_EXCEL = "Diem_Chuan_AGU_2023.xlsx"
IMAGE_URL_AGU = "https://cdn2.tuoitre.vn/471584752817336320/2023/8/23/photo-1692757438723-16927574387891089281359.jpg"


def fix_ocr_text(text):
    replacements = {'AOO': 'A00', 'AOl': 'A01', 'COO': 'C00', 'DOl': 'D01', 'D0l': 'D01'}
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text


def crawl_and_ocr_fixed():
    print(f"--- Đang cào dữ liệu: {TARGET_URL} ---")
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get(TARGET_URL)
        time.sleep(5)

        # Tải ảnh
        response = requests.get(IMAGE_URL_AGU)
        img_array = np.asarray(bytearray(response.content), dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        print(" Đang chạy OCR và căn chỉnh cột...")
        reader = easyocr.Reader(['vi'])
        result = reader.readtext(img, detail=1)

        data_points = []
        for (bbox, text, prob) in result:
            y_center = (bbox[0][1] + bbox[2][1]) / 2
            x_left = bbox[0][0]
            data_points.append({'x': x_left, 'y': y_center, 'text': fix_ocr_text(text)})

        df_ocr = pd.DataFrame(data_points).sort_values('y')

        # Nhóm dòng: Giảm ngưỡng Y xuống 12 để tách các dòng sát nhau tốt hơn
        df_ocr['row_id'] = (df_ocr['y'].diff() > 12).cumsum()

        final_rows = []
        for _, group in df_ocr.groupby('row_id'):
            group = group.sort_values('x')

            # Logic tách cột dựa trên khoảng cách X (ngưỡng 30 thay vì 50 để tách STT/Mã ngành)
            row_items = []
            if not group.empty:
                current_text = group.iloc[0]['text']
                last_x_right = group.iloc[0]['x'] + 20

                for i in range(1, len(group)):
                    # Nếu khoảng cách ngang > 30 pixel, coi là cột mới
                    if group.iloc[i]['x'] - last_x_right < 30:
                        current_text += " " + group.iloc[i]['text']
                    else:
                        row_items.append(current_text)
                        current_text = group.iloc[i]['text']
                    last_x_right = group.iloc[i]['x'] + 20
                row_items.append(current_text)

            # Chỉ lấy các dòng có từ 3 phần tử trở lên
            if len(row_items) >= 3:
                # Nếu hàng chỉ có 4 cột, có thể STT và Mã Ngành bị dính, ta tìm cách tách thủ công
                if len(row_items) == 4 and row_items[0].isdigit() == False:
                    first_cell = row_items[0].split(' ', 1)
                    if len(first_cell) == 2:
                        row_items = [first_cell[0], first_cell[1]] + row_items[1:]

                final_rows.append(row_items)

        return final_rows

    except Exception as e:
        print(f" Lỗi: {e}")
        return None
    finally:
        driver.quit()


if __name__ == "__main__":
    results = crawl_and_ocr_fixed()

    if results:
        df = pd.DataFrame(results)

        # Đảm bảo có đủ 5 cột theo yêu cầu
        headers = ["STT", "MÃ NGÀNH", "TÊN NGÀNH", "TỔ HỢP MÔN XÉT TUYỂN", "ĐIỂM CHUẨN"]

        # Nếu OCR đọc dư cột (do khoảng trắng lớn), ta gộp hoặc cắt
        if df.shape[1] > 5:
            df = df.iloc[:, :5]

        # Gán header (xử lý linh hoạt nếu dòng nào thiếu cột)
        df.columns = headers[:df.shape[1]]

        # Lưu file
        df.to_excel(OUTPUT_EXCEL, index=False)
        print(f" THÀNH CÔNG! Đã lưu: {OUTPUT_EXCEL}")
        print(df.head(10))
    else:
        print(" Không lấy được dữ liệu.")