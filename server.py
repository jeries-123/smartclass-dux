import RPi.GPIO as GPIO
import socket
import ssl
from flask import Flask, request, jsonify
from flask_cors import CORS

RELAY_PIN = 27      # GPIO17 for lamp
PROJECTOR_PIN = 18  # GPIO18 for projector

app = Flask(__name__)
cors = CORS(app, resources={r"/control": {"origins": "https://temp.aiiot.website"}})

GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)
GPIO.output(RELAY_PIN, GPIO.LOW)  # Relay off
GPIO.setup(PROJECTOR_PIN, GPIO.OUT)
GPIO.output(PROJECTOR_PIN, GPIO.LOW)  # Projector off

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

if __name__ == '__main__':
    # Create SSL context and load certificates
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain(certfile='/home/pi/Desktop/smartclass-dux/server.crt', keyfile='/home/pi/Desktop/smartclass-dux/server.key')

    # Run the Flask app with SSL
    app.run(host='0.0.0.0', port=5000, ssl_context=ssl_context)
