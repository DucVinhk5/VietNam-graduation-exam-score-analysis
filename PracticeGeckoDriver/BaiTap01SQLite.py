import sqlite3

# 1.Kết nối tới CSDL
conn = sqlite3.connect("inventory.db")

# Tạo đối tượng 'cursor' để thực thi các câu lệnh SQL
cursor =  conn.cursor()

# 2. Thao tác với DataBase và Table
# Lệnh SQL để tạo bảng products
sql1 = """
    CREATE TABLE IF NOT EXISTS products(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price NUMERIC NOT NULL,
        quantity INTEGER
)
"""

# Thực thi câu lệnh tạo bảng
cursor.execute(sql1)
conn.commit() # Lưu thay đổi vào DB
# 3. CRUD
# 3.1. Thêm (INSERT)
products_data = [
    ("Laptop A100", 999.99, 15),
    ("Mouse Wireless X", 25.50, 50),
    ("Monitor 27-inch", 249.00, 10)
]

# Lệnh SQL để chèn dữ liệu. Dùng '?' để tráng lỗi SQL Injection
sql2 = """
        INSERT INTO products (name, price, quantity) 
        VALUES
        (?, ?, ?)
"""

# THêm nhiều bản ghi cùng lúc
cursor.executemany(sql2, products_data)
conn.commit() # Lưu thay đổi

# 3.2 READ (SELECT)
sql3 = "SELECT * FROM products"

# Thực thi truy vấn
cursor.execute(sql3)

# Lấy tất cả kết quả
all_products = cursor.fetchall()

# In tiêu đề
print(f"{'ID':<4} | {'Tên Sản Phẩm':<20} | {'Giá':<10} | {'Số Lượng':<10}")

# Lặp và in ra
for p in all_products:
    print(f"{p[0]:<4} | {p[1]:<20} | {p[2]:<10} | {p[3]:<10}")

# 3.3 UPDATE
# Cập nhật giá của 'Laptop A100' và tăng số lượng lên 5.
product_to_update = "Laptop A100"
new_price = 950.00
increase_quantity = 5

sql4 = """
        UPDATE products 
        SET price = ?, quantity = quantity + ?
        WHERE name = ?
"""

# Thực thi câu lệnh UPDATE
cursor.execute(sql4, (new_price, increase_quantity, product_to_update))
conn.commit() # Lưu thay đổi

print(f"Đã cập nhật sản phẩm: {product_to_update}. Giá mới: {new_price}, Số lượng tăng thêm: {increase_quantity}")

# 3.4 DELETE
# Xóa sản phẩm 'Mouse Wireless X'.
product_to_delete = "Mouse Wireless X"

sql5 = """
        DELETE FROM products
        WHERE name = ?
"""

# Thực thi câu lệnh DELETE
cursor.execute(sql5, (product_to_delete,))
conn.commit() # Lưu thay đổi

print(f"Đã xóa sản phẩm: {product_to_delete}.")

print("\nDanh sách sản phẩm sau khi xóa:")
cursor.execute("SELECT * FROM products")
all_products_after_delete = cursor.fetchall()

print(f"{'ID':<4} | {'Tên Sản Phẩm':<20} | {'Giá':<10} | {'Số Lượng':<10}")
for p in all_products_after_delete:
    print(f"{p[0]:<4} | {p[1]:<20} | {p[2]:<10} | {p[3]:<10}")