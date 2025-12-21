import time
import requests
import cv2
import easyocr
import pandas as pd
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# CẤU HÌNH
TARGET_URL = "https://tuyensinh.hcmus.edu.vn/thong-bao-ket-qua-trung-tuyen-chinh-thuc-vao-dai-hoc-he-chinh-quy-nam-2024/"
ORIGINAL_IMG = "hcmus_original.png"
OUTPUT_EXCEL = "Diem_Chuan_HCMUS_2024.xlsx"


# TẢI ẢNH
def download_hcmus_image():
    print(f"--- Đang truy cập HCMUS: {TARGET_URL} ---")
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get(TARGET_URL)
        time.sleep(5)
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Tìm ảnh dựa trên class hoặc link bạn cung cấp
        img_tag = soup.find('img', src=re.compile(r'PA2-MAT-SAU-P'))

        if img_tag:
            # Ưu tiên lấy link to nhất từ srcset (thường là link cuối cùng)
            srcset = img_tag.get('srcset')
            if srcset:
                img_url = [s.strip().split(' ')[0] for s in srcset.split(',')][-1]
            else:
                img_url = img_tag['src']

            print(f"--- Đang tải ảnh chất lượng cao: {img_url} ---")
            img_data = requests.get(img_url).content
            with open(ORIGINAL_IMG, 'wb') as f:
                f.write(img_data)
            return True
        return False
    finally:
        driver.quit()


# XỬ LÝ OCR VÀ TÁCH CỘT THEO TỌA ĐỘ
def process_hcmus_ocr():
    print("--- Đang khởi tạo bộ đọc AI... ---")
    reader = easyocr.Reader(['vi', 'en'])

    # Tiền xử lý ảnh nhẹ (chuyển xám) để OCR chạy nhanh hơn với ảnh lớn
    img = cv2.imread(ORIGINAL_IMG)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cv2.imwrite("hcmus_temp.png", gray)

    results = reader.readtext("hcmus_temp.png", detail=1)

    # Nhóm theo hàng ngang (Y-axis)
    results.sort(key=lambda x: x[0][0][1])
    rows = []
    curr = [results[0]]
    for i in range(1, len(results)):
        if abs(results[i][0][0][1] - curr[-1][0][0][1]) <= 20:
            curr.append(results[i])
        else:
            rows.append(curr)
            curr = [results[i]]
    rows.append(curr)

    final_data = []
    print("--- Đang phân tích cấu trúc bảng ngành... ---")
    for row in rows:
        row.sort(key=lambda x: x[0][0][0])  # Sắp xếp X (trái sang phải)

        line_text = " ".join([r[1] for r in row])

        # Nhận diện hàng chứa Mã ngành (thường là 7 chữ số như 7480101)
        if re.search(r'\d{7}', line_text):
            # Tách thủ công các phần dựa trên cấu trúc hàng
            # [Mã ngành] [Tên ngành...] [Tổ hợp] [Điểm chuẩn]
            parts = line_text.replace('O', '0').replace(',', '.').split()

            if len(parts) >= 4:
                final_data.append({
                    "Mã ngành": parts[0],
                    "Điểm chuẩn": parts[-1],
                    "Tổ hợp": parts[-2],
                    "Tên ngành đào tạo": " ".join(parts[1:-2])
                })

    return final_data


# THỰC THI
if __name__ == "__main__":
    if download_hcmus_image():
        data = process_hcmus_ocr()
        if data:
            df = pd.DataFrame(data)
            df.to_excel(OUTPUT_EXCEL, index=False)
            print(f"✅ THÀNH CÔNG: Đã cào {len(df)} ngành của ĐH KHTN lưu vào {OUTPUT_EXCEL}")
            print(df.head())