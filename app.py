import requests
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

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

# API to control devices via switch
@app.route('/control', methods=['POST'])
def control_device():
    device = request.form.get('device')
    action = request.form.get('action')
    
    if device in devices:
        devices[device] = action
        print(f"Device '{device}' set to '{action}'")
        # Send control request to the remote API
        send_control_request(device, action)
        return jsonify({"status": "success", "device": device, "action": action})
    else:
        return jsonify({"status": "error", "message": "Invalid device"}), 400

# Function to send device control request to the remote API
def send_control_request(device, action):
    try:
        url = 'https://smartclass.loca.lt/control'
        response = requests.post(url, data={'device': device, 'action': action})
        
        if response.status_code == 200:
            print(f"Device '{device}' set to '{action}' via API")
        else:
            print(f"Error: Unable to set '{device}' to '{action}' (status: {response.status_code})")
    except Exception as e:
        print(f"Error sending control request: {str(e)}")

if __name__ == '__main__':
    app.run(debug=True)
