import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 1. Danh sách URL 8 trường thành viên ĐHQG-HCM
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


def scrape_dhqg_selenium():
    print("--- BẮT ĐẦU CÀO DỮ LIỆU 8 TRƯỜNG DÙNG SELENIUM ---")

    # Cấu hình Chrome
    options = Options()
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    all_data = []

    try:
        for school_name, url in urls.items():
            print(f"\n[+] Đang xử lý: {school_name}")
            driver.get(url)

            # Chờ bảng điểm thi THPT xuất hiện
            wait = WebDriverWait(driver, 15)
            # Selector nhắm vào tbody của bảng Điểm thi THPT
            tbody_selector = "#diem-thi-thpt .ant-table-tbody"

            try:
                # Đợi cho đến khi tbody xuất hiện trong DOM
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, tbody_selector)))
                tbody = driver.find_element(By.CSS_SELECTOR, tbody_selector)

                # Lấy tất cả hàng trong bảng
                rows = tbody.find_elements(By.TAG_NAME, "tr")

                for row in rows:
                    cols = row.find_elements(By.TAG_NAME, "td")
                    if len(cols) >= 5:
                        # Trích xuất text từ các ô dựa trên cấu trúc:
                        # STT | Tên ngành | Mã ngành | Tổ hợp môn | Điểm chuẩn | Ghi chú
                        row_content = [
                            school_name,
                            cols[0].text.strip(),  # STT
                            cols[1].text.strip(),  # Tên ngành
                            cols[2].text.strip(),  # Mã ngành
                            cols[3].text.strip(),  # Tổ hợp môn
                            cols[4].text.strip(),  # Điểm chuẩn
                            cols[5].text.strip() if len(cols) > 5 else ""  # Ghi chú
                        ]
                        all_data.append(row_content)

                print(f"    -> Đã lấy {len(rows)} hàng.")

            except Exception as inner_e:
                print(f"    [!] Không tìm thấy bảng hoặc lỗi hàng tại {school_name}")

        # 2. XUẤT DỮ LIỆU RA EXCEL
        if all_data:
            columns = ["Trường", "STT", "Tên ngành", "Mã ngành", "Tổ hợp môn", "Điểm chuẩn", "Ghi chú"]
            df = pd.DataFrame(all_data, columns=columns)

            output_file = "Diem_Chuan_8_Truong_DHQG.xlsx"
            df.to_excel(output_file, index=False)

            print("\n" + "=" * 50)
            print(f"THÀNH CÔNG! Tổng cộng lấy được {len(df)} dòng.")
            print(f"File lưu tại: {output_file}")
        else:
            print("\n[!] Không có dữ liệu nào được thu thập.")

    finally:
        driver.quit()


if __name__ == "__main__":
    scrape_dhqg_selenium()