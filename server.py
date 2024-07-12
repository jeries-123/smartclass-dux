from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import time
import requests
import subprocess
import re
import board  # Import board from adafruit_blinka
import digitalio  # Import digitalio from adafruit_blinka
import adafruit_dht  # Import Adafruit_DHT library for DHT sensor

RELAY_PIN = 27      # GPIO27 for lamp
PROJECTOR_PIN = 18  # GPIO18 for projector

app = Flask(__name__)
CORS(app)  # Enable CORS for all origins

# Initialize GPIO pins and DHT sensor
try:
    relay = digitalio.DigitalInOut(board.D27)
    relay.direction = digitalio.Direction.OUTPUT
    projector = digitalio.DigitalInOut(board.D18)
    projector.direction = digitalio.Direction.OUTPUT
    dht_sensor = adafruit_dht.DHT11(board.D4)  # GPIO4 for DHT11 sensor

except Exception as e:
    print(f"Error initializing GPIO or DHT sensor: {e}")

# Variables to hold sensor data
sensor_data = {"temperature": None, "humidity": None}
data_url = "https://temp.aiiot.website/data.php"
domain_url = "https://temp.aiiot.website/domain.php"  # Update this with your actual domain URL

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
def read_dht_sensor():
    global sensor_data
    while True:
        try:
            # Read temperature and humidity from DHT sensor
            temperature_c = dht_sensor.temperature
            humidity = dht_sensor.humidity

            # Update sensor data
            sensor_data = {"temperature": temperature_c, "humidity": humidity}

            # Post sensor data to your server
            response = requests.post(data_url, data=sensor_data)
            if response.status_code == 200:
                print("Sensor data sent successfully")
            else:
                print(f"Failed to send sensor data: {response.status_code}")

            time.sleep(60)  # Read sensor every 60 seconds
        except Exception as e:
            print(f"Error reading DHT sensor: {e}")
            time.sleep(10)  # Retry after 10 seconds if there's an error

# Start localtunnel and send the domain (run once when the server starts)
start_localtunnel()

# Start thread for reading sensor data
sensor_thread = threading.Thread(target=read_dht_sensor)
sensor_thread.daemon = True
sensor_thread.start()

# Define your Flask routes here
@app.route('/control', methods=['POST', 'OPTIONS'])
def control():
    # Your control logic here
    pass

@app.route('/sensor', methods=['GET'])
def get_sensor_data():
    return jsonify(sensor_data), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
