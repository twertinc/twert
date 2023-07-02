import sqlite3
import browser_history
from datetime import datetime
history = browser_history.get_history()
print(type(history.histories))

database_path = "nblocker.sqlite3"

def create_connection(db_file : str):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Exception as e:
       print(e)
    return conn
    
def add_history(conn, history_list):
    for entry in history_list:
        domain = entry[1]
        timestamp = entry[0]

        sql = """INSERT INTO domains (domain,hit_count,first_seen,last_seen)
                VALUES (?,1,?,?) 
                ON CONFLICT (domain) 
                DO UPDATE SET hit_count=hit_count+1, last_seen=?"""
        cursor = conn.cursor()
        cursor.execute(sql, (domain, timestamp, timestamp, timestamp))
        conn.commit()

a = create_connection(database_path)
add_history(a, history.histories)
a.close()

    





