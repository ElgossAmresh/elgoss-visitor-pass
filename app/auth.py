
from flask import Blueprint, request, render_template, jsonify, redirect, url_for,session,flash
from werkzeug.utils import secure_filename
from werkzeug.security import  check_password_hash
import os
from bson import Binary
from PIL import Image
from flask import send_file, make_response
import io
import base64
from flask_bcrypt import Bcrypt
# from bson import ObjectId  
from flask_login import UserMixin, login_user, login_required, logout_user, current_user
from models.database import collection
from app.extensions import bcrypt,login_manager

from models.user import User
users = User
 
auth = Blueprint('auth', __name__)
  

class User(UserMixin):
    def __init__(self, user_id, username, email, password,Job, profile_image):
        self.id = user_id
        self.username = username
        self.email = email
        self.password = password
        self.Job= Job
        self.profile_image=profile_image


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
                user_data["Job"],
                user_data["profile_image"]["image_name"]

            )
            print(f"user type:{type(user)}")
            session['user_id'] = email   
            session['username'] = user.username 
            session['profile_image'] = user.profile_image  
            session['Job']=user.Job         
            print(f"user data profile_image:{profile_image}")

            session['logged_in'] = True
            login_user(user)
            role = user_data.get("Job", "").lower()
            if role == "admin":
                
                
                return redirect(url_for('admin.admin_h')) 
            elif role == "security":
                
                return redirect(url_for('security.security_home'))  
            else:
                flash("Invalid role", "danger")
                return redirect(url_for('auth.login'))
        else:
            flash("Invalid email or password", "danger")
            return redirect(url_for('auth.login'))

    return render_template("login.html")

@ auth.route('/profile', methods=['POST', 'GET'])
def profile():
    if session.get('user_id'):
        email = session.get('user_id')
        user_data = collection.find_one({"Email": email})
        if user_data :
            # Convert _id to string
            user_data['_id'] = str(user_data['_id'])
            name = user_data.get('Name', '')  
          
            role=user_data.get('Job', '').lower()
            if role == "security":
                
                return render_template('profile_security.html', user_data=user_data, name=name, email=email)
            elif role == "admin":
               
                return render_template('profile_admin.html', user_data=user_data, name=name, email=email)  
            else :
                
                return redirect(url_for('auth.login'))
        
        else:
            return render_template('error.html', message="User data not found.")
  

        
@ auth.route('/view_profile', methods=['POST', 'GET'])
def view_profile():
    if 'user_id' in session:
        email = session['user_id']
        user_data = collection.find_one({'Email': email})
        if user_data:
            user_data['_id'] = str(user_data['_id'])  
            return render_template('profile_security.html', user_data=user_data)
        else:
            return render_template('error.html', message="User not found.")
    else:
        
      return render_template('auth.view_profile')

@auth.route('/update_profile', methods=['POST','GET'])
def update_profile():
    if 'user_id' in session:
        email = session['user_id']
        user_data = collection.find_one({'Email': email})
        if user_data:
            user_data['_id'] = str(user_data['_id'])  
            return render_template('update_profile.html',data=user_data)
   


@auth.route('/update_profile_all', methods=['POST','GET'])
def update_profile_all():
    
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
            email = session['user_id']
           
           
    updated_data = {
        'Name': request.form.get('firstName'),
        'lastName': request.form.get('lastName'),
        'Phone': request.form.get('Phone'),
        'Address': request.form.get('Address'),
        'City': request.form.get('City'),
        'State': request.form.get('State'),
        'Zip': request.form.get('Zip'),
        'Country': request.form.get('Country')
        
    }
    


    result = collection.update_one({'Email': email}, {'$set': updated_data})

    flash("Profile updated successfully!" if result.modified_count else "No changes made.")
    return redirect(url_for('auth.profile'))


@ auth.route('/cancle', methods=['POST', 'GET'])
def cancle():
                 
    return  render_template('security_home.html')

@auth.route('/upload_profile_image', methods=['POST'])
def upload_profile_image():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    file = request.files.get('profile_image')
    if file:
        filename = secure_filename(file.filename)
        save_path = os.path.join('static/images', filename)
        file.save(save_path)
        THUMBNAIL_SIZE = (100, 100)
        
        if not file or not file.filename.endswith(('.jpg', '.jpeg', '.png')):
                return render_template('update_profile.html', message="Invalid file type. Use JPG or PNG.")

            # Open image with Pillow
        image = Image.open(file)

        image.thumbnail(THUMBNAIL_SIZE)

        # Save thumbnail to a bytes 
        thumb_io = io.BytesIO()
        image.save(thumb_io, format=image.format or 'JPEG')
        thumb_data = thumb_io.getvalue()
        # image_doc = {
        #     'image_name': file.filename,  # Store original image name
        #     'thumbnail': thumb_data  # Store thumbnail as binary
        # }
       

        image_doc = {
            'image_name': file.filename,
            'thumbnail': Binary(thumb_data)
        }
        email = session['user_id']
        collection.update_one({'Email': email}, {'$set': {'profile_image': image_doc}})

    return redirect(url_for('auth.update_profile')) 





from flask import send_file, session
import io

@auth.route('/profile/image')
def profile_image():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    email = session['user_id']
    user = collection.find_one({'Email': email})

    if user and 'profile_image' in user:
        image_data = user['profile_image']['thumbnail']
        return send_file(io.BytesIO(image_data), mimetype='image/jpeg')

    return redirect(url_for('static', filename='default.jpg'))
 
