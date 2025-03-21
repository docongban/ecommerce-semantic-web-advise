import mysql.connector

db_config = {
    "host": "localhost",
    "user": "root",
    "password": "adminadmin",
    "database": "semantic_web_ecommerce",
}

def insertToMysql(tableName, data, cursor):
    if not data:
        print("Không có dữ liệu để insert.")
        return

    # Lấy danh sách cột từ keys của dict đầu tiên trong data_list
    columns = list(data.keys())
    placeholders = ", ".join(["%s"] * len(columns))

    sql = f"""
        INSERT INTO {tableName} ({', '.join(columns)})
        VALUES ({placeholders})
        ON DUPLICATE KEY UPDATE {", ".join([f"{col} = VALUES({col})" for col in columns])}
    """

    values = tuple(data.values())

    try:
        cursor.execute(sql, values)
        print(f"✅ Đã insert 1 data vào bảng {tableName}.")
        return cursor.lastrowid
    except Exception as e:
        print(f"❌ Lỗi khi insert vào MySQL: {e}")

def insertAllToMysql(tableName, data, cursor):
    if not data:
        print("Không có dữ liệu để insert.")
        return

    # Lấy danh sách cột từ keys của dict đầu tiên trong data_list
    columns = list(data[0].keys())
    placeholders = ", ".join(["%s"] * len(columns))

    sql = f"""
        INSERT INTO {tableName} ({', '.join(columns)})
        VALUES ({placeholders})
        ON DUPLICATE KEY UPDATE {", ".join([f"{col} = VALUES({col})" for col in columns])}
    """

    values = [tuple(item.values()) for item in data]

    try:
        cursor.executemany(sql, values)
        print(f"✅ Đã insert {len(data)} data vào bảng {tableName}.")
        return [cursor.lastrowid + i for i in range(len(data))]
    except Exception as e:
        print(f"❌ Lỗi khi insert vào MySQL: {e}")

