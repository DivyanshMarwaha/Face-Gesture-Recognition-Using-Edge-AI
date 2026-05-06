import cv2
import serial
import time
import numpy as np

# ===== SERIAL SETUP =====
arduino = serial.Serial('COM3', 9600)
time.sleep(2)

# ===== FACE MODEL =====
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)

cap = cv2.VideoCapture(0)

# ===== HISTORY BUFFER (for smoothing) =====
gesture_history = []
HISTORY_SIZE = 5

prev_center_x = 0
prev_time = time.time()

def get_stable_gesture(new_gesture):
    gesture_history.append(new_gesture)
    if len(gesture_history) > HISTORY_SIZE:
        gesture_history.pop(0)

    return max(set(gesture_history), key=gesture_history.count)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    h, w, _ = frame.shape
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    gesture = "NONE"
    confidence = 0.0

    if len(faces) > 0:

        # Take largest face (main subject)
        faces = sorted(faces, key=lambda f: f[2]*f[3], reverse=True)
        (x, y, fw, fh) = faces[0]

        center_x = x + fw // 2
        area = fw * fh

        cv2.rectangle(frame, (x,y), (x+fw,y+fh), (255,0,0), 2)

        # ===== NORMALIZED FEATURES =====
        norm_area = area / (w * h)
        norm_x = center_x / w

        # ===== GESTURE LOGIC =====

        # CLOSE / FAR
        if norm_area > 0.15:
            gesture = "CLOSE"
            confidence = min(1.0, norm_area * 2)

        elif norm_area < 0.03:
            gesture = "FAR"
            confidence = min(1.0, (0.05 - norm_area) * 10)

        # LEFT / RIGHT
        elif norm_x < 0.35:
            gesture = "LEFT"
            confidence = 1.0 - norm_x

        elif norm_x > 0.65:
            gesture = "RIGHT"
            confidence = norm_x

        # ===== SWIPE DETECTION =====
        current_time = time.time()
        speed = abs(center_x - prev_center_x) / max(0.001, (current_time - prev_time))

        if speed > 800:
            gesture = "SWIPE"
            confidence = min(1.0, speed / 1500)

        prev_center_x = center_x
        prev_time = current_time

    # ===== SMOOTHING =====
    stable_gesture = get_stable_gesture(gesture)

    # ===== SERIAL PROTOCOL =====
    message = f"{stable_gesture},{confidence:.2f}\n"
    arduino.write(message.encode())

    # ===== UI =====
    cv2.putText(frame, f"Gesture: {stable_gesture}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

    cv2.putText(frame, f"Confidence: {confidence:.2f}", (10, 70),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,200,255), 2)

    cv2.imshow("Edge AI Face System", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
