from flask import Blueprint, render_template, request, Response
import cv2
import datetime
import os
import time
from app.camera_manager import get_camera,release_camera
from app.ocr import extract_card_details

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
# def gen_frame():
     
#     while True:
#         success, frame = camera.read()
#         if not success:
#             break
#         else:
#             ret, buffer = cv2.imencode('.jpg', frame)
#             frame = buffer.tobytes()

#             yield (b'--frame\r\n'
#                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


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
        # remaining = max(0, int(countdown_duration - elapsed_time))

        # # Show countdown text on the video
        # cv2.putText(frame, f"Show your card - {remaining}s", (30, 40),
        #             cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # # After countdown, detect card and capture
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
    if captured_data:
        approvedby = ""  
        return render_template('extract.html', data=captured_data, approvedby=approvedby)
    else:
        return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
   
 