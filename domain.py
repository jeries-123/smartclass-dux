from flask import Flask, jsonify
import subprocess
import re
import requests
import threading

app = Flask(__name__)

# Replace with your actual domain URL for sending the tunnel URL
domain_url = "https://temp.aiiot.website/domain.php"

def start_localtunnel():
    try:
        command = ['lt', '--port', '5000', '--subdomain', 'saltunnelme']
        result = subprocess.run(command, capture_output=True, text=True)
        output = result.stdout

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

# Endpoint to test if server is running
@app.route('/')
def index():
    return "Server is running!"

# Example endpoint to fetch data
@app.route('/data')
def get_data():
    # Replace with your data fetching logic
    data = {"temperature": 25, "humidity": 60}
    return jsonify(data)

if __name__ == '__main__':
    # Start localtunnel in a separate thread
    localtunnel_thread = threading.Thread(target=start_localtunnel)
    localtunnel_thread.start()

    # Run Flask app
    app.run(debug=True)
