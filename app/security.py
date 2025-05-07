from flask import Blueprint, request, redirect, url_for,render_template,flash
from models.database import collection, securitylog,visitorlogtable,activevisitorstable,rejectedvistable,visitors_status
from werkzeug.security import generate_password_hash
from flask_login import login_required
from datetime import datetime
from pymongo import ASCENDING 
security = Blueprint('security', __name__, template_folder='templates')
visitobj = list(visitorlogtable.find())
activeobj = list(activevisitorstable.find())

rejectobj = list(rejectedvistable.find())

secobj = list(securitylog.find())


reject=len(rejectobj)
countvis = len(visitobj)
active = len(activeobj)
total=countvis+reject

approvedby = ""

security = Blueprint('security', __name__)


@security.route('/addsec', methods=['POST','GET'])

def add_security():
   if request.method == 'POST':
        if request.form['submit'] == 'pass':
            name1 = request.form['fullname']
            email1 = request.form['addemail']
            phone = request.form['phone']
            job = request.form['jobtitle']
            password = request.form['password']
            hashed_password = generate_password_hash(password)
            daobject = {
                "Name": name1,
                "Email": email1,
                "Phone": phone,
                "Job": job,
                "Password": hashed_password, 
            }

          

        collection.insert_one(daobject)
        securitylog.insert_one(daobject)
 
        return redirect(url_for('routes.login'))  # Redirect to the login page


@security.route('/securitydash',methods=['GET','POST'])
def securitydash():
    pan_data={}
 

    from_date = request.form.get('FromDate')
    to_date = request.form.get('ToDate')

    query = {}

    if from_date and to_date:
        try:
            from_obj = datetime.strptime(from_date, '%Y-%m-%d')
            to_obj = datetime.strptime(to_date, '%Y-%m-%d')
            query['Date'] = {"$gte": from_date, "$lte": to_date}

        except ValueError:
            pass  

    visitors = visitors_status.find(query).sort("Date", ASCENDING)
    
    visitobj = list(visitorlogtable.find())
    activeobj = list(activevisitorstable.find())
    return render_template('visitor.html', data=pan_data, visitobj=visitobj, activeobj=activeobj, approvedby=approvedby,visit=visitors)


@security.route("/visitor", methods=["GET"])
def visitor():   
    
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    print(f"startdate+++{start_date_str},end date---------{end_date_str}")
    query = {}
    visitobj = []

    if start_date_str and end_date_str:
        try:
            # Parse dates from string to datetime
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
            end_date = end_date.replace(hour=23, minute=59, second=59)  # include full end day            
            query = {
                'Date': {
                    '$gte': start_date,
                    '$lte': end_date
                }
            }
            print(f"quer++===================={query}")
            visitobj = list(visitors_status.find(query))
            print(f"store data in db {visitobj}")
        except ValueError:            
            visitobj = []

    else:        
        visitobj = list(visitors_status.find())
    return render_template("visitor.html",visitobj=visitobj)
    


@security.route("/security_home", methods=["GET"])
def security_home():
   
    return render_template("security_home.html",total=total,countvis=countvis)

@security.route('/home', methods=['POST', 'GET'])
def home():
    return render_template("security_home.html",total=total,countvis=countvis)
@security.route("/overview", methods=["GET"])
def overview():
    visitobj = list(visitorlogtable.find({"exit_time": None}))
  
    return render_template("overview.html",visitobj=visitobj)