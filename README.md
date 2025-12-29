# VietNam-graduation-exam-score-analysis

# Thu Thập và Phân Tích Dữ Liệu Điểm Thi THPT Quốc Gia 2025

[![Python](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)
[![Selenium](https://img.shields.io/badge/Selenium-Automation-green.svg)](https://www.selenium.dev/)
[![HUTECH](https://img.shields.io/badge/HUTECH-University-orange.svg)](https://www.hutech.edu.vn/)

Đồ án môn học **Mã nguồn mở trong khoa học dữ liệu**, tập trung vào việc xây dựng hệ thống tự động thu thập dữ liệu điểm thi và thực hiện phân tích thống kê để đánh giá bức tranh toàn cảnh về kỳ thi THPT Quốc Gia năm 2025.

## 📋 Mục Lục
- [Giới thiệu](#-giới-thiệu)
- [Thành viên nhóm](#-thành-viên-nhóm)
- [Công nghệ sử dụng](#-công-nghệ-sử-dụng)
- [Kiến trúc hệ thống](#-kiến-trúc-hệ-thống)
- [Quy trình thực hiện](#-quy-trình-thực-hiện)
- [Kết quả phân tích](#-kết-quả-phân-tích)
- [Hướng phát triển](#-hướng-phát-triển)

## 📖 Giới thiệu

Kỳ thi THPT Quốc Gia có vai trò quan trọng trong việc xét tốt nghiệp và tuyển sinh đại học. Đề tài này được thực hiện nhằm:
1.  **Thu thập dữ liệu:** Tự động hóa việc lấy điểm thi từ các trang thông tin chính thống (Vietnamnet).
2.  **Đánh giá:** Cung cấp cái nhìn khách quan về hiệu quả dạy học.
3.  **Phân tích:** Nhận diện xu hướng, mức độ phân hóa giữa các môn học và đưa ra các đề xuất cải thiện chất lượng dạy học.

**Giảng viên hướng dẫn:** ThS. Lê Nhật Tùng

## 👥 Thành viên nhóm

| STT | Họ và tên | MSSV | Vai trò |
|:---:|:---|:---|:---|
| 1 | **Nguyễn Đức Vinh** | 2386400052 | Leader |
| 2 | Nguyễn Đăng Khoa | 2386400026 | Member |
| 3 | Phan Xuân Dương | 2386400966 | Member |

## 🛠 Công nghệ sử dụng

Dự án sử dụng các công cụ và thư viện mã nguồn mở mạnh mẽ:

* **Ngôn ngữ lập trình:** [Python](https://www.python.org/) - Ngôn ngữ bậc cao với hệ sinh thái thư viện phong phú.
* **Thu thập dữ liệu (Crawling):** [Selenium](https://www.selenium.dev/) - Công cụ tự động hóa trình duyệt để mô phỏng thao tác người dùng.
* **Lưu trữ:** [SQLite](https://www.sqlite.org/index.html) - Hệ quản trị cơ sở dữ liệu nhẹ, phù hợp cho việc lưu trữ cục bộ.
* **Trực quan hóa (Visualization):**
    * **Matplotlib:** Vẽ biểu đồ cơ bản.
    * **Seaborn:** Mở rộng của Matplotlib, hỗ trợ vẽ biểu đồ thống kê hiện đại và đẹp mắt.

## 🏗 Kiến trúc hệ thống

Mô hình hoạt động của hệ thống bao gồm các thành phần chính:
1.  **User:** Kích hoạt hệ thống.
2.  **Orchestrator System:** Điều phối và gửi tác vụ (tasks).
3.  **Crawl Workers:** Nhận tác vụ và gửi request đến Website đích.
4.  **Parse Workers:** Nhận dữ liệu thô, phân tích cấu trúc (Structure Data).
5.  **Clean Data:** Làm sạch và kiểm tra tính hợp lệ (Check Valid Data).
6.  **Storage:** Lưu trữ dữ liệu sạch vào Database (SQLite).

## 🚀 Quy trình thực hiện

1.  **Thu thập dữ liệu:**
    * Nguồn dữ liệu: `vietnamnet.vn`
    * Sử dụng Selenium để duyệt qua danh sách số báo danh và lấy dữ liệu điểm.
2.  **Làm sạch dữ liệu:**
    * Xử lý dữ liệu thiếu, sai định dạng.
    * Chuẩn hóa dữ liệu trước khi lưu trữ.
3.  **Lưu trữ:**
    * Dữ liệu cấu trúc được lưu vào bảng trong SQLite.
4.  **Phân tích & Trực quan hóa:**
    * Truy vấn dữ liệu từ SQLite.
    * Vẽ biểu đồ Histogram, Violin plot để phân tích phổ điểm từng môn (Toán, Văn, Anh, Lý, Hóa, Sinh, Sử, Địa, GDCD...).

## 📊 Kết quả phân tích

Dựa trên dữ liệu thu thập được, nhóm đã rút ra một số nhận xét sơ bộ:
* **Phân bố điểm:** Đa số các môn học thuật cốt lõi tuân theo phân phối chuẩn (hình chuông) với đỉnh tập trung ở mức trung bình (5-6 điểm).
* **Độ phân hóa:** Đề thi có độ tin cậy cao, phân tách rõ ràng hai nhóm đối tượng: xét tốt nghiệp và xét tuyển đại học.

*(Bạn có thể chèn thêm hình ảnh biểu đồ từ file báo cáo vào thư mục `images/` và hiển thị tại đây)*

## 🔮 Hướng phát triển

Dự án định hướng mở rộng trong tương lai:

1.  **Mở rộng phạm vi:**
    * So sánh phổ điểm qua các năm (2023-2025).
    * Phân tích sâu theo khu vực (vùng miền, tỉnh thành).
2.  **Ứng dụng công nghệ cao:**
    * Áp dụng **Machine Learning** để dự đoán điểm hoặc phân nhóm năng lực thí sinh.
    * Xây dựng **Dashboard** (Plotly/PowerBI) để báo cáo Real-time.
3.  **Cải tiến kỹ thuật:**
    * Nâng cấp CSDL lên MySQL/PostgreSQL để quản lý Big Data.
    * Tự động cập nhật dữ liệu khi có nguồn mới.

---
© 2025 HUTECH University - Khoa Công nghệ thông tin
