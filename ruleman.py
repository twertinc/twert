import os
import datetime
import threading
from tracemalloc import start
import time
import psutil
import elevate

time_start = [] # ['21:29', '11:25']
time_end = [] # ['22:22', '11:37']
exe_list = [] # ['notepad.exe']
hosts_path = "C:\Windows\System32\drivers\etc\hosts"

redirect = "127.0.0.1"
website_list = [] # ["www.facebook.com","facebook.com",
      # "dub119.mail.live.com","www.dub119.mail.live.com",
      # "www.gmail.com","gmail.com"]

counter = 0

def update_rules(time_start_rules,time_end_rules,process_names,domain_names):
    #todo this should be Lock()
    global time_start 
    time_start.clear()
    time_start = time_start_rules.copy()
    global time_end
    time_end.clear()
    time_end = time_end_rules.copy()
    global exe_list
    exe_list = process_names.copy()
    global website_list
    website_list = domain_names.copy()
    print("update_rules(): ",threading.get_native_id(),time_start,time_end,exe_list,website_list)

def checktime(name):
    global time_start
    global time_end
    global counter
    counter = counter + 1

    if not time_start:
        # print(name,counter,threading.get_native_id(),"No time range means always True",len(time_start),time_start)
        return True
    else:
      # print("Checktime",counter,threading.get_native_id(),time_start,time_end)
      for i in range(len(time_start)):
        # print(name,"Checking time between",time_start[i],time_end[i],"now is",datetime.datetime.now().hour,":",datetime.datetime.now().minute)
        datetime_time_start = datetime.datetime.strptime(time_start[i], '%H:%M')

        datetime_time_end = datetime.datetime.strptime(time_end[i], '%H:%M')
        if (datetime_time_start.hour * 60 + datetime_time_start.minute <= datetime.datetime.now().hour * 60 + datetime.datetime.now().minute) and (datetime.datetime.now().hour * 60 + datetime.datetime.now().minute <= datetime_time_end.hour * 60 + datetime_time_end.minute):
            return True

    return False  


def blockexe(): #block từ time_start -> time_end (2 cái này là string) vd: "18:00"
    if checktime():
        #print("exe still blocked")

        for exe in exe_list: #todo, change to using psutil please
            cmd_string = "taskkill /f /im " + exe
            os.system(cmd_string) # os.system là để chạy command trên cmd

def psutil_blockexe(): #block từ time_start -> time_end (2 cái này là string) vd: "18:00"
    if checktime("exe"):
        for proc in psutil.process_iter():
            if proc.name() in exe_list:
                proc.kill()
    else:
        # print("psutil_blockexe checktime() not yet")
        pass
                

def webblock():  
    if checktime("web"):
        with open(hosts_path, 'r+') as file:
            content = file.read()
            for website in website_list:
                if website in content:
                    pass
                else:
                    # mapping hostnames to your localhost IP address
                    file.write(redirect + " " + website + "\n")
    else:
        with open(hosts_path, 'r+') as file:
            content=file.readlines()
            file.seek(0)
            for line in content:
                if not any(website in line for website in website_list):
                    file.write(line)

            # removing hostnmes from host file
            file.truncate()

def thread_run(id):
    print("A thread ",threading.get_native_id()," was spawned for rule manager daemon")
    while True:
        time.sleep(1)
        try:
            psutil_blockexe()
            webblock()
        except Exception as e:
            print("RuleMan exception: ",e)    

def start_thread():
    elevate.elevate()
    print("Rule Manager is now running ",threading.get_native_id())
    rThread = threading.Thread(target=thread_run,args=(1,),daemon=True)
    rThread.start()
    pass