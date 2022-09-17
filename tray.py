import webbrowser
from infi.systray import SysTrayIcon


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
systray = SysTrayIcon("icon.ico", "Twert 0.1", menu_options)


systray.start()