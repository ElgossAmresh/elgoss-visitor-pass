
from flask import Flask, Response, render_template, redirect, url_for, request, send_from_directory
import cv2
import os
from datetime import datetime

app = Flask(__name__)

SAVE_DIR = "static/captured_images"
os.makedirs(SAVE_DIR, exist_ok=True)

cap = None  # Global camera reference

# ✅ Load Haar Cascade for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# ✅ Stream video with live face detection
def generate_frames():
    global cap
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        # Convert to grayscale for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

        if len(faces) > 0:
            (x, y, w, h) = faces[0]  # Only the first face
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Encode frame
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    cap.release()

# ✅ Routes
# @app.route("/")
# def index():
#     return render_template("index.html")

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/', methods=["POST"])
def scan():
    return render_template("test.html")

@app.route("/stop_camera", methods=["GET", "POST"])
def stop_camera():
    global cap
    if cap is not None:
        cap.release()
        cv2.destroyAllWindows()
    return redirect("/")

# ✅ Capture still image (no face detection here)
@app.route('/capture')
def capture():
    global cap
    if cap is None or not cap.isOpened():
        return "Camera is not open", 400

    success, frame = cap.read()
    if not success:
        return "Error capturing image", 500

    filename = f"captured_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    img_path = os.path.join(SAVE_DIR, filename)
    cv2.imwrite(img_path, frame)

    return filename

@app.route('/static/<filename>')
def get_image(filename):
    return send_from_directory(SAVE_DIR, filename)

# ✅ Run the server
if __name__ == '__main__':
    app.run(debug=True, port=5000)