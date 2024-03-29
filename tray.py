import webbrowser
import os
import sys
import sqlite3


from infi.systray import SysTrayIcon


database_path = 'nblocker.sqlite3'

try:
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    current_user = os.path.expanduser('~')

    cursor.execute("delete from current_user")
    cursor.execute("insert into current_user (username) values ('{}')".format( current_user))

    conn.commit()
    conn.close()
except Exception as e:
    print(e)
def dashboard(systray):
    url = 'http://127.0.0.1:5000/admin/'
    webbrowser.open_new(url)


def domainRules(systray):
    url = 'http://127.0.0.1:5000/admin/domain_rules/'
    webbrowser.open_new(url)

def domains(systray):
    url = 'http://127.0.0.1:5000/admin/domains/'
    webbrowser.open_new(url)

def processRules(systray):
    url = 'http://127.0.0.1:5000/admin/process_rules/'
    webbrowser.open_new(url)

def processes(systray):
    url = 'http://127.0.0.1:5000/admin/processes/'
    webbrowser.open_new(url)

def timeRules(systray):
    url = 'http://127.0.0.1:5000/admin/time_rules/'
    webbrowser.open_new(url)

def about(systray):
    url = 'http://127.0.0.1:5000/admin/about/'
    webbrowser.open_new(url)

menu_options = (
    ("Dashboard", None, dashboard),
    ("Domain Rules", None, domainRules),
    ("Domains", None, domains),
    ("Process Rules", None, processRules),
    ("Processes", None, processes),
    ("Time Rules", None, timeRules),
    ("About", None, about),
)

icon_path = ""
if getattr(sys, 'frozen', False):
    icon_path = os.path.join(sys._MEIPASS, 'favicon.ico')
else:
    icon_path = 'favicon.ico'



systray = SysTrayIcon(icon_path, "Twert", menu_options)


systray.start()