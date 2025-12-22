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

# CẤU HÌNH
TARGET_URL = "https://xaydungchinhsach.chinhphu.vn/diem-chuan-truong-dai-hoc-an-giang-dhqg-tphcm-2024-119240819085941492.htm"
IMG_NAME = "agu_phan_2_chuan.jpg"
OUTPUT_FILE = "Diem_Chuan_AGU_2024.xlsx"


def download_image():
    print("--- Đang truy cập để lấy ảnh gốc số 2... ---")
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    try:
        driver.get(TARGET_URL)
        time.sleep(5)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        # Tìm chính xác ảnh số 2 (Ảnh chứa danh sách từ STT 22)
        img_tags = soup.find_all('img', class_='lightbox-content')
        if len(img_tags) >= 2:
            img_url = img_tags[1].get('data-original') or img_tags[1].get('src')
            if img_url.startswith('//'): img_url = 'https:' + img_url
            print(f"--- Đã tải link ảnh gốc: {img_url} ---")
            img_data = requests.get(img_url, headers={'User-Agent': 'Mozilla/5.0'}).content
            with open(IMG_NAME, 'wb') as f:
                f.write(img_data)
            return True
        return False
    finally:
        driver.quit()


def process_ocr_agu_refined():
    print("--- Đang khởi tạo AI nhận diện văn bản (CPU Mode)... ---")
    reader = easyocr.Reader(['vi', 'en'])

    img = cv2.imread(IMG_NAME)
    if img is None: return None
    h, w, _ = img.shape

    # Tiền xử lý: Chuyển xám và khử nhiễu nhẹ để giữ nét chữ
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    processed = cv2.bilateralFilter(gray, 9, 75, 75)
    cv2.imwrite("debug_agu.jpg", processed)

    results = reader.readtext("debug_agu.jpg", detail=1)
    if not results: return None

    # Nhóm hàng theo trục Y (Ngưỡng 20 pixel)
    results.sort(key=lambda x: x[0][0][1])
    rows = []
    curr_row = [results[0]]
    for i in range(1, len(results)):
        if abs(results[i][0][0][1] - curr_row[-1][0][0][1]) <= 20:
            curr_row.append(results[i])
        else:
            rows.append(curr_row)
            curr_row = [results[i]]
    rows.append(curr_row)

    final_data = []
    for row in rows:
        row.sort(key=lambda x: x[0][0][0])  # Sắp xếp từ trái sang phải

        item = {"STT": "", "Mã ngành": "", "Tên ngành": "", "Tổ hợp": "", "Điểm chuẩn": ""}
        name_parts = []
        to_hop_parts = []

        for (bbox, text, prob) in row:
            # Tính vị trí X tương đối (%)
            x_center = (bbox[0][0] + bbox[1][0]) / (2 * w)
            clean_text = text.replace('O', '0').replace('o', '0').replace(',', '.')

            # PHÂN VÙNG CỘT CHUẨN CHO AGU (STT | Mã | Tên | Tổ hợp | Điểm)
            if x_center < 0.08:
                item["STT"] = clean_text
            elif 0.08 <= x_center < 0.22:
                # Mã ngành thường là 7 chữ số
                if re.search(r'\d{5,7}', clean_text): item["Mã ngành"] = clean_text
            elif 0.22 <= x_center < 0.65:
                name_parts.append(text)
            elif 0.65 <= x_center < 0.85:
                to_hop_parts.append(text)
            elif x_center >= 0.85:
                # Điểm chuẩn AGU nằm trong khoảng 15-26
                if re.search(r'\d', clean_text): item["Điểm chuẩn"] = clean_text

        item["Tên ngành"] = " ".join(name_parts).strip()
        item["Tổ hợp"] = " ".join(to_hop_parts).strip()

        # Chỉ lấy hàng có Mã ngành bắt đầu bằng 7 và có tên ngành
        if re.match(r'^7', str(item["Mã ngành"])) and len(item["Tên ngành"]) > 5:
            # Làm sạch điểm chuẩn
            item["Điểm chuẩn"] = re.sub(r'[^0-9.]', '', item["Điểm chuẩn"])
            final_data.append(item)

    return final_data


if __name__ == "__main__":
    if download_image():
        data = process_ocr_agu_refined()
        if data:
            df = pd.DataFrame(data)
            df.to_excel(OUTPUT_FILE, index=False)
            print(f" THÀNH CÔNG! Đã lưu {len(df)} ngành học vào {OUTPUT_FILE}")
            print(df.head())
        else:
            print(" OCR không lấy được dữ liệu. Kiểm tra file debug_agu.jpg.")