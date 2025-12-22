import time
import requests
import cv2
import easyocr
import pandas as pd
import re
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urljoin

# CẤU HÌNH
TARGET_URL = "https://hcmut.edu.vn/tintuc/Cong-bo-diem-chuan-cua-phuong-thuc-xet-tuyen-tong-hop-nam-2024"
BASE_URL = "https://hcmut.edu.vn"
OUTPUT_EXCEL = "Diem_Chuan_BachKhoa_2024.xlsx"


# TẢI ẢNH
def get_images():
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    downloaded = []
    try:
        driver.get(TARGET_URL)
        time.sleep(5)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        img_tags = soup.find_all('img', src=re.compile(r'/img/news/'))
        for i, img in enumerate(img_tags):
            full_url = urljoin(BASE_URL, img['src'])
            data = requests.get(full_url).content
            fname = f"bk_part_{i}.png"
            with open(fname, 'wb') as f: f.write(data)
            downloaded.append(fname)
        return downloaded
    finally:
        driver.quit()


# OCR VÀ XỬ LÝ TÁCH CỘT
def process_ocr_with_columns(file_list):
    reader = easyocr.Reader(['vi', 'en'])
    final_table_data = []

    for file in file_list:
        print(f"--- Đang xử lý tách cột file: {file} ---")
        # detail=1 để lấy tọa độ [x, y]
        results = reader.readtext(file, detail=1)
        if not results: continue

        # Bước A: Nhóm theo hàng (trục Y)
        results.sort(key=lambda x: x[0][0][1])
        rows = []
        curr_row = [results[0]]
        for i in range(1, len(results)):
            if abs(results[i][0][0][1] - curr_row[-1][0][0][1]) <= 15:
                curr_row.append(results[i])
            else:
                rows.append(curr_row)
                curr_row = [results[i]]
        rows.append(curr_row)

        # Bước B: Tách cột dựa trên tọa độ X trong mỗi hàng
        for row in rows:
            # Sắp xếp từ trái sang phải
            row.sort(key=lambda x: x[0][0][0])

            # Khởi tạo các biến cột
            ma_nganh = ""
            ten_nganh = []
            diem_chuan = ""

            # Logic:
            # - Mã ngành thường nằm bên trái cùng (X nhỏ)
            # - Điểm chuẩn thường nằm bên phải cùng (X lớn)
            # - Tên ngành nằm ở giữa
            for item in row:
                box, text, prob = item
                x_pos = box[0][0]  # Tọa độ X của góc trên bên trái

                # Sửa lỗi chữ O thành số 0
                text_clean = text.replace('O', '0').replace('o', '0').replace(',', '.')

                if x_pos < 150 and re.match(r'^\d+$', text_clean):  # Cột Mã ngành
                    ma_nganh = text_clean
                elif x_pos > 550:  # Cột Điểm chuẩn (Giả định bảng rộng 800-1000px)
                    if re.search(r'\d', text_clean):
                        diem_chuan = text_clean
                else:  # Còn lại là Tên ngành
                    ten_nganh.append(text_clean)

            # Chỉ lưu nếu có Mã ngành hoặc Điểm chuẩn để loại bỏ tiêu đề rác
            if ma_nganh or diem_chuan:
                final_table_data.append({
                    "Mã ngành": ma_nganh,
                    "Tên ngành": " ".join(ten_nganh),
                    "Điểm chuẩn": diem_chuan
                })

    return final_table_data


# THỰC THI
if __name__ == "__main__":
    imgs = get_images()
    if imgs:
        data = process_ocr_with_columns(imgs)
        df = pd.DataFrame(data)
        # Loại bỏ các dòng rỗng hoặc nhiễu
        df = df[df['Điểm chuẩn'] != ""]
        df.to_excel(OUTPUT_EXCEL, index=False)
        print(f"--- THÀNH CÔNG: Dữ liệu đã được tách cột tại {OUTPUT_EXCEL} ---")