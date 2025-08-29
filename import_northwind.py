import sqlite3
import pandas as pd
import os

# مسار مجلد CSV
data_dir = "data/northwind-SQLite3-main"
# مسار قاعدة SQLite
db_path = "data/northwind.sqlite"

# فتح أو إنشاء قاعدة البيانات
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# استيراد كل الملفات في المجلد
for filename in os.listdir(data_dir):
    file_path = os.path.join(data_dir, filename)
    
    if filename.endswith(".csv"):
        table_name = os.path.splitext(filename)[0]
        df = pd.read_csv(file_path)
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        print(f"Imported CSV: {table_name}")
    
    elif filename.endswith(".sql"):
        with open(file_path, "r", encoding="utf-8") as f:
            sql_script = f.read()
        cursor.executescript(sql_script)
        print(f"Executed SQL script: {filename}")

# تأكيد وحفظ التغييرات
conn.commit()
conn.close()
print("All files imported into SQLite successfully!")
