import sqlite3
import browser_history
from datetime import datetime
import time
from urllib.parse import urlparse
import threading
import logging
import os
import sys
import copy

# logging.basicConfig(filename=r'C:\Users\Nam Anh\twert\logs\history.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
# logging.warning("path of history.py: {}".format(os.path.dirname(os.path.abspath(__file__))))

database_path = "nblocker.sqlite3"
program_start_time = datetime.now()


def find_nth(haystack, needle, n):
    start = haystack.find(needle)
    while (start>= 0 and n > 1):
        start = haystack.find(needle, start + len(needle))
        n-=1
    return start
    

def absolute_history_path(path):
    if os.path.isabs(path):
        return path
    
    # logging.warning("path of sys.executable: {}".format(os.path.dirname(sys.executable)))
    exec_path = str(os.path.dirname(sys.executable)) + "\\" 

    tmp_conn = create_connection(database_path)
    tmp_cur = tmp_conn.cursor()
    user_path = tmp_cur.execute("select username from current_user").fetchall()[0][0]
    tmp_conn.close()
    # logging.warning("user path: {}".format(os.path.join(user_path, path)))
    return os.path.join(user_path, path)

def copy_history_file(absolute_og_path, new_path):
    pass

def convert_browser_path():
    # read from copy location, absolute_history _path is the path of the og
    browser_history.browsers.Chromium.windows_path = absolute_history_path(browser_history.browsers.Chromium.windows_path)
    browser_history.browsers.Chrome.windows_path = absolute_history_path(browser_history.browsers.Chrome.windows_path)
    browser_history.browsers.Firefox.windows_path = absolute_history_path(browser_history.browsers.Firefox.windows_path)
    browser_history.browsers.Edge.windows_path = absolute_history_path(browser_history.browsers.Edge.windows_path)
    browser_history.browsers.Opera.windows_path = absolute_history_path(browser_history.browsers.Opera.windows_path)
    browser_history.browsers.OperaGX.windows_path = absolute_history_path(browser_history.browsers.OperaGX.windows_path)
    browser_history.browsers.Brave.windows_path = absolute_history_path(browser_history.browsers.Brave.windows_path)
    browser_history.browsers.Vivaldi.windows_path = absolute_history_path(browser_history.browsers.Vivaldi.windows_path)


def parse_domain(domain: str):
    return urlparse(domain).netloc

# start_time = time.time()

# history = browser_history.get_history()

# for num, entry in enumerate(history.histories):
#     print("{}. time:{} , domain:{} ".format(num, entry[0], parse_domain(entry[1])))

# print("time to print history: {}".format(time.time() - start_time))


def create_connection(db_file : str):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Exception as e:
        logging.error(e)
    return conn
    
def diff_history(datetime_history_list, history_list_after): 
    
    diff = []
    for entry in range(len(history_list_after)-1, 0, -1):
        if (history_list_after[entry][0] > datetime_history_list):
            diff.append(history_list_after[entry])
        else:
            break
    return diff

def log_a_list(prefix, tmp_list, num):
    num = min(len(tmp_list), num)
    for i in range(1,num + 1):
        # logging.warning("{}. {} :{}".format(num - i + 1, prefix, tmp_list[-i]))
        pass

def add_all_history(conn, datetime_history_list):
    # copy new file over , check against old file, add diff to admin, delete old file 
    convert_browser_path()

    # logging.warning("Chromium.windows_path: {}".format(browser_history.browsers.Chromium.windows_path))
    # logging.warning("Chrome.windows_path: {}".format(browser_history.browsers.Chrome.windows_path))
    # logging.warning("Firefox.windows_path: {}".format(browser_history.browsers.Firefox.windows_path))
    # logging.warning("Edge.windows_path: {}".format(browser_history.browsers.Edge.windows_path))
    # logging.warning("Opera.windows_path: {}".format(browser_history.browsers.Opera.windows_path))
    # logging.warning("OperaGX.windows_path: {}".format(browser_history.browsers.OperaGX.windows_path))
    # logging.warning("Brave.windows_path: {}".format(browser_history.browsers.Brave.windows_path))
    # logging.warning("Vivaldi.windows_path: {}".format(browser_history.browsers.Vivaldi.windows_path))
    history_list_future = []
    try:    
        history_list_future = browser_history.get_history().histories
        log_a_list("history_list_future current entry",history_list_future, 100)
    except Exception as e:
        # logging.warning(e)
        pass
    diff = diff_history(datetime_history_list, history_list_future)
    log_a_list("diff current entry",diff, 10)
    diff.reverse()
    for entry in diff:
        domain = parse_domain(entry[1])
        timestamp = entry[0]
        # logging.warning("time:{} , domain:{} ".format(timestamp, domain))
        sql = """INSERT INTO domains (domain,hit_count,first_seen,last_seen, browser)
                VALUES (?,1,?,?, ?) 
                ON CONFLICT (domain) 
                DO UPDATE SET hit_count=hit_count+1, last_seen=?, browser = ?
                """
        sql1 = """INSERT INTO domains (domain,hit_count,first_seen,last_seen, browser)
                VALUES (?,1,?,?, ?) 
                """
        cursor = conn.cursor()
        cursor.execute(sql, (domain, timestamp, timestamp, 'TRUE', timestamp , 'TRUE'))
        #cursor.execute(sql1, (domain, timestamp, timestamp, 'TRUE'))
    conn.commit()
    # logging.warning("time add history: {}".format(history_list_future[-1][0]))
    return history_list_future[-1][0]


def thread_run():
    convert_browser_path()
    # logging.warning("Chromium.windows_path: {}".format(browser_history.browsers.Chromium.windows_path))
    # logging.warning("Chrome.windows_path: {}".format(browser_history.browsers.Chrome.windows_path))
    # logging.warning("Firefox.windows_path: {}".format(browser_history.browsers.Firefox.windows_path))
    # logging.warning("Edge.windows_path: {}".format(browser_history.browsers.Edge.windows_path))
    # logging.warning("Opera.windows_path: {}".format(browser_history.browsers.Opera.windows_path))
    # logging.warning("OperaGX.windows_path: {}".format(browser_history.browsers.OperaGX.windows_path))
    # logging.warning("Brave.windows_path: {}".format(browser_history.browsers.Brave.windows_path))
    # logging.warning("Vivaldi.windows_path: {}".format(browser_history.browsers.Vivaldi.windows_path))
    conn = create_connection(database_path)
    datetime_current_history = browser_history.get_history().histories[-1][0]
    # logging.warning("beginning time: {}".format(datetime_current_history))
    while True:
        try:
            datetime_current_history = add_all_history(conn, datetime_current_history)
            time.sleep(90)
        except (KeyboardInterrupt, SystemExit):
            try:
                log_a_list("all history", browser_history.get_history().histories, 1000)
            except Exception as e:
                # logging.warning("error when adding all history: {}".format(e))
                conn.close()
            conn.close()
            break
    





def start_thread():
    rThread = threading.Thread(target=thread_run,daemon=True)
    rThread.start()
    pass




# still can't resolve bug where history is inserted into the browser's history non-linearly, meaning that sometimes old entries can be added later. 
# tried to minimize this bug by adding the new browser history entries every 15 minutes.
# can optimize by changing history_sql in browsers.py and generic.py. Current approach in clunky, can replace the diff function with the correct sql call where visit_time > datetime_current_history. 