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

TARGET_URL = "https://xaydungchinhsach.chinhphu.vn/diem-chuan-truong-dai-hoc-bach-khoa-dhqg-tphcm-2023-119230823002223459.htm"
OUTPUT_EXCEL = "Diem_Chuan_BachKhoa_2023.xlsx"
IMAGE_URL_BK = "https://xdcs.cdnchinhphu.vn/446259493575335936/2023/8/23/bk2-1692724056619604185755.jpg"


def run_scraper_bachkhoa_fixed_v2():
    print(f"--- Đang thực hiện cào dữ liệu Bách khoa ---")
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get(TARGET_URL)
        time.sleep(3)

        resp = requests.get(IMAGE_URL_BK)
        img_arr = np.asarray(bytearray(resp.content), dtype=np.uint8)
        img = cv2.imdecode(img_arr, cv2.IMREAD_COLOR)

        reader = easyocr.Reader(['vi', 'en'])
        result = reader.readtext(img, detail=1)

        # Lưu tất cả các mảnh text kèm tọa độ
        all_elements = []
        for (bbox, text, prob) in result:
            all_elements.append({
                'x': bbox[0][0],
                'y': (bbox[0][1] + bbox[2][1]) / 2,
                'text': text.strip()
            })

        # Sắp xếp theo thứ tự từ trên xuống dưới, từ trái sang phải
        all_elements.sort(key=lambda e: (e['y'], e['x']))

        final_rows = []
        current_entry = None

        for el in all_elements:
            txt = el['text']
            # Kiểm tra nếu là Mã ngành (3 chữ số ở lề trái)
            if re.match(r'^\d{3}$', txt) and el['x'] < img.shape[1] * 0.2:
                if current_entry:
                    final_rows.append(current_entry)
                current_entry = {"ma": txt, "rest": []}
            else:
                if current_entry:
                    current_entry["rest"].append(txt)

        # Thêm mục cuối cùng
        if current_entry:
            final_rows.append(current_entry)

        # Xử lý phần "rest" để tách Tên và Điểm
        processed_data = []
        for entry in final_rows:
            full_rest = " ".join(entry["rest"])

            # Regex tìm điểm chuẩn: số thập phân hoặc số nguyên ở cuối chuỗi
            # Điểm của BK 2023 thường có dạng như 54.00 hoặc 73.51
            score_match = re.findall(r'(\d+\.\d{2}|\d+\,\d{2}|\d{2,3})', full_rest)

            if score_match:
                diem = score_match[-1]
                # Tên ngành là phần còn lại sau khi bỏ điểm
                ten = full_rest.replace(diem, "").strip()
                # Làm sạch các ký tự nhiễu
                ten = re.sub(r'^[^\w]+|[^\w]+$', '', ten).strip()
                processed_data.append([entry["ma"], ten, diem])
            else:
                processed_data.append([entry["ma"], full_rest, ""])

        # Xuất file
        df = pd.DataFrame(processed_data, columns=["MÃ NGÀNH", "TÊN NGÀNH", "ĐIỂM CHUẨN"])

        # Hậu xử lý: Nếu tên ngành bị trống, có thể do OCR gộp điểm vào mã
        df = df[df['MÃ NGÀNH'].str.len() == 3]

        df.to_excel(OUTPUT_EXCEL, index=False)
        print(f"--- THÀNH CÔNG! Đã xuất {len(df)} hàng vào {OUTPUT_EXCEL} ---")
        print(df.tail(5))  # Kiểm tra ngành cuối

    except Exception as e:
        print(f" Lỗi: {e}")
    finally:
        driver.quit()


if __name__ == "__main__":
    run_scraper_bachkhoa_fixed_v2()