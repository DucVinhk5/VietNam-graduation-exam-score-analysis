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
from urllib.parse import urljoin

# CẤU HÌNH
TARGET_URL = "https://tuyensinh.uit.edu.vn/diem-chuan-cua-truong-dh-cong-nghe-thong-tin-qua-cac-nam"
BASE_URL = "https://tuyensinh.uit.edu.vn"
OUTPUT_EXCEL = "Diem_Chuan_UIT_2024.xlsx"


#TẢI ẢNH
def get_uit_image():
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get(TARGET_URL)
        time.sleep(4)
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Tìm ảnh có chứa 'diem-chuan' trong src
        img_tag = soup.find('img', src=re.compile(r'diem-chuan'))

        if img_tag:
            full_url = urljoin(BASE_URL, img_tag['src'])
            print(f"--- Đang tải ảnh UIT: {full_url} ---")
            img_data = requests.get(full_url).content
            with open("uit_table.jpg", "wb") as f:
                f.write(img_data)
            return "uit_table.jpg"
        return None
    finally:
        driver.quit()


# OCR VÀ TÁCH CỘT THEO TỶ LỆ CHIỀU NGANG (X-AXIS)
def process_uit_ocr_refined(img_path):
    reader = easyocr.Reader(['vi', 'en'])
    img = cv2.imread(img_path)
    h, w, _ = img.shape
    results = reader.readtext(img_path, detail=1)

    # Bước 1: Nhóm hàng cực kỳ khắt khe (Sai số chỉ 8-10 pixel)
    results.sort(key=lambda x: x[0][0][1])
    rows = []
    if not results: return []

    curr_row = [results[0]]
    for i in range(1, len(results)):
        if abs(results[i][0][0][1] - curr_row[-1][0][0][1]) <= 10:
            curr_row.append(results[i])
        else:
            rows.append(curr_row)
            curr_row = [results[i]]
    rows.append(curr_row)

    final_table = []
    for row in rows:
        row.sort(key=lambda x: x[0][0][0])
        # Tạo khung dữ liệu chuẩn
        entry = {"Mã ngành": "", "Tên ngành": "", "2024": "", "2023": "", "2022": "", "2021": "", "2020": ""}
        name_parts = []

        for box, text, prob in row:
            # Tính toán vị trí X tương đối (%)
            x_mid = (box[0][0] + box[1][0]) / (2 * w)
            # Dọn dẹp văn bản: Xóa chữ cái trong cột điểm, giữ lại số và dấu chấm
            clean = re.sub(r'[^0-9\.]', '', text.replace(',', '.').replace('O', '0'))

            if x_mid < 0.12:
                entry["Mã ngành"] = clean
            elif x_mid < 0.44:
                name_parts.append(text)
            elif 0.44 <= x_mid < 0.55:
                entry["2024"] = clean
            elif 0.55 <= x_mid < 0.66:
                entry["2023"] = clean
            elif 0.66 <= x_mid < 0.77:
                entry["2022"] = clean
            elif 0.77 <= x_mid < 0.88:
                entry["2021"] = clean
            else:
                entry["2020"] = clean

        entry["Tên ngành"] = " ".join(name_parts)

        # Chỉ lấy nếu là hàng dữ liệu thực (có mã ngành số)
        if re.match(r'^\d+$', entry["Mã ngành"]):
            final_table.append(entry)

    return final_table


# THỰC THI
if __name__ == "__main__":
    path = get_uit_image()
    if path:
        data = process_uit_ocr_refined(path)
        if data:
            df = pd.DataFrame(data)
            # Sắp xếp lại thứ tự cột cho đẹp
            cols = ["Mã ngành", "Tên ngành", "2024", "2023", "2022", "2021", "2020"]
            df[cols].to_excel(OUTPUT_EXCEL, index=False)
            print(f" THÀNH CÔNG: Đã lưu bảng điểm 5 năm UIT vào {OUTPUT_EXCEL}")