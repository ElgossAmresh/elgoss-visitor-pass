from deepface import DeepFace
import cv2
import os
import numpy as np
import datetime

from flask import Blueprint, jsonify, render_template
from models.database import collection, intern_db

intern = Blueprint('intern', __name__)

# Face detection
def detect_face_with_box(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    return faces, frame



# Main route to match faces
@intern.route('/match_face', methods=['GET'])
def match_face():
    print("📷 Opening camera...")
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    captured_frame = None

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Failed to read frame.")
            break

        faces, frame_with_box = detect_face_with_box(frame)
        cv2.imshow("🎥 Camera - Auto Capture on Face Detection", frame_with_box)

        cv2.waitKey(1)
        if len(faces) > 0:
            captured_frame = frame.copy()
            print(" Face detected & auto-captured.")
            break

    cap.release()
    cv2.destroyAllWindows()

    if captured_frame is None:
        return jsonify({"status": "failed", "message": "No face captured."})

    # Optional: Show the captured image briefly
    cv2.imshow(" Captured Frame", captured_frame)
    cv2.waitKey(1000)
    cv2.destroyAllWindows()
    
   

    matched_users = []

    for user in collection.find():
        print("Processing user:", user.get("email", "unknown"))

        profile_data = user.get("profile_image")
        if not isinstance(profile_data, dict):
            print(" Invalid profile_image format")
            continue

        image_path = profile_data.get("image_path")
        image_name = profile_data.get("image_name")

        if not image_path or not os.path.exists(image_path):
            print(f" Missing or invalid image: {image_name}")
            continue

        print(f"Valid image path: {image_path}")
        # Proceed with face matching...

       

        try:
            result = DeepFace.verify(
                img1_path=image_path,
                img2_path=captured_frame,
                model_name='ArcFace',
                detector_backend='opencv',
                enforce_detection=True
            )

            if result["verified"]:
                matched_filename = os.path.basename(image_path)  # e.g., rahul.jpg
                print(f" Match found with:+++++++++++++++++++++++++ {matched_filename}")

                # Find user document from MongoDB using image_name
                user_doc = collection.find_one({
                    "profile_image.image_name": matched_filename
                })
                # print(f" User document found>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>: {user_doc}")
                if user_doc:
                    user_id = user_doc["_id"]
                    Name = user_doc.get("Name")
                    Email=user_doc.get("Email")
                    print(f" User ID: {user_id}, Email: {Name}")
                    now = datetime.datetime.now()
                    intime = now.strftime("%H:%M:%S")        # "14:25:30"
                    date = now.strftime("%Y-%m-%d")          # "2025-06-19"

                    # Insert attendance entry
                    intern_db.insert_one({
                        "_id": user_id,
                        "Email": Email,
                        "Name": Name,
                        "Status": "Present",
                        "In_time": intime,
                        "Today_date": date
                    })

                    print(f" Attendance recorded for user ID:>>>>>>>>>>>>>>>>>>>>>>> {user_id}")
                else:
                    print(f" No user found with image: {matched_filename}")

                    
                    break

        except Exception as e:
            print(f" DeepFace error with {image_path}: {e}")

    if matched_users:
        return jsonify({
            "status": "success",
            "match_found": True,
            "matches": matched_users
        })

    print(" No match found in folder.")
    return jsonify({
        "status": "success",
        "match_found": False,
        "message": "No matching face found in folder images."
    })

# Attendance merge view
@intern.route('/merged_attendance',methods=['GET','POST'])
def merged_attendance():
    print("Merging attendance data...")
   
    results=intern_db.find()
    merged_data = list(results)
    
    return render_template("attendance_table.html", list=merged_data)
