import cv2

camera = None

def get_camera():

    global camera
    try:
        if camera is None or not camera.isOpened():
            camera = cv2.VideoCapture(0)
            if not camera.isOpened():
                raise Exception("Unable to open the camera.")
    except Exception as e:
        print(f"[ERROR] Failed to get camera: {e}")
        camera = None
    return camera

def release_camera():
    global camera
    try:
        if camera is not None:
            camera.release()
            cv2.destroyAllWindows()
            camera = None
    except Exception as e:
        print(f"[ERROR] Failed to release camera: {e}")


