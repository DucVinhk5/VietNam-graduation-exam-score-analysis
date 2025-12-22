from bs4 import BeautifulSoup
from typing import List, Optional
from helper.color_map import STATUS_MAP, RESET


def parser_html(page_source: str, year: int, sbd: int) -> Optional[List[List[str]]]:
    # Tạo đối tượng BeautifulSoup
    soup = BeautifulSoup(page_source, "lxml")

    # Kiểm tra xem trang có thông báo "không có dữ liệu" không
    if soup.find("p", class_="notification__main"):
        icon, color = STATUS_MAP["Fail"]
        print(f"Parse: {year} - {sbd}, {color}Status: {icon} No data found{RESET}")
        return None

    # Lấy thông tin khu vực
    khu_vuc_tag = soup.find("p", class_="edu-institution")
    khu_vuc = khu_vuc_tag.get_text(strip=True) if khu_vuc_tag else ""

    # Tìm thẻ tbody trong bảng
    tbody_tag = soup.find("tbody")
    if not tbody_tag:
        icon, color = STATUS_MAP["Fail"]
        print(f"Parse: {year} - {sbd}, {color}Status: {icon} No table found{RESET}")
        return None

    # Thông tin cơ bản cho mỗi hàng
    general_infos = [year, khu_vuc, sbd]
    results = []

    # Lặp qua từng hàng trong bảng và thêm dữ liệu vào results
    for row in tbody_tag.find_all("tr"):
        cols = [td.get_text(strip=True) for td in row.find_all("td")]
        results.append(general_infos + cols)

    # In thông báo thành công với số lượng hàng
    icon, color = STATUS_MAP["Success"]
    print(f"Parse: {year} - {sbd}, {color}Status: {icon} Success, {len(results)} rows{RESET}")
    return results
