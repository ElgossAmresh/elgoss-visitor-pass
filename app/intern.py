import os
 # Disable MSMF on Windows
import time
from deepface import DeepFace
import cv2
import numpy as np
import datetime, threading
from flask import Blueprint, jsonify, render_template, Response,request
from models.database import collection, intern_db
from app.camera_manager import release_camera
intern = Blueprint('intern', __name__)

# Global variables()
lock = threading.Lock()
# captured_frame = None
# face_captured = False




# Face detection
def detect_face_with_box(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
    return faces, frame

# Live video generator
def generate_frames():
    os.environ["OPENCV_VIDEOIO_PRIORITY_MSMF"] = "0" 
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        print("Retrying camera initialization...")
        camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    print("Starting video stream...............................................")
    global captured_frame, face_captured

    while True:
        if not camera.isOpened():
            print("Camera not opened.")
            break

        success, frame = camera.read()
        cv2.imshow("Live", frame)
        if not success or frame is None:
            print("Frame not read properly.")
            continue

        try:
            print ("Processing frame..............................................................................")
            faces, boxed_frame = detect_face_with_box(frame)
            if len(faces) > 0:
                print("Face detected. Pausing for 5 seconds...")
                time.sleep(0)

                # Optional: Reinitialize camera
                camera.release()
                time.sleep(5)  # Small delay before restart
                camera = cv2.VideoCapture(0)
                if not camera.isOpened():
                    print("Retrying camera initialization...")
                    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW) 
                continue
           

            ret, jpeg = cv2.imencode('.jpg', boxed_frame)
            match_face(boxed_frame)
            if not ret:
                continue

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
        except Exception as e:
            print("Streaming error:", e)
            continue



# Live video stream
@intern.route('/video_feed_intern')
def video_feed_intern():
    print("Video feed route called+++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Face match route
# @intern.route('/match_face', methods=['GET'])
def match_face(boxed_frame):
    print(boxed_frame)
    

    frame_copy = boxed_frame
    #     captured_frame = None
    #     face_captured = False

    matched_users = []

    for user in collection.find():
        profile = user.get("profile_image", {})
        if not isinstance(profile, dict):
            print(" profile_image is not a dict:", profile)
            
            continue  # skip this user

        image_path = profile.get("image_path")
        if not image_path or not os.path.exists(image_path):
            continue

        try:
            result = DeepFace.verify(
                img1_path=image_path,
                img2_path=frame_copy,
                model_name='ArcFace',
                detector_backend='opencv',
                enforce_detection=True
            )

            if result.get("verified"):
                matched_users.append({
                    "Name": user.get("Name", "Unknown"),
                    "Email": user.get("Email", "")
                })

                # Save attendance
                now = datetime.datetime.now()
                intern_db.insert_one({
                    "_id": user["_id"],
                    "Name": user.get("Name"),
                    "Email": user.get("Email"),
                    "Status": "Present",
                    "In_time": now.strftime("%H:%M:%S"),
                    "Today_date": now.strftime("%Y-%m-%d")
                })
                break

        except Exception as e:
            print(f"DeepFace error with {image_path}: {e}")

    if matched_users:
      return "match found"

# Render camera & match page
@intern.route('/attendance_camera', methods=['GET', 'POST'])
def attendance_camera():
    return render_template("attendance_camera.html")

# View all merged attendance
@intern.route('/merged_attendance', methods=['GET', 'POST'])
def merged_attendance():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    query = {}

   

    # Filter by date range if provided
    if start_date and end_date:
        query['Date'] = {
            "$gte": start_date,
            "$lte": end_date
        }
    data = list(intern_db.find(query))
   
    return render_template("attendance_table.html", list=data)
@intern.route('/release_camera', methods=['GET', 'POST'])
def release_camera():
    release_camera()
    return 0