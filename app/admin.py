from flask import Blueprint, request, redirect, url_for,render_template,flash,request
from werkzeug.security import generate_password_hash
from models.database import collection, adminlog, securitylog,visitorlogtable,activevisitorstable,reqvistable,rejectedvistable,visitors_status
from datetime import datetime
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

@admin.route('/admindash')

def admindash():

    global months,accept_data,total_data
    all_visitors = list(visitors_status.find({}))  

    monthly_stats = defaultdict(lambda: {"accept": 0, "total": 0})

    for visitor in all_visitors:
        if 'Date' in visitor:
            dt = visitor['Date']
            # Convert string to datetime if needed
            if isinstance(dt, str):
                try:
                      dt = datetime.fromisoformat(dt)
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
            hashed_password = generate_password_hash(Password)
            # hashed_password = bcrypt.generate_password_hash(Password).decode('utf-8')
            new_admin = {
                "Name":Name,
                "Email":Email,
                "Phone":Phone,
                "Job":Job,
                "Password":hashed_password 

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


@admin.route('/updateusers/<id>', methods=['POST', 'GET'])
def updateusers(id):
    users = collection.db.users
    items = users.find_one({'_id': ObjectId(id)})

    if request.method == 'POST':
        if request.form['submit'] == 'pass':
            myquery = {'_id': ObjectId(id)}

            updatelog = {"$set":
                             {"Name": request.form.get('Name'),
                              "Email": request.form.get('Email'),
                              "Phone": request.form.get('Phone'),
                              "Job": request.form.get('Job'),
                              "Password": request.files.get('Password'),
                              "date": datetime.datetime.utcnow()
                              }
                         }

    adminlog.update_one(myquery, updatelog)
    collection.update_one(myquery, updatelog)
    securitylog.update_one(myquery, updatelog)

    return redirect(url_for('admin.admindash'))
@admin.route("/notification",methods=['POst','GET'])
def notification():
    reqobj = list(reqvistable.find())
    return render_template ('Notification.html',reqobj=reqobj)   

@admin.route("/user_over",methods=['POst','GET'])
def user_over():
    
    return render_template ('user_overview.html', secobj=secobj, adminobj=adminobj)  

@admin.route("/visitor_over",methods=['POst','GET'])
def visitor_over():
    return render_template ('visitor_overview.html', rejectobj=rejectobj, visitobj=visitobj)  


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
                      dt = datetime.fromisoformat(dt)
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
