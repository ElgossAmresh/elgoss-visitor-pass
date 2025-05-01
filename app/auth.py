
from flask import Blueprint, request, render_template, jsonify, redirect, url_for,session,flash

from werkzeug.security import  check_password_hash

from flask_bcrypt import Bcrypt
# from bson import ObjectId  
from flask_login import UserMixin, login_user, login_required, logout_user, current_user
from models.database import collection
from app.extensions import bcrypt,login_manager

from models.user import User
users = User
 
auth = Blueprint('auth', __name__)
  

class User(UserMixin):
    def __init__(self, user_id, username, email, password,Job):
        self.id = user_id
        self.username = username
        self.email = email
        self.password = password
        self.Job= Job


@login_manager.user_loader
def load_user(user_id):
    return users.get_by_id(user_id)





@ auth.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user_data = collection.find_one({"Email": email})
        print(f"user data  {user_data}")
        
        if not user_data:
            flash("Invalid email and Password", "danger")
            return redirect(url_for('auth.login'))

        # Check password
        if check_password_hash(user_data["Password"], password):
            user = User(
                str(user_data["_id"]),
                user_data["Name"],
                user_data["Email"],
                user_data["Password"],
                user_data["Job"]
            )

           
            login_user(user)

            role = user_data.get("Job", "").lower()

            if role == "admin":
                # flash("Login successful!", "success")
                return redirect(url_for('admin.admin_h')) 
            elif role == "security":
                # flash("Login successful!", "success")
                return redirect(url_for('security.security_home'))  
            else:
                flash("Invalid role", "danger")
                return redirect(url_for('auth.login'))
        else:
            flash("Invalid email or password", "danger")
            return redirect(url_for('auth.login'))

    return render_template("login.html")


    


    


