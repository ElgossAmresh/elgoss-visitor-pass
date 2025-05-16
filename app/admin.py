from flask import Blueprint, request, redirect, url_for,render_template,flash,request,session
from werkzeug.security import generate_password_hash
from models.database import collection, adminlog, securitylog,visitorlogtable,activevisitorstable,reqvistable,rejectedvistable,visitors_status
from datetime import date,datetime
from flask_bcrypt import Bcrypt
from bson import ObjectId
from collections import defaultdict
from flask import json

admin = Blueprint('admin', __name__)
bcrypt = Bcrypt()

visitobj = list(visitorlogtable.find())
activeobj = list(activevisitorstable.find())

rejectobj = list(rejectedvistable.find())
adminobj = list(adminlog.find())
secobj = list(securitylog.find())
reqobj = list(reqvistable.find())
pending=len(reqobj)
reject=len(rejectobj)
countvis = len(visitobj)
active = len(activeobj)

total=reject+countvis
now = datetime.now()          
current_date = now.date().isoformat() 
current_time = now.time().isoformat()  

@admin.route('/admindash')

def admindash():

    global months,accept_data,total_data,Name
    all_visitors = list(visitors_status.find({}))  

    monthly_stats = defaultdict(lambda: {"accept": 0, "total": 0})

    for visitor in all_visitors:
        if 'Date' in visitor:
            dt = visitor['Date']
           
            if isinstance(dt, str):
                try:
                      dt = datetime.fromisoformat(dt)
                except ValueError:
                    continue  

            month = dt.strftime("%b")  
            monthly_stats[month]["total"] += 1
            if visitor.get("status") == "accept":
                monthly_stats[month]["accept"] += 1

    
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    accept_data = [monthly_stats[m]["accept"] for m in months]
    total_data = [monthly_stats[m]["total"] for m in months]
    if session.get('user_id'):
        email = session.get('user_id')
        user_data = collection.find_one({"Email": email})
        if user_data :
            # Convert _id to string
            user_data['_id'] = str(user_data['_id'])
            Name = user_data.get('Name', '') 



    return render_template('admin_h.html',pending=pending ,total=total,countvis=countvis, active=active,rejectobj=reject,
                           months=months, accept_data=accept_data, total_data=total_data)


@admin.route('/addadmin', methods=['POST'])
def add_admin():
      if request.method == 'POST':
       
        if request.form['submit1'] == 'pass':
            Name= request.form['fullname']
            Email=request.form['addemail']
            Phone=request.form['phone']
            Job=request.form['jobtitle']
            Password=request.form['password']
            date = current_date
            time=current_time

            hashed_password = generate_password_hash(Password)
            # hashed_password = bcrypt.generate_password_hash(Password).decode('utf-8')
            new_admin = {
                "Name":Name,
                "Email":Email,
                "Phone":Phone,
                "Date":date,
                "Time":time,
                "Job":Job,
                "Password":hashed_password ,                  
               'profile_image': {
                   'image_name':'dummy.png',
                   'thumbnail':'test'
               } 
        }

            
            collection.insert_one(new_admin)
            adminlog.insert_one(new_admin)
        return redirect(url_for('admin.admindash'))
@admin.route('/deleteuser/<string:Phone>', methods=['POST', 'GET'])
def deleteuser(Phone):
    collection.delete_one({"Phone": Phone})
    securitylog.delete_one({"Phone": Phone})
    adminlog.delete_one({"Phone": Phone})
    return redirect(url_for('admin.admindash'))


# @admin.route('/updateusers/<id>', methods=['POST', 'GET'])
# def updateusers(id):
#     users = collection.db.users
#     items = users.find_one({'_id': ObjectId(id)})

#     if request.method == 'POST':
#         if request.form['submit'] == 'pass':
#             myquery = {'_id': ObjectId(id)}

#             updatelog = {"$set":
#                              {"Name": request.form.get('Name'),
#                               "Email": request.form.get('Email'),
#                               "Phone": request.form.get('Phone'),
#                               "Job": request.form.get('Job'),
#                               "Password": request.files.get('Password'),
#                               "date": datetime.datetime.utcnow()
#                               }
#                          }

#     adminlog.update_one(myquery, updatelog)
#     collection.update_one(myquery, updatelog)
#     securitylog.update_one(myquery, updatelog)

    # return redirect(url_for('admin.admindash'))

@admin.route('/edituser/<string:Phone>', methods=['GET','POST'])
def edituser():
    phone = request.args.get('Phone')
    user = collection.find_one({"Phone": phone})

    return render_template('user_overview.html')

@admin.route("/notification",methods=['POst','GET'])
def notification():
    reqobj = list(reqvistable.find())
    return render_template ('Notification.html',reqobj=reqobj) 


@admin.route("/filter_role", methods=['GET'])  # dropdown filtering
def filter_role():
   
    status = request.args.get('role', 'all')
    query = {} if status == 'all' else {"Job": status}

    users = list(collection.find(query))  
    return render_template('user_overview.html', users=users, selected_role=status)


@admin.route("/visitor_over",methods=['POst','GET'])
def visitor_over():

    status = request.args.get('status', 'all')
    query = {} if status == 'all' else {"status": status}

    users = list(visitors_status.find(query))  
    return render_template('visitor_overview.html', users=users, status_filter=status) 


@admin.route("/admin_h",methods=['POst','GET'])
def admin_h():
    global months,accept_data,total_data
    all_visitors = list(visitors_status.find({}))  

    monthly_stats = defaultdict(lambda: {"accept": 0, "total": 0})

    for visitor in all_visitors:
        if 'Date' in visitor:
            dt = visitor['Date']
            # Convert string to datetime if needed
            if isinstance(dt, str):
                try:
                      dt = date.fromisoformat(dt)
                except ValueError:
                    continue  

            month = dt.strftime("%b")  
            monthly_stats[month]["total"] += 1
            if visitor.get("status") == "accept":
                monthly_stats[month]["accept"] += 1

    #  month order for the chart
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    accept_data = [monthly_stats[m]["accept"] for m in months]
    total_data = [monthly_stats[m]["total"] for m in months]
    return render_template ("admin_h.html",  pending=pending ,total=total,countvis=countvis, active=active,rejectobj=reject,
                           months=months, accept_data=accept_data, total_data=total_data)  
   







@admin.route('/submit_date_range', methods=['POST'])
def submit_date_range():
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')

    # start_dt = date.strptime(start_date, '%Y-%m-%d')
    # end_dt = date.strptime(end_date, '%Y-%m-%d')
    # end_dt = end_dt.replace(hour=23, minute=59, second=59)

    print(f"[INFO] Date range submitted: {start_date} to {end_date}")

    results = list(visitors_status.find({
        "Date": {
            "$gte": start_date,
            "$lte": end_date 
        }
        
    }))
    
    # for r in results:
    #     r["_id"] = str(r["_id"])
    #     r["timestamp"] = r["timestamp"].strftime("%d-%b-%Y %H:%M")
    
    return render_template("visitor.html",  visitobj=results)
