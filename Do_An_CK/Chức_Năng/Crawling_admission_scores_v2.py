import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 1. DANH SÁCH URL 8 TRƯỜNG THÀNH VIÊN
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


def scrape_all_dhqg():
    print("--- BẮT ĐẦU CÀO DỮ LIỆU TỔNG HỢP 8 TRƯỜNG ---")

    options = Options()
    # options.add_argument("--headless") # Bỏ comment nếu muốn chạy ẩn
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    all_data = []

    try:
        for school_name, url in urls.items():
            print(f"\n[+] Đang xử lý: {school_name}")
            driver.get(url)
            wait = WebDriverWait(driver, 20)

            # Bước 1: Cuộn trang để kích hoạt bảng tải dữ liệu
            driver.execute_script("window.scrollTo(0, 1000);")
            time.sleep(3)

            # Bước 2: Tìm tất cả các bảng (Điểm THPT, Xét tuyển kết hợp...)
            table_selectors = [
                "//div[@id='diem-thi-thpt']//tbody[contains(@class, 'ant-table-tbody')]",
                "//div[@id='xet-tuyen-ket-hop']//tbody[contains(@class, 'ant-table-tbody')]"
            ]

            for selector in table_selectors:
                try:
                    # Kiểm tra xem bảng đó có tồn tại trên trang không
                    tbodies = driver.find_elements(By.XPATH, selector)
                    for tbody in tbodies:
                        rows = tbody.find_elements(By.TAG_NAME, "tr")

                        count = 0
                        for row in rows:
                            # Bỏ qua hàng trống/hàng đang tải
                            if "ant-table-placeholder" in row.get_attribute("class"):
                                continue

                            cols = row.find_elements(By.TAG_NAME, "td")
                            if len(cols) >= 5:
                                # Cấu trúc web: [0]STT, [1]Tên, [2]Mã, [3]Tổ hợp, [4]Điểm, [5]Ghi chú
                                stt = cols[0].text.strip()
                                ten_nganh = cols[1].text.strip()
                                ma_nganh = cols[2].text.strip()
                                to_hop = cols[3].text.strip()
                                diem = cols[4].text.strip()
                                ghi_chu = cols[5].text.strip() if len(cols) > 5 else ""

                                all_data.append([
                                    school_name, stt, ma_nganh, ten_nganh, to_hop, diem, ghi_chu
                                ])
                                count += 1
                        if count > 0:
                            print(f"    -> Đã lấy {count} ngành từ bảng.")
                except:
                    continue

        # 3. XUẤT FILE EXCEL TỔNG HỢP
        if all_data:
            columns = ["Trường", "STT", "Mã ngành", "Tên ngành", "Tổ hợp môn", "Điểm chuẩn", "Ghi chú"]
            df = pd.DataFrame(all_data, columns=columns)

            # Làm sạch dữ liệu: Xóa các dòng tiêu đề bị lẫn vào
            df = df[df["Mã ngành"] != "Mã ngành"]

            output_file = "Diem_Chuan_8_Truong_DHQG.xlsx"
            df.to_excel(output_file, index=False)

            print("\n" + "=" * 50)
            print(f"THÀNH CÔNG! Tổng cộng đã cào được {len(df)} hàng dữ liệu.")
            print(f"File lưu tại: {output_file}")
        else:
            print("\n[!] Không lấy được dữ liệu. Kiểm tra kết nối mạng hoặc Selector.")

    finally:
        driver.quit()


if __name__ == "__main__":
    scrape_all_dhqg()