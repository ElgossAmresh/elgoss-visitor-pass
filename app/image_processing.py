from flask import Blueprint, render_template, request, Response
import cv2
import datetime
import os
import time
from bson.binary import Binary
from bson import Binary

from app.camera_manager import get_camera,release_camera
from app.ocr import extract_card_details
from models.database import visitors_status
def record(out):
    global rec, camera
    while rec:
        success, frame = camera.read()
        if success:
            out.write(frame)
        time.sleep(0.05)
   
image_processing = Blueprint('image_processing', __name__)

global pan_data,frame
pan_data=None
frame=None
capture = 0
camera = get_camera()



def gen_frames():
    global captured_image, captured_data
    captured_data = None
    captured_image = None
    start_time = time.time()
    countdown_duration = 10.0  # seconds
    
    while True:
        success, frame = camera.read()
        if not success:
            break

        elapsed_time = time.time() - start_time
       
        if elapsed_time >= countdown_duration and captured_image is None:
            now = datetime.datetime.now()
            filename = os.path.join('shots', f"shot_{now.strftime('%Y%m%d_%H%M%S')}.png")
            cv2.imwrite(filename, frame)
            captured_image = filename
            captured_data = extract_card_details(filename)
            release_camera()
            print(f"[INFO] Card captured and saved to {filename}")
            break

        # Encode the current frame for streaming
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@image_processing.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@image_processing.route('/show_captured')
def show_captured():
    
   
    # global captured_image, captured_data
    # if captured_data:
        approvedby = ""  
        return render_template('extract.html', data=captured_data, approvedby=approvedby)
    # else:
    #     return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
    



def gen_frame_image():
    global captured_image, current_uid
    captured_image = None
    start_time = time.time()
    countdown_duration = 10.0  # seconds
    print(f"gen frame capture")
    while True:
        success, frame = camera.read()
        if not success:
            break


        elapsed_time = time.time() - start_time

        if elapsed_time >= countdown_duration and captured_image is None:
            now = datetime.datetime.now()
            filename = os.path.join('shots', f"shot_{now.strftime('%Y%m%d_%H%M%S')}.png")
            cv2.imwrite(filename, frame)

            with open(filename, 'rb') as f:
                image_data = f.read()

            # Check if UID exists in MongoDB
            existing_record = visitors_status.find_one({"uid": current_uid})

            if existing_record:
                # Update existing document with new image and timestamp
                visitors_status.update_one(
                    {"uid": current_uid},
                    {
                        "$set": {
                            "filename": filename,
                            "image": bson.Binary(image_data),
                            "timestamp": now
                        }
                    }
                )
                print(f"[INFO] Updated existing record for UID {current_uid}.")
            else:
                # Insert new record if UID not found
                visitors_status.insert_one({
                    "uid": current_uid,
                    "filename": filename,
                    "image": bson.Binary(image_data),
                    "timestamp": now,
                })
                print(f"[INFO] Inserted new record for UID {current_uid}.")

            captured_image = filename
            release_camera()
            break

        # Encode frame
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')



@image_processing.route('/capture_image', methods=['POST'])
def capture_image():
    uid = request.form.get('uid')  # Get UID from form
    global current_uid
    current_uid = uid
    print(f"[INFO] Capture request received for UID: {uid}")
    return Response(gen_frame_image(), mimetype='multipart/x-mixed-replace; boundary=frame')
