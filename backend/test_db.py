from db import get_connection

try:
    conn = get_connection()
    print("MYSQL CONNECTION SUCCESS")
    conn.close()
except Exception as e:
    print("MYSQL CONNECTION FAILED")
    print(e)
