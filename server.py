import RPi.GPIO as GPIO
from flask import Flask, request, jsonify
from flask_cors import CORS
import board
import adafruit_dht
import threading
import time
import requests
from flask_socketio import SocketIO, emit

# Initialize the Flask app and SocketIO with eventlet support for WebSockets
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Enable CORS for specific origins
CORS(app, resources={r"/*": {"origins": [
    "https://smartclass.dux.aiiot.center", 
    "http://smartclass.dux.aiiot.center", 
    "https://www.smartclass.dux.aiiot.center", 
    "http://www.smartclass.dux.aiiot.center"]}})

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

# Function to read the DHT sensor and send data to clients via WebSocket
def read_dht_sensor():
    while True:
        try:
            temperature_c = dht_sensor.temperature
            humidity = dht_sensor.humidity
            
            # Send sensor data via WebSocket to connected clients
            if temperature_c is not None and humidity is not None:
                sensor_data = {
                    "temperature": temperature_c,
                    "humidity": humidity,
                }
                socketio.emit('sensor_data', sensor_data)  # Emit data to all clients
                print(f"Data sent: {sensor_data}")
            else:
                print("Failed to read sensor data")

        except RuntimeError as error:
            print(f"Runtime error: {error}")
        except Exception as e:
            print(f"An error occurred: {e}")
        
        time.sleep(10)  # Update every 10 seconds

# Start a background thread to read the sensor and send data
sensor_thread = threading.Thread(target=read_dht_sensor)
sensor_thread.daemon = True
sensor_thread.start()

# Flask routes
@app.route('/control', methods=['POST', 'OPTIONS'])
def control():
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

# Start the SocketIO server with eventlet support
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
