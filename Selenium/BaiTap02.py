from pygments.formatters.html import webify 
from selenium import webdriver
from selenium.webdriver.common.by import By
import time 

# Khởi tạo Webdriver 
driver = webdriver.Chrome()

# Mở trang 
url = "https://en.wikipedia.org/wiki/List_of_painters_by_name"
driver.get(url)

# Đợi khoảng chừng 2 giây 
time.sleep(2)

# lấy tất cả các thể <a>
tags = driver.find_elements(By.XPATH,"//a[contains(@title,'List of painters')]")

# Tạo ra danh sách các liên kết 
links = [tag.get_attribute("href") for tag in tags]

# Xuất thông tin 
for link in links:
    print(link)

# dong Webdriver
driver.quit()