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
TARGET_URL = "https://www.uhsvnu.edu.vn/tin-tuc/diem-chuan-trung-tuyen-truong-dai-hoc-khoa-hoc-suc-khoe-nam-2024/"
ORIGINAL_IMG = "uhs_original.jpg"
PROCESSED_IMG = "uhs_enhanced.jpg"
OUTPUT_EXCEL = "Diem_Chuan_UHS_2024.xlsx"


# TẢI ẢNH

def get_image_from_uhs():
    print(f"--- Đang truy cập website: {TARGET_URL} ---")
    options = Options()
    # options.add_argument("--headless") # Ẩn trình duyệt nếu muốn
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get(TARGET_URL)
        time.sleep(5)  # Đợi trang tải ảnh

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        # Tìm ảnh dựa trên class đặc trưng của WordPress hoặc tìm ảnh có kích thước lớn
        img_tag = soup.find('img', class_='wp-image-11175')

        if not img_tag:
            # Dự phòng: tìm bất kỳ ảnh nào chứa "diem-chuan" trong link hoặc srcset
            img_tag = soup.find('img', srcset=True)

        if img_tag:
            # Ưu tiên lấy link ảnh chất lượng cao nhất từ srcset
            srcset = img_tag.get('srcset')
            if srcset:
                links = [s.strip().split(' ')[0] for s in srcset.split(',')]
                img_url = links[-1]  # Lấy link cuối cùng (thường là ảnh to nhất)
            else:
                img_url = img_tag['src']

            print(f"--- Đã tìm thấy link ảnh chất lượng cao: {img_url} ---")
            img_data = requests.get(img_url).content
            with open(ORIGINAL_IMG, 'wb') as f:
                f.write(img_data)
            return True
        else:
            print(" Không tìm thấy ảnh bảng điểm trên trang web này.")
            return False
    finally:
        driver.quit()



# TIỀN XỬ LÝ ẢNH

def preprocess_for_ocr(path):
    print("--- Đang xử lý ảnh để AI đọc rõ hơn... ---")
    img = cv2.imread(path)
    # Chuyển xám và tăng độ tương phản
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Khử nhiễu và nhị phân hóa (Otsu Thresholding)
    processed = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    cv2.imwrite(PROCESSED_IMG, processed)
    return PROCESSED_IMG



# OCR và NẮN DÒNG DỮ LIỆU

def process_ocr_to_table(img_path):
    print("--- Đang chạy OCR nhận diện chữ... ---")
    reader = easyocr.Reader(['vi', 'en'])
    # detail=1 để lấy tọa độ xử lý hàng ngang
    results = reader.readtext(img_path, detail=1)

    if not results: return None

    # Nhóm các đoạn text theo tọa độ Y (hàng ngang)
    results.sort(key=lambda x: x[0][0][1])
    rows = []
    current_row = [results[0]]
    y_threshold = 25  # Tăng ngưỡng để phù hợp với ảnh chụp bảng rộng

    for i in range(1, len(results)):
        if abs(results[i][0][0][1] - current_row[-1][0][0][1]) <= y_threshold:
            current_row.append(results[i])
        else:
            rows.append(current_row)
            current_row = [results[i]]
    rows.append(current_row)

    final_data = []
    for row in rows:
        row.sort(key=lambda x: x[0][0][0])  # Sắp xếp từ trái sang phải
        texts = [r[1] for r in row]
        line = " ".join(texts)

        # Nhận diện hàng chứa Mã ngành (7 chữ số)
        if re.search(r'\d{7}', line):
            # Sửa lỗi phổ biến
            line = line.replace('O', '0').replace('o', '0').replace(',', '.')
            parts = line.split()

            if len(parts) >= 4:
                final_data.append({
                    "Mã ngành": parts[0],
                    "Điểm chuẩn": parts[-1],
                    "Tổ hợp": parts[-2],
                    "Tên ngành": " ".join(parts[1:-2])
                })
    return final_data



# THỰC THI
if __name__ == "__main__":
    if get_image_from_uhs():
        enhanced_path = preprocess_for_ocr(ORIGINAL_IMG)
        data = process_ocr_to_table(enhanced_path)

        if data:
            df = pd.DataFrame(data)
            df.to_excel(OUTPUT_EXCEL, index=False)
            print(f"\n THÀNH CÔNG! Đã lưu kết quả tại: {OUTPUT_EXCEL}")
            print(df)
        else:
            print(" OCR không trích xuất được bảng dữ liệu.")