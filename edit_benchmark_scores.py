import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# 1. Danh sách các trường cần cào
urls = {
    "Đại học Khoa học Sức khỏe": "https://diemthi.tuyensinh247.com/diem-chuan/dai-hoc-khoa-hoc-suc-khoe-tphcm-QSY.html",
    "Đại học Bách Khoa": "https://diemthi.tuyensinh247.com/diem-chuan/dai-hoc-bach-khoa-hcm-QSB.html",
    "Đại học Khoa học Tự nhiên": "https://diemthi.tuyensinh247.com/diem-chuan/dai-hoc-khoa-hoc-tu-nhien-tphcm-QST.html",
    "Đại học Công nghệ Thông tin": "https://diemthi.tuyensinh247.com/diem-chuan/dai-hoc-cong-nghe-thong-tin-dhqg-tphcm-QSC.html",
    "Đại học Kinh tế Luật": "https://diemthi.tuyensinh247.com/diem-chuan/dai-hoc-kinh-te-luat-tphcm-QSK.html",
    "Đại học KHXH và Nhân văn": "https://diemthi.tuyensinh247.com/diem-chuan/dai-hoc-khoa-hoc-xa-hoi-va-nhan-van-tphcm-QSX.html",
    "Đại học Quốc tế": "https://diemthi.tuyensinh247.com/diem-chuan/dai-hoc-quoc-te-dhqg-tphcm-QSQ.html",
    "Đại học An Giang": "https://diemthi.tuyensinh247.com/diem-chuan/dai-hoc-an-giang-QSA.html"
}

# 2. Cấu hình hiển thị trình duyệt
chrome_options = Options()
# chrome_options.add_argument("--headless") # Bỏ comment nếu muốn ẩn trình duyệt
chrome_options.add_experimental_option("detach", True)  # Giữ trình duyệt sau khi chạy xong
chrome_options.add_argument("--start-maximized")

# Khởi tạo Driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

all_data = []

print("--- BẮT ĐẦU CÀO DỮ LIỆU ---")

for school_name, url in urls.items():
    print(f"Đang xử lý: {school_name}...")
    try:
        driver.get(url)
        time.sleep(3)  # Đợi trang và các bảng JS load hoàn tất

        # Chuyển mã nguồn sang BeautifulSoup để xử lý nhanh hơn
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Tìm tất cả các bảng trên trang
        tables = soup.find_all('table')

        if not tables:
            print(f"  [!] Không tìm thấy bảng nào tại {school_name}")
            continue

        for table in tables:
            # Kiểm tra xem bảng có chứa tiêu đề cột "Ngành" hay không để tránh bảng rác
            header_text = table.get_text()
            if "Ngành" not in header_text and "Điểm" not in header_text:
                continue

            # Lấy tên năm (h2 hoặc h3 nằm ngay phía trên bảng)
            year_tag = table.find_previous(['h2', 'h3'])
            year_text = year_tag.get_text(strip=True) if year_tag else "Thông tin chung"

            tbody = table.find('tbody')
            if not tbody:
                continue

            rows = tbody.find_all('tr')
            for tr in rows:
                cols = [td.get_text(strip=True) for td in tr.find_all('td')]
                if len(cols) >= 3:  # Chỉ lấy những dòng có dữ liệu thực sự
                    # Thêm Tên trường và Năm vào đầu danh sách cột
                    all_data.append([school_name, year_text] + cols)

    except Exception as e:
        print(f"  [X] Lỗi tại {school_name}: {e}")

driver.quit()

# 3. Kiểm tra và xuất dữ liệu ra Excel
if all_data:
    # Xác định số lượng cột lớn nhất để đặt tên cột cho đúng
    max_cols_found = max(len(row) for row in all_data)

    # Tạo danh sách tiêu đề cột tạm thời
    column_names = ["Trường", "Năm/Phương thức", "STT", "Mã ngành", "Tên ngành", "Tổ hợp", "Điểm chuẩn", "Ghi chú"]
    # Nếu dữ liệu thực tế nhiều cột hơn danh sách trên, tự động thêm cột "Khác"
    while len(column_names) < max_cols_found:
        column_names.append(f"Thông tin khác {len(column_names) - 6}")

    # Tạo DataFrame
    df = pd.DataFrame(all_data, columns=column_names[:max_cols_found])
    
    # ===== FIX RIÊNG ĐH KHOA HỌC SỨC KHỎE KHI XUẤT EXCEL =====
    mask = df["Trường"] == "Đại học Khoa học Sức khỏe"

    # Hoán đổi Mã ngành <-> Tên ngành
    df.loc[mask, ["Mã ngành", "Tên ngành"]] = df.loc[
        mask, ["Tên ngành", "Mã ngành"]
    ].values

    # Xuất ra file Excel
    output_file = "diem_chuan_cac_truong_dhqg.xlsx"
    df.to_excel(output_file, index=False)

    print("-" * 30)
    print(f"THÀNH CÔNG! Đã cào tổng cộng {len(all_data)} dòng.")
    print(f"Dữ liệu đã được lưu vào file: {output_file}")
else:
    print("-" * 30)
    print("THẤT BẠI: Không có dữ liệu nào được thu thập.")