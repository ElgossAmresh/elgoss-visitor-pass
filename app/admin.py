from flask import Blueprint, request, redirect, url_for,render_template,flash,request,session
from werkzeug.security import generate_password_hash
from models.database import collection, adminlog, intern_db,securitylog,visitorlogtable,activevisitorstable,reqvistable,rejectedvistable,visitors_status
from datetime import date,datetime
from flask_bcrypt import Bcrypt
from bson import ObjectId
from collections import defaultdict
from flask import json
import smtplib
from config.setting import SMTP_PORT,SMTP_SERVER,SENDER_EMAIL,SENDER_PASSWORD

from email.mime.text import MIMEText

admin = Blueprint('admin', __name__)
bcrypt = Bcrypt()

visitobj = list(visitorlogtable.find())
activeobj = list(activevisitorstable.find())

rejectobj  = list(visitors_status.find({"Status": "rejected"}))

adminobj = list(adminlog.find())
secobj = list(securitylog.find())
reqobj = list(reqvistable.find())
pending=len(reqobj)
reject=len(rejectobj)
countvis = len(visitobj)
active = len(activeobj)
visit=list(visitors_status.find())

totals= list(visitors_status.find()) 
total=len(totals)
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



    return render_template('admin_h.html',  pending=pending ,total=totals,countvis=countvis, active=active,rejectobj=reject,
                           months=months, accept_data=accept_data, total_data=total_data )


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
            update_pass(Email)
            new_admin = {
                "Name":Name,
                "Email":Email,
                "Phone":Phone,
                "Date":date,
                "Time":time,
                "Job":Job,
                "Password":hashed_password ,                  
               'profile_image': {
                   'image_name':None,
                   'thumbnail':'test'
               } 
        }

            update_pass(Email)
            if Job =="Intern":
                intern_db.insert_one(new_admin)
            collection.insert_one(new_admin)
            adminlog.insert_one(new_admin)
        return redirect(url_for('admin.filter_role'))

     
@admin.route('/deleteuser/<string:Phone>', methods=['POST', 'GET'])
def deleteuser(Phone):
    collection.delete_one({"Phone": Phone})
    securitylog.delete_one({"Phone": Phone})
    adminlog.delete_one({"Phone": Phone})
    # return render_template('user_overview.html')
    return redirect(url_for('admin.filter_role'))




@admin.route('/edituser/<string:Phone>', methods=['GET','POST'])
def edituser():
    phone = request.args.get('Phone')
    user = collection.find_one({"Phone": phone})

    return render_template('user_overview.html')

@admin.route("/notification",methods=['POst','GET'])
def notification():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
   
    filtered = reqvistable.find({
        "Date": {
            "$gte": start_date,
            "$lte": end_date
        }
    })

    return render_template('Notification.html',reqobj=filtered)

 

@admin.route("/filter_role", methods=['GET'])  # dropdown filtering
def filter_role():
   
    status = request.args.get('role', 'all')
    query = {} if status == 'all' else {"Job": status}

    users = list(collection.find(query))  
    return render_template('user_overview.html', users=users, selected_role=status)

@admin.route("/visitor_over", methods=['GET', 'POST'])
def visitor_over():
    status = request.args.get('status', 'all')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    query = {}

    # Filter by status if not 'all'
    if status != 'all':
        query['status'] = status

    # Filter by date range if provided
    if start_date and end_date:
        query['Date'] = {
            "$gte": start_date,
            "$lte": end_date
        }
    users = list(visitors_status.find(query))
    return render_template('visitor_overview.html', users=users, status_filter=status)



@admin.route("/admin_h",methods=['POst','GET'])
def admin_h():
    filter_type = request.args.get("filter", "all")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
   
    query = {}

    # Apply status filter
    if filter_type == "accepted":
        query["status"] = "accepted"
    elif filter_type == "rejected":
        query["status"] = "rejected"
    elif filter_type == "pending":
        query["status"] = ""

    
    if start_date and end_date:
        try:
            start_dt = start_date
            end_dt = end_date
            # Assuming the 'date' field in your MongoDB is stored as datetime object
            query["date"] = {"$gte": start_dt, "$lte": end_dt}
        except ValueError:
            print("Invalid date format received")
    
  

    # Query the filtered results
    visitobj = list(visitors_status.find(query).sort("date", -1))

    # For total stats (not filtered)
    all_visitors = list(visitors_status.find({}))

    reject = sum(1 for v in all_visitors if v.get("status") == "rejected")
    active = sum(1 for v in all_visitors if v.get("status") == "accepted")
    pending = sum(1 for v in all_visitors if v.get("status") == "")

    total = len(all_visitors)

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
                           months=months, accept_data=accept_data, total_data=total_data ,visitobj =visitobj)  
    

@admin.route("/attendance",methods=['POST','GET'])
def attendance():
    return render_template("attendance_table.html")



def update_pass(email):

    sender_email = SENDER_EMAIL
    sender_password = SENDER_PASSWORD

    smtp_server = SMTP_SERVER
    smtp_port = SMTP_PORT
    recipient_email = email


    subject = "reset Password"
    body = "http://127.0.0.1:5000/update_password"

    # Send the email
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = recipient_email

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Enable TLS encryption
            server.login(sender_email, sender_password)
            server.send_message(msg)
            session['reset_email'] = email # start the session of exist email in your db
        # print(f"OTP '{otp}' sent to {recipient_email}")
    except Exception as e:
        print(f"Error sending email: {e}")


@admin.route("/update_password",methods=['POST','GET'])
def update_password():

    return render_template("update_pass.html")




