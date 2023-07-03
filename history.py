import sqlite3
import browser_history
from datetime import datetime
import time
from urllib.parse import urlparse
import threading
def parse_domain(domain: str):
    return urlparse(domain).netloc

# start_time = time.time()

# history = browser_history.get_history()

# for num, entry in enumerate(history.histories):
#     print("{}. time:{} , domain:{} ".format(num, entry[0], parse_domain(entry[1])))

# print("time to print history: {}".format(time.time() - start_time))

database_path = "nblocker.sqlite3"

def create_connection(db_file : str):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Exception as e:
       print(e)
    return conn
    
def diff_history(history_list_prev, history_list_after) -> list: 
    
    diff = []
    for entry in range(len(history_list_after)-1, 0, -1):
        if (history_list_after[entry]!= history_list_prev[-1]):
            diff.append(history_list_after[entry])
        else:
            break
    return diff


def add_all_history(conn, history_list: list):
    for entry in history_list:
        domain = parse_domain(entry[1])
        timestamp = entry[0]

        sql = """INSERT INTO domains (domain,hit_count,first_seen,last_seen)
                VALUES (?,1,?,?) 
                ON CONFLICT (domain) 
                DO UPDATE SET hit_count=hit_count+1, last_seen=?"""
        cursor = conn.cursor()
        cursor.execute(sql, (domain, timestamp, timestamp, timestamp))
        conn.commit()
def add_all_history_one_min_interval(conn, history_list : list):
    time.sleep(60)
    history_list_future = browser_history.get_history().histories
    diff = diff_history(history_list, history_list_future)
    for entry in diff:
        domain = parse_domain(entry[1])
        timestamp = entry[0]

        sql = """INSERT INTO domains (domain,hit_count,first_seen,last_seen)
                VALUES (?,1,?,?) 
                ON CONFLICT (domain) 
                DO UPDATE SET hit_count=hit_count+1, last_seen=?"""
        cursor = conn.cursor()
        cursor.execute(sql, (domain, timestamp, timestamp, timestamp))
        conn.commit()


def thread_run():
    conn = create_connection(database_path)
    while True:
        add_all_history_one_min_interval(conn, browser_history.get_history().histories)

def start_thread():
    rThread = threading.Thread(target=thread_run,daemon=True)
    rThread.start()
    pass



