
from flask import Blueprint, request, render_template, jsonify, redirect, url_for,session,flash
from werkzeug.utils import secure_filename
from werkzeug.security import  check_password_hash
import os
from bson import Binary
from PIL import Image
from flask import send_file, make_response
import io
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
            session['user_id'] = user.email   
            session['username'] = user.username 
            session['profile_image'] = user.profile_image  
            session['Job']=user.Job 
            if user.username and len(user.username) > 0:
             session['username_short'] = user.username[0].upper()
            else:
             session['username_short'] = '?'  

           

            session['logged_in'] = True
            login_user(user)
            role = user_data.get("Job", "").lower()
            if role == "admin":
                
                return redirect(url_for('admin.admin_h')) 
            elif role == "intern":
                
                return redirect(url_for('security.security_home')) 
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
            return render_template('view_profile.html', data=user_data)
        else:
            return render_template('error.html', message="User not found.")
    else:
        
      return render_template('view_profile.html')

@auth.route('/update_profile', methods=['POST','GET'])
def update_profile():
    if 'user_id' in session:
        email = session['user_id']
        user_data = collection.find_one({'Email': email})
        if user_data:
            user_data['_id'] = str(user_data['_id'])  
            return render_template('update_profile.html',data=user_data)
   


@auth.route('/update_profile_all', methods=['POST'])
def update_profile_all():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        email = session.get('user_id')

        updated_data = { 
            'Name': request.form.get('firstName'),
            'lastName': request.form.get('lastName'),
            'Phone': request.form.get('Phone'),
            'Address': request.form.get('Address'),
            'City': request.form.get('City'),
            'State': request.form.get('State'),
            'PIN code': request.form.get('PIN code'),
            'DOB': request.form.get('DOB'),
            'Email': request.form.get('Email'),
            'Skill': request.form.get('Skill'),
            'Gender': request.form.get('Gender'),
            'Company': request.form.get('Company'),
            'class10_board':request.form.get('class10_board'),
            'class10_year':request.form.get('class10_year'),
            'class10_percentage':request.form.get('class10_percentage'),
            'class10_schoolName':request.form.get('class10_schoolName'),
            
            'class12_board':request.form.get('class12_board'),
            'class12_year':request.form.get('class12_year'),
            'class12_percentage':request.form.get('class12_percentage'),
            'class12_schoolName':request.form.get('class12_schoolName'),
            
            'grad_university':request.form.get('grad_university'),
            'grad_year':request.form.get('grad_year'),
            'grad_percentage':request.form.get('grad_percentage'),
            'grad_collegename':request.form.get('grad_collegename'),
            
            'pg_university':request.form.get('pg_university'),
            'pg_year':request.form.get('pg_year'),
            'pg_percentage':request.form.get('pg_percentage'),
            'pg_collegename':request.form.get('pg_collegename'),
            
            'skill1':request.form.get('skill1'),
            'skill2':request.form.get('skill2'),
            'skill3':request.form.get('skill3'),
            'skill4':request.form.get('skill4')
        }
        if email:
            
            collection.update_one({'Email': email}, {'$set': updated_data})

        return redirect(url_for('auth.view_profile'))

    
    return redirect(url_for('auth.view_profile'))



@ auth.route('/cancle', methods=['POST', 'GET'])
def cancle():
    role=session['Job']
    job=role.lower()
    if job =='admin':
        return redirect(url_for('auth.view_profile'))
    else:
       return  redirect(url_for('auth.view_profile'))

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

            
        image = Image.open(file)

        image.thumbnail(THUMBNAIL_SIZE)

        # Save thumbnail to a bytes 
        thumb_io = io.BytesIO()
        image.save(thumb_io, format=image.format or 'JPEG')
        thumb_data = thumb_io.getvalue()
       
        image_doc = {
            'image_name': file.filename,
            'image_path': save_path,
            'thumbnail': Binary(thumb_data)
        }
        session['profile_image'] = {
            'image_name': file.filename,
            'image_path': save_path,
            'thumbnail': thumb_data
        }
        email = session['user_id']
       
        collection.update_one({'Email': email}, {'$set': {'profile_image': image_doc}})
        
    return redirect(url_for('auth.update_profile')) 



@auth.route('profile_image')
def profile_image():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    email = session['user_id']
    user = collection.find_one({'Email': email})

    if user and 'profile_image' in user:
        image_data = user['profile_image']['thumbnail']
        return send_file(io.BytesIO(image_data), mimetype='image/jpeg')

    return redirect(url_for('static', filename='default.jpg'))
 
