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

###########################################################################################
#tổ hợp 3 môn xét tuyển
# A00, A01, D01, D07 đối với học sinh THPT thuộc khu vực 3 (không nhân hệ số) là 21 điểm.
############################################################################################
# --- CẤU HÌNH ---
TARGET_URL = "https://xaydungchinhsach.chinhphu.vn/diem-chuan-truong-dai-hoc-kinh-te-luat-dhqg-tphcm-nam-2024-11924081717344347.htm"
IMG_PATH = "uel_2024_high_res.jpg"
OUTPUT_EXCEL = "Diem_Chuan_UEL.xlsx"


#TẢI ẢNH
def download_image():
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    try:
        driver.get(TARGET_URL)
        time.sleep(5)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        img_tag = soup.find('img', class_='lightbox-content')
        if img_tag:
            # Lấy ảnh gốc để tránh bị mờ (lỗi zoom/thumbnail)
            img_url = img_tag.get('data-original') or img_tag.get('src')
            if img_url.startswith('//'): img_url = 'https:' + img_url
            print(f"--- Đã tải ảnh gốc: {img_url} ---")
            img_data = requests.get(img_url).content
            with open(IMG_PATH, 'wb') as f:
                f.write(img_data)
            return True
        return False
    finally:
        driver.quit()


# XỬ LÝ OCR VÀ TÁCH CỘT THEO CẤU TRÚC BẢNG
def extract_uel_table(img_path):
    print("--- Đang khởi tạo OCR và phân tích cấu trúc bảng... ---")
    reader = easyocr.Reader(['vi', 'en'])
    results = reader.readtext(img_path, detail=1)
    if not results: return None

    # Nhóm theo hàng ngang (Y-axis)
    results.sort(key=lambda x: x[0][0][1])
    rows = []
    curr = [results[0]]
    for i in range(1, len(results)):
        if abs(results[i][0][0][1] - curr[-1][0][0][1]) <= 15:
            curr.append(results[i])
        else:
            rows.append(curr)
            curr = [results[i]]
    rows.append(curr)

    final_table = []
    for row in rows:
        row.sort(key=lambda x: x[0][0][0])  # Sắp xếp từ trái sang phải

        # Biến tạm cho từng cột
        stt, ma_nganh, diem = "", "", ""
        ten_nganh_parts = []

        for box, text, prob in row:
            x_pos = box[0][0]  # Vị trí ngang
            clean_text = text.replace('O', '0').replace('o', '0').replace(',', '.')

            # Tách cột dựa trên vị trí X (tọa độ ngang) của bảng UEL
            if x_pos < 80:  # Cột STT
                stt = clean_text
            elif 80 <= x_pos < 250 and re.match(r'^\d{7}$', clean_text):  # Cột Mã ngành
                ma_nganh = clean_text
            elif x_pos > 700:  # Cột Điểm chuẩn (phía bên phải cùng)
                if re.search(r'\d', clean_text): diem = clean_text
            else:  # Các phần ở giữa là Tên chương trình đào tạo
                if clean_text.strip(): ten_nganh_parts.append(text)

        # Chỉ lưu nếu hàng đó có Mã ngành hoặc Điểm chuẩn hợp lệ
        if ma_nganh or (diem and len(ten_nganh_parts) > 0):
            final_table.append({
                "STT": stt,
                "Mã ngành": ma_nganh,
                "Tên chương trình đào tạo": " ".join(ten_nganh_parts),
                "Điểm chuẩn": diem
            })
    return final_table


# THỰC THI
if __name__ == "__main__":
    if download_image():
        data = extract_uel_table(IMG_PATH)
        if data:
            df = pd.DataFrame(data)
            # Dọn dẹp: Xóa các hàng tiêu đề bị lẫn vào
            df = df[df['Điểm chuẩn'].str.contains(r'\d', na=False)]
            df.to_excel(OUTPUT_EXCEL, index=False)
            print(f" HOÀN THÀNH: Đã lưu bảng điểm chuẩn vào {OUTPUT_EXCEL}")
            print(df.head(10))