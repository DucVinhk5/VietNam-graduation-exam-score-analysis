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
OUTPUT_EXCEL = "Diem_Chuan_UHS_2023.xlsx"
IMAGE_ID = "img_618740352107241472"


def crawl_and_fix_ocr():
    print(f"--- Đang kết nối tới: {TARGET_URL} ---")
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get(TARGET_URL)
        time.sleep(5)
        img_element = driver.find_element(By.ID, IMAGE_ID)
        img_url = img_element.get_attribute("src")

        response = requests.get(img_url)
        img_array = np.asarray(bytearray(response.content), dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        print(" Đang chạy OCR và xử lý gom nhóm dòng...")
        reader = easyocr.Reader(['vi'])
        result = reader.readtext(img, detail=1)

        # 1. Chuyển kết quả OCR vào danh sách để xử lý tọa độ
        data_points = []
        for (bbox, text, prob) in result:
            y_center = (bbox[0][1] + bbox[2][1]) / 2
            x_left = bbox[0][0]
            data_points.append({'x': x_left, 'y': y_center, 'text': text})

        df_ocr = pd.DataFrame(data_points)

        # 2. THUẬT TOÁN GOM NHÓM DÒNG (Dựa trên sai lệch tọa độ Y)
        # Sắp xếp theo Y trước
        df_ocr = df_ocr.sort_values('y')

        # Tạo nhãn hàng (Row ID) dựa trên khoảng cách Y giữa các cụm chữ
        # Nếu khoảng cách Y giữa 2 chữ > 20 pixel thì coi là hàng mới
        df_ocr['row_id'] = (df_ocr['y'].diff() > 20).cumsum()

        # 3. GỘP CÁC CHỮ TRONG CÙNG MỘT HÀNG THEO CỘT
        rows = []
        for _, group in df_ocr.groupby('row_id'):
            # Trong mỗi hàng, sắp xếp theo X (từ trái qua phải)
            group = group.sort_values('x')

            # Gom các chữ nằm quá gần nhau theo phương ngang (x) thành 1 ô dữ liệu
            # (Ví dụ: "Y", "khoa" -> "Y khoa")
            row_items = []
            if not group.empty:
                current_text = group.iloc[0]['text']
                last_x_right = group.iloc[0]['x'] + 50  # Giả định độ rộng chữ

                for i in range(1, len(group)):
                    if group.iloc[i]['x'] - last_x_right < 40:  # Khoảng cách các từ trong 1 ô
                        current_text += " " + group.iloc[i]['text']
                    else:
                        row_items.append(current_text)
                        current_text = group.iloc[i]['text']
                    last_x_right = group.iloc[i]['x'] + 50
                row_items.append(current_text)

            if len(row_items) >= 3:  # Lọc bỏ các dòng rác (logo, text linh tinh)
                rows.append(row_items)

        return rows

    except Exception as e:
        print(f" Lỗi: {e}")
        return None
    finally:
        driver.quit()


if __name__ == "__main__":
    final_rows = crawl_and_fix_ocr()

    if final_rows:
        # Làm sạch dữ liệu để khớp 5 cột: STT, Mã ngành, Tên ngành, Mã tổ hợp, Điểm chuẩn
        processed_data = []
        for r in final_rows:
            # Nếu dòng bị dư cột do OCR đọc nhầm dấu phân cách, chỉ lấy 5 cột đầu
            if len(r) >= 5:
                processed_data.append(r[:5])
            # Nếu thiếu cột (ví dụ Mã ngành bị dính vào Tên ngành), bạn có thể xử lý thủ công tại đây
            elif len(r) == 4:
                processed_data.append(r)

        df = pd.DataFrame(processed_data)

        # Đặt tên cột
        cols = ["STT", "Mã ngành", "Tên ngành", "Mã tổ hợp", "Điểm trúng tuyển"]
        df.columns = cols[:len(df.columns)]

        df.to_excel(OUTPUT_EXCEL, index=False)
        print(f" THÀNH CÔNG! Đã xuất file: {OUTPUT_EXCEL}")
        print("-" * 30)
        print(df)
    else:
        print(" Không lấy được dữ liệu.")