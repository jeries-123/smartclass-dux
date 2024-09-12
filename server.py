import RPi.GPIO as GPIO
from flask import Flask, request, jsonify
from flask_cors import CORS
import board
import adafruit_dht
import threading
import time
import requests
from flask_socketio import SocketIO
import eventlet
import eventlet.wsgi

# Initialize the Flask app and SocketIO
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Enable CORS for specific origins and allow the bypass-tunnel-reminder header
CORS(app, resources={r"/*": {"origins": ["https://smartclass.dux.aiiot.center", 
                                         "http://smartclass.dux.aiiot.center", 
                                         "https://www.smartclass.dux.aiiot.center", 
                                         "http://www.smartclass.dux.aiiot.center"],
                            "allow_headers": ["Content-Type", "bypass-tunnel-reminder"]}})

RELAY_PIN = 27      # GPIO27 for lamp
PROJECTOR_PIN = 18  # GPIO18 for projector
DHT_PIN = board.D4  # GPIO4 for DHT11 sensor

GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)
GPIO.output(RELAY_PIN, GPIO.LOW)  # Relay off
GPIO.setup(PROJECTOR_PIN, GPIO.OUT)
GPIO.output(PROJECTOR_PIN, GPIO.LOW)  # Projector off

# Initialize the DHT sensor
dht_sensor = adafruit_dht.DHT11(DHT_PIN)

# Function to read the DHT sensor and send data to the server
def read_dht_sensor():
    while True:
        try:
            temperature_c = dht_sensor.temperature
            humidity = dht_sensor.humidity
            
            # Prepare sensor data
            sensor_data = {
                "temperature": temperature_c,
                "humidity": humidity,
            }
            
            # Send data to the server
            response = requests.post("https://smartclass.dux.aiiot.center/data.php", data=sensor_data)
            if response.status_code == 200:
                print(f"Data sent successfully: {sensor_data}")
            else:
                print(f"Failed to send data: {response.status_code}")
                
        except RuntimeError as error:
            print(f"Runtime error: {error}")
        except Exception as e:
            print(f"An error occurred: {e}")
        
        time.sleep(100)

# Start a background thread to read the sensor and send data
sensor_thread = threading.Thread(target=read_dht_sensor)
sensor_thread.daemon = True
sensor_thread.start()

# WebRTC signaling: Handle WebSocket connections for screen sharing
@socketio.on('offer')
def handle_offer(data):
    # Relay offer to the Raspberry Pi or other client
    socketio.emit('offer', data, broadcast=True, include_self=False)

@socketio.on('answer')
def handle_answer(data):
    # Relay answer back to the browser (screen sharer)
    socketio.emit('answer', data, broadcast=True, include_self=False)

@socketio.on('candidate')
def handle_candidate(data):
    # Relay ICE candidate information
    socketio.emit('candidate', data, broadcast=True, include_self=False)

# GPIO control route
@app.route('/control', methods=['POST', 'OPTIONS'])
def control():
    if request.method == 'OPTIONS':
        # Handle preflight CORS request
        response = jsonify({"status": "CORS preflight OK"})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, bypass-tunnel-reminder')
        return response, 200
    elif request.method == 'POST':
        # Handle actual POST request
        data = request.form
        device = data.get('device')
        action = data.get('action')

        if device == 'lamp':
            if action == 'on':
                GPIO.output(RELAY_PIN, GPIO.HIGH)  # Relay on
                print("Turning relay ON")
            elif action == 'off':
                GPIO.output(RELAY_PIN, GPIO.LOW)  # Relay off
                print("Turning relay OFF")
        elif device == 'projector':
            if action == 'on':
                GPIO.output(PROJECTOR_PIN, GPIO.HIGH)  # Projector on
                print("Turning projector ON")
            elif action == 'off':
                GPIO.output(PROJECTOR_PIN, GPIO.LOW)  # Projector off

        return jsonify({"status": "success"}), 200

# Sensor data route//
@app.route('/sensor', methods=['GET'])
def get_sensor_data():
    try:
        temperature_c = dht_sensor.temperature
        humidity = dht_sensor.humidity
        if temperature_c is None or humidity is None:
            raise RuntimeError("Failed to read sensor data")
        return jsonify({"temperature": temperature_c, "humidity": humidity}), 200
    except RuntimeError as error:
        return jsonify({"error": "DHT sensor read failed", "message": str(error)}), 500
    except Exception as e:
        return jsonify({"error": "Unexpected error", "message": str(e)}), 500

# Use eventlet to run the Flask app
if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 5000)), app)
