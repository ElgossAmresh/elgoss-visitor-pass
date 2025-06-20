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
# total=countvis+reject

approvedby = ""

security = Blueprint('security', __name__)


@security.route('/addsec', methods=['POST','GET'])

# def add_security():
#    if request.method == 'POST':
#         if request.form['submit'] == 'pass':
#             name1 = request.form['fullname']
#             email1 = request.form['addemail']
#             phone = request.form['phone']
#             job = request.form['jobtitle']
#             password = request.form['password']
#             hashed_password = generate_password_hash(password)
#             daobject = {
#                 "Name": name1,
#                 "Email": email1,
#                 "Phone": phone,
#                 "Job": job,
#                 "Password": hashed_password, 
#             }

          

#         collection.insert_one(daobject)
#         securitylog.insert_one(daobject)
 
#         return redirect(url_for('routes.login'))  # Redirect to the login page


@security.route('/securitydash',methods=['GET','POST'])
def securitydash():
    pan_data={}
 

    from_date = request.form.get('start_date')
    to_date = request.form.get('end_date')

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
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    print(f"start date ============================== {start_date}, end date: {end_date}")
    filtered_visitors = visitors_status.find({
        "Date": {
            "$gte": start_date,
            "$lte": end_date
        }
    })
    print(f"Filtered visitors : {filtered_visitors}")

    return render_template("visitor.html",  visitobj=filtered_visitors)
     
    


@security.route("/security_home", methods=["GET"])
def security_home():
    filter_type = request.args.get("filter", "all")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    print(f"start date ============================== {start_date}")
    query = {}

    # Apply status filter
    if filter_type == "accepted":
        query["status"] = "accepted"
    elif filter_type == "exist":
        query["status"] = "exist"
    elif filter_type == "":
        query["status"] = ""

    
    if start_date and end_date:
        try:
            start_dt = start_date
            end_dt = end_date
            # Assuming the 'date' field in your MongoDB is stored as datetime object
            query["date"] = {"$gte": start_dt, "$lte": end_dt}
        except ValueError:
            print("Invalid date format received")
    
    print(f"Final MongoDB query: {query}")  # Debugging

    # Query the filtered results
    visitobj = list(visitors_status.find(query).sort("date", -1))

    # For total stats (not filtered)
    all_visitors = list(visitors_status.find({}))

    reject = sum(1 for v in all_visitors if v.get("status") == "rejected")
    active = sum(1 for v in all_visitors if v.get("status") == "accepted")
    pending = sum(1 for v in all_visitors if v.get("status") == "")

    total = len(all_visitors)
   
 
    return render_template("security_home.html",total=total,countvis=countvis,active=active,visitobj=visitobj)

@security.route('/home', methods=['POST', 'GET'])
def home():
    return render_template("security_home.html",countvis=countvis)

@security.route("/overview", methods=["GET"])
def overview():
    visitobj = list(visitorlogtable.find({"exit_time": None}))
  
    return render_template("overview.html",visitobj=visitobj)


@security.route("/filter_by_date",methods=["GET"])
def filter_by_date():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    print(f"start date ============================== {start_date}, end date: {end_date}")
    filtered_visitors = visitors_status.find({
        "Date": {
            "$gte": start_date,
            "$lte": end_date
        }
    })
    print(f"Filtered visitors : {filtered_visitors}")

    return render_template("visitor.html",  visitobj=filtered_visitors)
@security.route("/attendance_camera", methods=["GET"])
def attendance_camera():

    return render_template("attendance_camera.html")