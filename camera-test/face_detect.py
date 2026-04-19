import cv2
import face_recognition
from face_embedding import load_known_faces
def gstreamer_pipeline(sensor_id=0, flip_method=0):
    return (
        "nvarguscamerasrc sensor-id=%d ! "
        "video/x-raw(memory:NVMM), width=1280, height=720, framerate=30/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=640, height=360, format=BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=BGR ! appsink"
        % (sensor_id, flip_method)
    )

def main():
    known_encodings, known_names = load_known_faces()
    # Load the pre-installed Haar Cascade for face detection
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    # Initialize the camera using the GStreamer pipeline
    cap = cv2.VideoCapture(0) 
    #cap = cv2.VideoCapture(gstreamer_pipeline(flip_method=2), cv2.CAP_GSTREAMER)

    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    print("Camera Live! Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

        cv2.imshow("Jetson Face Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

