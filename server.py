import RPi.GPIO as GPIO
from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import time
import requests
import subprocess
import re

RELAY_PIN = 27      # GPIO27 for lamp
PROJECTOR_PIN = 18  # GPIO18 for projector
DHT_PIN = board.D4  # GPIO4 for DHT11 sensor

app = Flask(__name__)
CORS(app)  # Enable CORS for all origins

GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)
GPIO.output(RELAY_PIN, GPIO.LOW)  # Relay off
GPIO.setup(PROJECTOR_PIN, GPIO.OUT)
GPIO.output(PROJECTOR_PIN, GPIO.LOW)  # Projector off

# Variables to hold sensor data
sensor_data = {"temperature": None, "humidity": None}
data_url = "https://temp.aiiot.website/data.php"
domain_url = "https://temp.aiiot.website/domain.php"  # Update this with the correct URL for your server

def start_localtunnel():
    try:
        command = ['lt', '--port', '5000', '--subdomain', 'saltunnelme']
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output = result.stdout + result.stderr

        # Log the complete output of the lt command
        print(f"Localtunnel command output: {output}")

        # Extract the localtunnel URL using regex
        match = re.search(r'https://[a-zA-Z0-9-]+\.loca\.lt', output)
        if match:
            localtunnel_url = match.group(0)
            print(f"Localtunnel URL: {localtunnel_url}")

            try:
                # Send the domain to the PHP server
                response = requests.post(domain_url, data={"domain": localtunnel_url})
                if response.status_code == 200:
                    print(f"Domain sent successfully: {localtunnel_url}")
                else:
                    print(f"Failed to send domain: {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"An error occurred while sending domain: {e}")
        else:
            print("Failed to find localtunnel URL")
    except Exception as e:
        print(f"Error starting LocalTunnel: {e}")

# Start a background thread to read the sensor and send data
sensor_thread = threading.Thread(target=read_dht_sensor)
sensor_thread.daemon = True
sensor_thread.start()

# Start localtunnel and send the domain (run once when the server starts)
start_localtunnel()

@app.route('/control', methods=['POST', 'OPTIONS'])
def control():
    if request.method == 'OPTIONS':
        return jsonify({"status": "success"}), 200
    elif request.method == 'POST':
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
                print("Turning projector OFF")

        return jsonify({"status": "success"}), 200

@app.route('/sensor', methods=['GET'])
def get_sensor_data():
    return jsonify(sensor_data), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
