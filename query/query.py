import pandas as pd
import sqlite3


# Đường dẫn tới db
DB_PATH = r"C:\Users\DELL\Documents\GitHub\VietNam-graduation-exam-score-analysis\diem_thpt_quoc_gia.db"
TABLE_NAME = "Diem_THPT_QuocGia"

# Thiết lập kết nối tới db
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Truy vấn số lượng học sinh
query = f"SELECT COUNT(DISTINCT SBD) FROM {TABLE_NAME}"
count = cursor.execute(query).fetchone()[0]

print(f"Số lượng học sinh: {count:_}")

# Truy vấn các chỉ số thống kê cơ bản từng môn
query = f"SELECT DISTINCT subject FROM {TABLE_NAME}"
subjects = cursor.execute(query).fetchall()

query = """
    SELECT
        COUNT(score),
        MAX(score),
        AVG(score),
        MIN(score)
    FROM Diem_THPT_QuocGia
    WHERE subject = ?
"""

stats = []

for subject in subjects:
    cursor.execute(query, (subject[0],))
    stat = cursor.fetchone()
    stats.append((subject[0],) + stat)

stat_df = pd.DataFrame(stats, columns=['Subject', 'Count', 'Max', 'Mean', 'Min'])
print(stat_df.round(2))