from deepface import DeepFace
import cv2
import os
import numpy as np
import datetime
from flask import Blueprint, jsonify

intern = Blueprint('intern', __name__)


def detect_face_with_box(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    return faces, frame


@intern.route('/match_face', methods=['GET'])
def match_face():
    print("📷 Opening camera...")
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    captured_frame = None
    face_detected = False

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to read frame.")
            break

        faces, frame_with_box = detect_face_with_box(frame)
        cv2.imshow("Camera - Detecting Face", frame_with_box)

        if len(faces) > 0:
            print("🧠 Face detected! Capturing image...")
            captured_frame = frame.copy()
            
            face_detected = True
            break
        
        if cv2.waitKey(1) & 0xFF == 27:
            print("❌ Exit requested.")
            cap.release()
            cv2.destroyAllWindows()
            return jsonify({"status": "cancelled", "message": "ESC pressed"})

    cap.release()
    cv2.destroyAllWindows()

    if not face_detected or captured_frame is None:
        return jsonify({"status": "failed", "message": "No face captured."})

    # Directory containing face images
    folder_path = os.path.join("static", "captured_images")
    matched_users = []
    cv2.imshow("Captured Face", cv2.resize(captured_frame, (300, 300)))
    print("📷 Showing captured image. Press any key to continue...")
    
    cv2.destroyWindow("Captured Face")
    for filename in os.listdir(folder_path):
        if not filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            continue

        image_path = os.path.join(folder_path, filename)
        db_img = cv2.imread(image_path)
        
        if db_img is None:
            print(f"⚠️ Could not read image: {filename}")
            continue

        try:
            print(f"🔍 Matching with {filename}...")
            result = DeepFace.verify(
                img1_path=db_img,
                img2_path=captured_frame,
                model_name='ArcFace',
                detector_backend='opencv',
                enforce_detection=True
            )

            if result['verified']:
                now = datetime.datetime.now()
                print(f"✅ Match found: {filename} at {now}")
                matched_users.append({
                    "matched_user": filename,
                    "distance": round(result['distance'], 4),
                    "timestamp": now.strftime("%Y-%m-%d %H:%M:%S")
                })

        except Exception as e:
            print(f"❌ DeepFace error with {filename}: {e}")

    if matched_users:
        return jsonify({
            "status": "success",
            "match_found": True,
            "matches": matched_users
        })

    print("🔍 No match found in folder.")
    return jsonify({
        "status": "success",
        "match_found": False,
        "message": "No matching face found in folder images."
    })
