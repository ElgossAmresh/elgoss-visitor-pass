from flask import Blueprint, redirect, url_for, request, render_template
from models.database import reqvistable, visitorlogtable, activevisitorstable, rejectedvistable,otp_send, visitors_status
from app.camera_manager import release_camera
import datetime,os
from flask_login import login_required
visitor = Blueprint('visitors', __name__)


@visitor.route('/visitor1', methods=['GET', 'POST'])
def visitor1():
    global approvedby, dobee, dataobject1,pan_data
    
    if request.method == 'POST':
        if request.form['submit'] == 'pass':
            name = request.form['name']
            father = request.form['father']
            dob = request.form['dob']
            gender = request.form['gender']
            uid = request.form['uid']
            date = request.form['Date']
            purpose = request.form['Purpose']
            email = request.form['Email']
            phone = request.form['phone']
            apprv = request.form['Approvedby']
            card = request.form['card']

            dataobject1 = {
                "Name": name,
                "Gender": gender,
                "Card": card,
                "UID": uid,
                "Date": date,
                "Purpose": purpose,
                "Email": email,
                "phone": phone,
                "Approvedby": apprv,
                "Exittime": "",
                "status":""
            }
            
            reqvistable.insert_one(dataobject1)
            visitors_status.insert_one(dataobject1)
            dobee = 1
            
        return redirect(url_for('security.securitydash'))

   
    # return render_template('security_dashboard.html',data=pan_data)


@visitor.route('/deletevis/<uid>', methods=['POST', 'GET'])
def deletevis(uid):
    global approvedby
    activevisitorstable.delete_one({"UID": uid})
    now1 = datetime.datetime.now()
    dt_string = now1.strftime("%d/%m/%Y %H:%M:%S")
    myquery = {"UID": uid}
    newvalues = {"$set": {"Exittime": dt_string}}
    visitorlogtable.update_one(myquery, newvalues)
    return redirect(url_for('security.securitydash'))


@visitor.route('/acceptvis/<uid>', methods=['POST', 'GET'])
def acceptvis(uid):
    element1 = reqvistable.find_one({"UID": uid})
    reqvistable.delete_one({"UID": uid})
  
    visitorlogtable.insert_one(element1)
    activevisitorstable.insert_one(element1)
    status = 'accept' 
    myquery = visitors_status.find_one({"UID": uid})

    visitors_status.update_one(myquery, {"$set": {"status": status}})


    return redirect(url_for('admin.admindash'))


@visitor.route('/rejectvis/<uid>', methods=['POST', 'GET'])
def rejectvis(uid):
    element2 = reqvistable.find_one({"UID": uid})
    reqvistable.delete_one({"UID": uid})
    rejectedvistable.insert_one(element2)
    status = 'reject'  
    myquery = visitors_status.find_one({"UID": uid})

    visitors_status.update_one(myquery, {"$set": {"status": status}})
    return redirect(url_for('admin.admindash'))



