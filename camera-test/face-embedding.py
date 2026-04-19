import cv2
import face_recognition
import numpy as np
import os

DB_PATH = "face_db"
if not os.path.exists(DB_PATH): os.makedirs(DB_PATH)

def load_known_faces():
    known_encodings, known_names = [], []
    for file in os.listdir(DB_PATH):
        if file.endswith(".npy"):
            known_encodings.append(np.load(os.path.join(DB_PATH, file)))
            known_names.append(file.replace(".npy", ""))
    return known_encodings, known_names

def gstreamer_pipeline(flip_method=2):
    return (
        "nvarguscamerasrc ! video/x-raw(memory:NVMM), width=1280, height=720, framerate=30/1 ! "
        "nvvidconv flip-method=%d ! video/x-raw, width=640, height=360, format=BGRx ! "
        "videoconvert ! video/x-raw, format=BGR ! appsink drop=True" % flip_method
    )

def main():
    known_encodings, known_names = load_known_faces()
    #cap = cv2.VideoCapture(gstreamer_pipeline(), cv2.CAP_GSTREAMER)
    cap = cv2.VideoCapture(0)
    input_mode = False
    current_name = ""
    last_encoding = None

    while True:
        ret, frame = cap.read()
        if not ret: break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        # Identification Logic
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            name, color = "UNKNOWN", (0, 0, 255)
            if known_encodings:
                matches = face_recognition.compare_faces(known_encodings, face_encoding, 0.5)
                if True in matches:
                    name, color = known_names[matches.index(True)], (0, 255, 0)
            
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            last_encoding = face_encoding

        # GUI Overlays
        if input_mode:
            cv2.rectangle(frame, (50, 150), (590, 210), (0, 0, 0), -1)
            cv2.putText(frame, f"Enter Name: {current_name}_", (70, 190), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        else:
            cv2.putText(frame, "'S': Save Face | 'Q': Quit", (10, 340), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        cv2.imshow("Jetson AI - Full GUI", frame)
        key = cv2.waitKey(1) & 0xFF

        # Input Mode Handling
        if input_mode:
            if key == 13: # ENTER Key
                if current_name and last_encoding is not None:
                    np.save(os.path.join(DB_PATH, f"{current_name}.npy"), last_encoding)
                    known_encodings.append(last_encoding)
                    known_names.append(current_name)
                input_mode, current_name = False, ""
            elif key == 8: # BACKSPACE
                current_name = current_name[:-1]
            elif 32 <= key <= 126: # Regular Characters
                current_name += chr(key)
        elif key == ord('s'):
            if face_encodings: input_mode = True
        elif key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

