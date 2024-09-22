import cv2
import mediapipe as mp
import requests
from flask import Flask, render_template, Response, jsonify, request

app = Flask(__name__)

# For Mediapipe hand detection
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Track the last gesture to avoid repeated API calls
last_gesture = None

# Control device state
devices = {
    "lamp": "off",
    "projector": "off",
    "ac": "off"
}

# Route for the main page
@app.route('/')
def index():
    return render_template('index.html')

# API to fetch sensor data (temperature & humidity) from the remote API
@app.route('/sensor_data', methods=['GET'])
def get_sensor_data():
    try:
        # Fetch temperature and humidity data from the remote API
        url = 'https://smartclass.serveo.net/sensor_data'
        response = requests.get(url)
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            print(f"Error: Failed to fetch sensor data, status code: {response.status_code}")
            return jsonify({"error": "Failed to fetch sensor data"}), response.status_code
    except Exception as e:
        print(f"Error: Unable to reach the sensor data API: {str(e)}")
        return jsonify({"error": "Unable to reach the sensor data API"}), 502

# API to control devices via switch
@app.route('/control', methods=['POST'])
def control_device():
    device = request.form.get('device')
    action = request.form.get('action')
    
    if device in devices:
        devices[device] = action
        print(f"Device '{device}' set to '{action}'")
        # Send control request to the remote API (for actual control)
        send_control_request(device, action)
        return jsonify({"status": "success", "device": device, "action": action})
    else:
        return jsonify({"status": "error", "message": "Invalid device"}), 400

# Route to stream video with hand detection for lamp and projector control
@app.route('/video_feed/<device>')
def video_feed(device):
    return Response(generate_frames(device), mimetype='multipart/x-mixed-replace; boundary=frame')

# Function to capture video and detect hands for lamp or projector control
def generate_frames(device):
    global last_gesture

    cap = cv2.VideoCapture(0)  # Use the first camera (0)

    if not cap.isOpened():
        print("Error: Could not open video source.")
        return

    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            # Convert the frame to RGB for Mediapipe processing
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Process the frame with Mediapipe Hands
            result = hands.process(rgb_frame)

            if result.multi_hand_landmarks:
                for hand_landmarks in result.multi_hand_landmarks:
                    mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                    # Detect gesture: check thumb and index tip positions for "on" or "off"
                    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                    index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

                    # Determine gesture
                    gesture = "off" if thumb_tip.y > index_tip.y else "on"

                    # Only control device (lamp or projector) if the gesture changes
                    if gesture != last_gesture:
                        print(f"Gesture recognized for {device}: {gesture}")
                        send_control_request(device, gesture)  # Send control request to API
                        last_gesture = gesture

            # Encode the frame for streaming to the web
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            # Yield the frame to be displayed in the browser
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    # Release the video capture
    cap.release()

# Function to send device control request to the remote API
def send_control_request(device, action):
    try:
        # Sending a POST request to the remote control API
        url = 'https://smartclass.serveo.net/control'
        response = requests.post(url, data={'device': device, 'action': action})
        
        if response.status_code == 200:
            print(f"Device '{device}' set to '{action}' via API")
        else:
            print(f"Error: Unable to set '{device}' to '{action}' (status: {response.status_code})")
    except Exception as e:
        print(f"Error sending control request: {str(e)}")


if __name__ == '__main__':
    app.run(debug=True)
