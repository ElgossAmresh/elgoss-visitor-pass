from flask import Blueprint, request, redirect, url_for,render_template,flash
from models.database import collection, securitylog,visitorlogtable,activevisitorstable,rejectedvistable
from werkzeug.security import generate_password_hash
from flask_login import login_required

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


@security.route('/securitydash')
def securitydash():
    pan_data={}
    
    visitobj = list(visitorlogtable.find())
    activeobj = list(activevisitorstable.find())
    return render_template('visitor.html', data=pan_data, visitobj=visitobj, activeobj=activeobj, approvedby=approvedby)


@security.route("/visitor", methods=["GET"])
def visitor():
    visitobj = list(visitorlogtable.find())
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