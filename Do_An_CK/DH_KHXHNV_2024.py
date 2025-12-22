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
TARGET_URL = "https://hcmussh.edu.vn/tin-tuc/cong-bo-diem-chuan-trung-tuyen-bang-ket-qua-thi-tot-nghiep-thpt-2024"
BASE_URL = "https://hcmussh.edu.vn"
OUTPUT_EXCEL = "Diem_Chuan_HCMUSSH_2024.xlsx"


# TẢI ẢNH
def get_hcmussh_images():
    print("--- Đang kết nối tới HCMUSSH... ---")
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    downloaded_files = []
    try:
        driver.get(TARGET_URL)
        time.sleep(5)
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Tìm tất cả ảnh trong nội dung bài viết
        img_tags = soup.find_all('img', src=re.compile(r'/img/news/'))

        # Chỉ lấy 3 hình tiếp theo sau hình giới thiệu
        # (Bắt đầu từ index 1 đến 4)
        target_imgs = img_tags[1:4]

        for i, img in enumerate(target_imgs):
            full_url = urljoin(BASE_URL, img['src'])
            print(f"--- Đang tải bảng điểm phần {i + 1}: {full_url} ---")
            img_data = requests.get(full_url).content
            file_name = f"ussh_part_{i}.png"
            with open(file_name, 'wb') as f:
                f.write(img_data)
            downloaded_files.append(file_name)
        return downloaded_files
    finally:
        driver.quit()


# XỬ LÝ OCR TÁCH CỘT THEO CẤU TRÚC USSH
def process_ussh_ocr(file_list):
    reader = easyocr.Reader(['vi', 'en'])
    all_data = []

    for file in file_list:
        print(f"--- Đang đọc dữ liệu từ: {file} ---")
        results = reader.readtext(file, detail=1)
        if not results: continue

        # Nhóm theo hàng (Y-axis)
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

        for row in rows:
            row.sort(key=lambda x: x[0][0][0])
            line = " ".join([r[1] for r in row])
            line = line.replace('O', '0').replace('o', '0').replace(',', '.')

            # Regex tìm Mã ngành (7 chữ số) và Điểm chuẩn (số thập phân)
            ma_match = re.search(r'7\d{6}', line)
            diem_match = re.findall(r'\d{1,2}\.\d{1,2}', line)

            if ma_match and diem_match:
                ma_nganh = ma_match.group()
                diem_chuan = diem_match[-1]

                # Cấu trúc USSH: [STT] [Tên ngành] [Mã ngành] [Tổ hợp] [Điểm]
                # Ta bóc tách Tên ngành dựa trên vị trí Mã ngành
                parts = line.split(ma_nganh)
                ten_nganh = parts[0].strip()
                # Loại bỏ STT ở đầu tên ngành nếu có
                ten_nganh = re.sub(r'^\d+\s+', '', ten_nganh)

                to_hop = parts[1].replace(diem_chuan, '').strip()

                all_data.append({
                    "Tên ngành": ten_nganh,
                    "Mã ngành": ma_nganh,
                    "Tổ hợp xét tuyển": to_hop,
                    "Điểm chuẩn": diem_chuan
                })
    return all_data


# THỰC THI
if __name__ == "__main__":
    imgs = get_hcmussh_images()
    if imgs:
        final_table = process_ussh_ocr(imgs)
        df = pd.DataFrame(final_table)
        df.to_excel(OUTPUT_EXCEL, index=False)
        print(f" HOÀN THÀNH! Đã trích xuất {len(df)} ngành vào {OUTPUT_EXCEL}")