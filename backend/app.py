import cv2
import numpy as np
import mediapipe as mp
from flask import Flask, Response
from flask_cors import CORS  # Import CORS
from threading import Thread
from gtts import gTTS
import os
from playsound import playsound

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for all domains
CORS(app)

# Landmarks for left and right eye from the face mesh
LEFT_EYE = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
RIGHT_EYE = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]

# Initialize MediaPipe Face Mesh and Face Detection
mediapipe_face_mesh = mp.solutions.face_mesh
face_mesh = mediapipe_face_mesh.FaceMesh(max_num_faces=1, min_detection_confidence=0.6, min_tracking_confidence=0.7)
mp_face_mesh = mp.solutions.face_mesh
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

face_detection = mp_face_detection.FaceDetection(min_detection_confidence=0.5)

# Constants for blink and yawn detection
EYE_AR_THRESH = 0.25  # Threshold for eye closure (blinking)
EYE_AR_CONSEC_FRAMES = 3  # Consecutive frames for blink detection
YAWN_THRESH = 20  # Threshold for yawn detection
GAZE_THRESH = 0.1  # Threshold for gaze direction detection

alarm_status2 = False
TOTAL_BLINKS = 0
BLINK_COUNTER = 0  # Counter to track consecutive frames below the EAR threshold

def eye_aspect_ratio(eye):
    A = np.linalg.norm(eye[1] - eye[5])
    B = np.linalg.norm(eye[2] - eye[4])
    C = np.linalg.norm(eye[0] - eye[3])
    return (A + B) / (2.0 * C)

def final_ear(landmarks, img, x1, y1):
    leftEye = np.array([(landmarks[i].x * img.shape[1] + x1, landmarks[i].y * img.shape[0] + y1) for i in range(33, 42)])
    rightEye = np.array([(landmarks[i].x * img.shape[1] + x1, landmarks[i].y * img.shape[0] + y1) for i in range(263, 272)])
    leftEAR = eye_aspect_ratio(leftEye)
    rightEAR = eye_aspect_ratio(rightEye)
    ear = (leftEAR + rightEAR) / 2.0
    return (ear, leftEye, rightEye)

def lip_distance(landmarks, img, x1, y1):
    top_lip = np.concatenate([
        [(landmarks[i].x * img.shape[1] + x1, landmarks[i].y * img.shape[0] + y1) for i in range(13, 15)],
        [(landmarks[i].x * img.shape[1] + x1, landmarks[i].y * img.shape[0] + y1) for i in range(78, 80)]
    ])
    low_lip = np.concatenate([
        [(landmarks[i].x * img.shape[1] + x1, landmarks[i].y * img.shape[0] + y1) for i in range(14, 16)],
        [(landmarks[i].x * img.shape[1] + x1, landmarks[i].y * img.shape[0] + y1) for i in range(308, 310)]
    ])
    top_mean = np.mean(top_lip, axis=0)
    low_mean = np.mean(low_lip, axis=0)
    return abs(top_mean[1] - low_mean[1])

def euclidean_distance(point, point1):
    x, y = point.x, point.y
    x1, y1 = point1.x, point1.y
    distance = np.sqrt((x1 - x)**2 + (y1 - y)**2)
    return distance

def blink_ratio(image, landmarks, right_indices, left_indices):
    right_eye_landmarks = [landmarks[i] for i in right_indices]
    left_eye_landmarks = [landmarks[i] for i in left_indices]
    
    right_eye_landmark1 = right_eye_landmarks[0]
    right_eye_landmark2 = right_eye_landmarks[8]
    right_eye_landmark3 = right_eye_landmarks[12]
    right_eye_landmark4 = right_eye_landmarks[4]
    
    left_eye_landmark1 = left_eye_landmarks[0]
    left_eye_landmark2 = left_eye_landmarks[8]
    left_eye_landmark3 = left_eye_landmarks[12]
    left_eye_landmark4 = left_eye_landmarks[4]
    
    right_eye_horizontal_distance = euclidean_distance(right_eye_landmark1, right_eye_landmark2)
    right_eye_vertical_distance = euclidean_distance(right_eye_landmark3, right_eye_landmark4)
    left_eye_vertical_distance = euclidean_distance(left_eye_landmark3, left_eye_landmark4)
    left_eye_horizontal_distance = euclidean_distance(left_eye_landmark1, left_eye_landmark2)
    
    right_eye_ratio = right_eye_horizontal_distance / right_eye_vertical_distance
    left_eye_ratio = left_eye_horizontal_distance / left_eye_vertical_distance
    
    eyes_ratio = (right_eye_ratio + left_eye_ratio) / 2
    return eyes_ratio

def gaze_direction(leftEye, rightEye):
    # Compute the center of the eye
    left_pupil = np.mean(leftEye[1:3], axis=0)
    right_pupil = np.mean(rightEye[1:3], axis=0)

    # Compute gaze direction based on pupil positions
    left_eye_x = np.mean(leftEye[:, 0])
    right_eye_x = np.mean(rightEye[:, 0])
    eye_width = right_eye_x - left_eye_x
    avg_pupil_x = (left_pupil[0] + right_pupil[0]) / 2

    if avg_pupil_x < left_eye_x + GAZE_THRESH * eye_width:
        return "Looking Left"
    elif avg_pupil_x > right_eye_x - GAZE_THRESH * eye_width:
        return "Looking Right"
    else:
        return "Looking Center"

