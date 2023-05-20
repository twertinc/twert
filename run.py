from flask import Flask, request, url_for

from flask_admin import Admin, BaseView, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView

from flask_autocrud import AutoCrud
from flask_sqlalchemy import SQLAlchemy
import psutil
import socket
import platform
import ruleman
import time
import datetime
import os
import sys
from Classify import Classify


def resource_path( relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# https://flask-admin.readthedocs.io/en/v1.0.9/templates/#building-blocks
# https://flask-admin.readthedocs.io/en/latest/api/mod_model/

db = None
product_name = "Twert version 0.1 Beta"

class AnalyticsView(AdminIndexView):
    @expose('/')
    def index(self):
        # group into 0 (night), 1 (morning), 2(afternoon), 3 (evening)
        # select count(id),ROUND(strftime('%H',last_seen)/6) as time_type from domains where last_seen>datetime('now','-7 days') group by time_type

        # top domains order by hit_count grouped by time_type
        # select domain,hit_count,ROUND(strftime('%H',last_seen)/6) as time_type, LENGTH(domain) - LENGTH(REPLACE(domain, '.', '')) as dot_count from domains where last_seen>datetime('now','-7 days') and dot_count=1 order by time_type,hit_count desc

        # Select top 10 records for each category
        # https://stackoverflow.com/questions/28119176/select-top-n-record-from-each-group-sqlite
        time_type_top3_query = """SELECT *
FROM (
    SELECT
      ROW_NUMBER() OVER (
        PARTITION BY "time_type"
        ORDER BY "hit_count" DESC
      ) AS "rnk",
      *
    FROM (
           SELECT domain,
                  hit_count,
                  ROUND(strftime('%H', last_seen) / 6) AS time_type,
                  LENGTH(domain) - LENGTH([REPLACE](domain, '.', '') ) AS dot_count
             FROM domains
            WHERE last_seen > datetime('now', '-7 days') AND 
                  dot_count = 1
            ORDER BY time_type,
                     hit_count DESC
       )
) sub
WHERE
  "sub"."rnk" <= 3
ORDER BY
  "sub"."time_type" ASC,
  "sub"."hit_count" DESC"""

        ret = db.session.execute(time_type_top3_query)
        rows = ret.fetchall()
        time_type_top3 = rows # row[0,1, ...] rnk=0, domain=1,hit_count=2,time_type=3,dot_count=4
        print("Time type top 3",time_type_top3)
      
        # top 10 domains
        # select domain,hit_count from domains  where last_seen>datetime('now','-7 days') order by hit_count desc limit 10
        ret = db.session.execute("select domain,hit_count,LENGTH(domain) - LENGTH([REPLACE](domain, '.', '') ) AS dot_count from domains  where last_seen>datetime('now','-7 days') and dot_count=1 order by hit_count desc limit 5")
        rows = ret.fetchall()
        # top5_domains = [o[0] for o in rows]
        # top5_hits = [o[1] for o in rows]
        top5 = rows
        print("Top 5 domains",rows)
   

        # top 10 top level domains
        # select domain,hit_count,LENGTH(domain) - LENGTH(REPLACE(domain, '.', '')) as dot_count  from domains  where last_seen>datetime('now','-7 days') and dot_count<=1 order by hit_count desc limit 10
        return self.render('admin/dashboard.html',top5=top5)
		
class AboutView(BaseView):
    @expose('/')
    def index(self):
        uptime_secs = (time.time() - psutil.boot_time())
        uptimestr = str(datetime.timedelta(seconds=uptime_secs))
        return self.render('admin/about.html',len=len,datetime=datetime,
          users=",".join([o.name for o in psutil.users()]),
          uptime=uptimestr,memory=psutil.virtual_memory(),cpu_percent=psutil.cpu_percent(),
          psutil=psutil,socket=socket,product_name=product_name,platform=platform)

		
class CustomAdminView(ModelView):
    can_export = True
    details_modal = True
    column_display_pk = True
    can_set_page_size = True
    can_view_details = True
    column_exclude_list = ['id']
    form_excluded_columns = ['create_time','modify_time','id','first_seen','last_seen']
    list_template = "admin/model/my_list.html"
	

def convert(word):
    return ''.join(x.capitalize() or '_' for x in word.split('_'))
	
def update_process_list(dbsession):
  
  for proc in psutil.process_iter():
    try:
        # Get process name & pid from process object.
        processName = proc.name()
        processExe = proc.exe()
        processID = proc.pid
        print(processExe , ' ::: ', processID)
        dbsession.execute("INSERT INTO processes (full_name,exe_name,running) VALUES (:full,:exe,True) ON CONFLICT (full_name) DO UPDATE SET running=True",{"full":processExe,"exe":processName})
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        pass

  dbsession.commit()

# def rules_push_to_manager(model):
#     global db

#     # fetch time rules
#     ret = db.session.execute("SELECT  strftime('%H:%M',from_time),strftime('%H:%M',to_time) FROM time_rules")
#     rows = ret.fetchall()
#     print(rows)

#     time_starts = []
#     time_ends = []

#     for row in rows:
#       # print(type(row),type(row[0]))
#       time_start = row[0]
#       time_end = row[1]
#       time_starts.append(time_start)
#       time_ends.append(time_end)
   
#     # fetch process rules
#     process_names = []

#     ret = db.session.execute("SELECT  exe_name FROM process_rules WHERE is_blocked=TRUE")
#     rows = ret.fetchall()
#     print(rows)
#     for row in rows:
#       process_names.append(row[0])
    
#     # fetch domain rules
#     domain_names = []
#     ret = db.session.execute("SELECT  domain FROM domain_rules WHERE is_blocked=TRUE")
#     rows = ret.fetchall()
#     print(rows)
#     for row in rows:
#       domain_names.append(row[0])
    

#     ruleman.update_rules(time_starts,time_ends,process_names, domain_names)
   

def rules_changed(form,model,is_created):
    print("Rule changed ",form,model,is_created)
    #rules_push_to_manager(model)
    pass

def rules_deleted(model):
    print("Rule deleted ",model)
    #rules_push_to_manager(model)
    pass
	
def main():
    application_path = ""
    database_path = ""
    if getattr(sys, 'frozen', False):
      template_folder = os.path.join(sys._MEIPASS, 'templates')
      static_folder = os.path.join(sys._MEIPASS, 'static')
      application_path = os.path.dirname(sys.executable)
      database_path = os.path.join(application_path, 'nblocker.sqlite3')
      app = Flask(__name__, template_folder=template_folder, static_folder = static_folder)
    else:
      app = Flask(__name__)
      application_path = os.path.dirname(__file__)
      database_path = 'nblocker.sqlite3'
    app.config['SECRET_KEY'] = 'more_difficult_string'
    app.config['FLASK_ADMIN_SWATCH'] = 'cerulean' #'cosmo'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite+pysqlite:///' + database_path
    app.config['SQLALCHEMY_TsRACK_MODIFICATIONS'] = False
    print(os.path.join(os.path.dirname(application_path), 'nblocker.sqlite3'))
    admin = Admin(app,template_mode='bootstrap4', index_view=AnalyticsView(name='Dashboard'))
    global db
    db = SQLAlchemy(app)
    autocrud = AutoCrud(app, db)

    #app.add_url_rule('/favicon.ico',redirect_to=url_for('static', filename='favicon.ico'))
	
    @app.route('/dns', methods=['GET'])
    def dns_incoming():
      args = request.args
      domain = args.get("domain")
      if domain is not None:
        print("DNS query reported "+domain)
        dbret = db.session.execute("INSERT INTO domains (domain,hit_count,first_seen,last_seen) VALUES ('{}',1,datetime('now'),datetime('now')) ON CONFLICT (domain) DO UPDATE SET hit_count=hit_count+1, last_seen=datetime('now')".format(domain))
        print("DbRet {}".format(dbret))
        db.session.commit()
	  
      return args	  
	
    #admin.add_view(AnalyticsView(name='Dashboard', endpoint='analytics'))

    # setup views and catch rules changed
    for k, m in autocrud.models.items():
        setattr(CustomAdminView, 'column_searchable_list', m.searchable())
        # setattr(CustomAdminView, 'name', k + "XX")
        print("Adding AdminView for ",k)
        aView = CustomAdminView(m, db.session, name=convert(k))
        if k=="domains" or k=="processes":
           aView.can_create = False
           aView.can_edit = False
           aView.can_delete = False
  
        if k=="domain_rules" or k=="process_rules" or k=="time_rules":
           aView.after_model_change = rules_changed
           aView.after_model_delete = rules_deleted

        admin.add_view(aView)

    # add the about at last
    admin.add_view(AboutView(name='About', endpoint='about'))
    
		
    @app.after_request
    def after_request(resp):
      if "/edit" in request.full_path or "/new" in request.full_path:
        print('after_request '+request.full_path)
      
      return resp		

    @app.before_request
    def before_request():
      if "/admin/processes" in request.full_path:
        print(" >> Loading process list ...")
        update_process_list(db.session)
		
    app.run(debug=True,use_reloader=False)


if __name__ == '__main__':
    print("Starting RuleManager ...")
    ruleman.start_thread()
    Classify.start_thread()
    main()
