from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import re
import time


# 1. CẤU HÌNH TRƯỜNG VÀ ĐƯỜNG DẪN

# Danh sách các trường và URL tương ứng
school_urls = [
    ("ĐH Bách Khoa", "https://tuyensinh.vnuhcm.edu.vn/index.php?route=catalog/diemchuan/truong&truong_id=1"),
    ("ĐH Khoa học Xã hội và Nhân văn",
     "https://tuyensinh.vnuhcm.edu.vn/index.php?route=catalog/diemchuan/truong&truong_id=12"),
    ("ĐH Khoa học Tự nhiên", "https://tuyensinh.vnuhcm.edu.vn/index.php?route=catalog/diemchuan/truong&truong_id=11"),
    ("Trường Quốc tế", "https://tuyensinh.vnuhcm.edu.vn/index.php?route=catalog/diemchuan/truong&truong_id=6"),
    ("ĐH Kinh tế - Luật", "https://tuyensinh.vnuhcm.edu.vn/index.php?route=catalog/diemchuan/truong&truong_id=5"),
    ("ĐH Công nghệ Thông tin", "https://tuyensinh.vnuhcm.edu.vn/index.php?route=catalog/diemchuan/truong&truong_id=4"),
    ("Khoa Y (Khoa học Sức khỏe)",
     "https://tuyensinh.vnuhcm.edu.vn/index.php?route=catalog/diemchuan/truong&truong_id=9"),
    ("Phân hiệu ĐHQG-HCM tại tỉnh An Giang",
     "https://tuyensinh.vnuhcm.edu.vn/index.php?route=catalog/diemchuan/truong&truong_id=16"),
    ("Phân hiệu ĐHQG-HCM tại tỉnh Bến Tre (ID 17)",
     "https://tuyensinh.vnuhcm.edu.vn/index.php?route=catalog/diemchuan/truong&truong_id=17"),
    ("Phân hiệu ĐHQG-HCM tại tỉnh Bến Tre (ID 19)",
     "https://tuyensinh.vnuhcm.edu.vn/index.php?route=catalog/diemchuan/truong&truong_id=19"),
]

TABLE_XPATH = "/html/body/div[3]/div/div/div[2]/div[2]/div[2]/table"
all_data = []
driver = None

# Cấu hình Options cho Selenium WebDriver
options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--ignore-certificate-errors')


# 2. HÀM CÀO DỮ LIỆU CHÍNH

def scrape_school_data(school_name, url, driver):
    temp_data_rows = []

    try:
        print(f"\n[{school_name}] Đang truy cập: {url}")
        driver.get(url)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, TABLE_XPATH))
        )
        print(f"[{school_name}] Tải trang thành công. Bắt đầu trích xuất.")

        table_element = driver.find_element(By.XPATH, TABLE_XPATH)
        table_html = table_element.get_attribute('outerHTML')
        soup = BeautifulSoup(table_html, 'html.parser')
        tbody = soup.find('tbody')

        if tbody:
            rows = tbody.find_all('tr')
            for row in rows:
                cols = row.find_all('td')

                if len(cols) >= 7:
                    stt = cols[0].text.strip()
                    ten_nganh = cols[1].text.strip()

                    to_hop_mon_tags = cols[2].find_all('a')
                    to_hop_mon_list = [f"{tag.get('title')} ({tag.text.strip()})" for tag in to_hop_mon_tags]

                    chi_tieu = cols[3].text.strip()

                    diem_cot_e = cols[4].text.strip()
                    diem_cot_f = cols[5].text.strip()
                    diem_cot_g = cols[6].text.strip()

                    # Làm sạch và chuẩn hóa dữ liệu
                    diem_cot_e = re.sub(r'\s*\|', ' |', diem_cot_e).replace('\n', '').replace('\t', '')
                    diem_cot_f = re.sub(r'\s*\|', ' |', diem_cot_f).replace('\n', '').replace('\t', '')

                    # Thêm dữ liệu đã trích xuất vào danh sách
                    temp_data_rows.append({
                        'Trường': school_name,
                        'STT': stt,
                        'Ngành/Chương trình': ten_nganh,
                        'Tổ hợp môn': ', '.join(to_hop_mon_list),
                        'Chỉ tiêu': chi_tieu,

                        '2024': diem_cot_e if diem_cot_e else 'N/A',

                        '2023': diem_cot_f if diem_cot_f else 'N/A',

                        '2022': diem_cot_g if diem_cot_g else 'N/A',
                    })

            print(f"[{school_name}] Trích xuất thành công {len(temp_data_rows)} ngành.")
            return pd.DataFrame(temp_data_rows)
        else:
            print(f"[{school_name}] Không tìm thấy thẻ <tbody> trong bảng đã trích xuất (có thể bảng trống).")
            return pd.DataFrame()

    except Exception as e:
        print(f"[{school_name}] Đã xảy ra lỗi trong quá trình cào: {e}")
        return pd.DataFrame()


# 3. KHỐI THỰC THI CHÍNH VÀ TỔNG HỢP

try:
    driver = webdriver.Chrome(options=options)

    for school_name, url in school_urls:
        df_school = scrape_school_data(school_name, url, driver)
        if not df_school.empty:
            all_data.append(df_school)

        time.sleep(1)

except Exception as e:
    print(f"\nLỖI CHUNG: Không thể khởi tạo Driver hoặc lỗi trong vòng lặp: {e}")

finally:
    if driver:
        driver.quit()

# 4. LƯU TRỮ VÀ HIỂN THỊ KẾT QUẢ

if all_data:
    df_final = pd.concat(all_data, ignore_index=True)

    final_column_order = [
        'Trường',
        'STT',
        'Ngành/Chương trình',
        'Tổ hợp môn',
        'Chỉ tiêu',
        '2024',
        '2023',
        '2022',
    ]

    # Sắp xếp lại các cột
    df_final = df_final[final_column_order]

    # XUẤT FILE CSV
    file_name = 'Diem_chuan_DHQG_TPHCM_2024_23_22.csv'
    df_final.to_csv(file_name, index=False, encoding='utf-8-sig')

    print("\n" + "=" * 80)
    print(f" QUÁ TRÌNH CÀO HOÀN THÀNH.")
    print(f"Dữ liệu đã được lưu vào file: {file_name}")
    print("=" * 80)

    print("\n5 dòng dữ liệu đầu tiên:\n")
    try:
        print(df_final.head().to_markdown(index=False))
    except ImportError:
        print(df_final.head())

else:
    print("\n KHÔNG có dữ liệu nào được trích xuất.")