# Function to play alarm for yawn
def alarm(message):
    global alarm_status2
    if alarm_status2:
        # Save the text-to-speech audio file
        audio_path = "yawn_alert.mp3"
        tts = gTTS(text=message, lang='en')
        tts.save(audio_path)

        # Check if file exists before attempting to play
        if os.path.exists(audio_path):
            try:
                # Play the audio file
                playsound(audio_path)
            except Exception as e:
                print(f"Error playing sound: {e}")
        else:
            print(f"Audio file not found: {audio_path}")

        # Remove the audio file after playing
        if os.path.exists(audio_path):
            os.remove(audio_path)

def generate_frames():
    global alarm_status2, TOTAL_BLINKS, BLINK_COUNTER
    # Start video capture
    cap = cv2.VideoCapture(0)

    while True:
        ret, img = cap.read()
        if not ret:
            break

        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results_detection = face_detection.process(rgb_img)

        # Create a blank image for landmarks
        landmarks_img = np.zeros((img.shape[0], img.shape[1], 3), dtype=np.uint8)

        if results_detection.detections:
            for detection in results_detection.detections:
                bboxC = detection.location_data.relative_bounding_box
                ih, iw, _ = img.shape
                padding = 0.05  # Add padding around the face box
                x, y, w, h = int(bboxC.xmin * iw), int(bboxC.ymin * ih), int(bboxC.width * iw), int(bboxC.height * ih)

                # Adjust bounding box with padding
                x1 = max(0, x - int(padding * w))
                y1 = max(0, y - int(padding * h))
                x2 = min(iw, x + w + int(padding * w))
                y2 = min(ih, y + h + int(padding * h))

                face_roi = img[y1:y2, x1:x2]
                rgb_face_roi = cv2.cvtColor(face_roi, cv2.COLOR_BGR2RGB)
                results_mesh = face_mesh.process(rgb_face_roi)

                if results_mesh.multi_face_landmarks:
                    for landmarks in results_mesh.multi_face_landmarks:
                        # Draw landmarks on landmarks_img
                        mp_drawing.draw_landmarks(landmarks_img, landmarks, mp_face_mesh.FACEMESH_TESSELATION)

                        # Calculate eye aspect ratio (EAR)
                        ear, leftEye, rightEye = final_ear(landmarks.landmark, face_roi, x1, y1)

                        # Blink detection logic
                        eyes_ratio = blink_ratio(img, landmarks.landmark, RIGHT_EYE, LEFT_EYE)
                        if eyes_ratio > 3:
                            BLINK_COUNTER += 1
                        else:
                            if BLINK_COUNTER > 4:
                                TOTAL_BLINKS += 1
                            BLINK_COUNTER = 0

                        # Calculate lip distance for yawn detection
                        distance = lip_distance(landmarks.landmark, face_roi, x1, y1)
                        print(f"Detected lip distance: {distance}")  # Debugging line
                        if distance > YAWN_THRESH:
                            cv2.putText(img, "Yawn Alert", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                            if not alarm_status2:
                                alarm_status2 = True
                                t = Thread(target=alarm, args=("Yawn Detected!",))
                                t.daemon = True
                                t.start()
                        else:
                            alarm_status2 = False

                        # Determine gaze direction
                        gaze = gaze_direction(leftEye, rightEye)
                        cv2.putText(img, gaze, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

        # Display blink count on the main image
        cv2.putText(img, f"Total Blinks: {TOTAL_BLINKS}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        # Create a collage with landmarks overlaid
        collage = np.hstack((img, landmarks_img))

        # Convert the image to JPEG for streaming
        ret, buffer = cv2.imencode('.jpg', collage)
        if not ret:
            continue
        frame = buffer.tobytes()

        # Yield the frame in multipart format
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

    cap.release()
from flask import jsonify

# Modify the alarm function to return a response to the React frontend
def alarm(message):
    global alarm_status2
    if alarm_status2:
        # Save the text-to-speech audio file
        audio_path = "yawn_alert.mp3"
        tts = gTTS(text=message, lang='en')
        tts.save(audio_path)

        # Check if file exists before attempting to play
        if os.path.exists(audio_path):
            try:
                # Play the audio file
                playsound(audio_path)
            except Exception as e:
                print(f"Error playing sound: {e}")
        else:
            print(f"Audio file not found: {audio_path}")

        # Remove the audio file after playing
        if os.path.exists(audio_path):
            os.remove(audio_path)

        # Send a response to React frontend to trigger sound playback
        return jsonify({"alarm": True})
    return jsonify({"alarm": False})

@app.route('/yawn-detected', methods=['POST'])
def yawn_detected():
    global alarm_status2
    if alarm_status2:
        return alarm("Yawn Detected!")
    return jsonify({"alarm": False})

@app.route('/video')
def video():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
