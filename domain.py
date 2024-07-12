from flask import Flask
import requests
from pyngrok import ngrok

app = Flask(__name__)

# Start localtunnel and get the public URL
tunnel_url = ngrok.connect(5000).public_url
print(f"Localtunnel URL: {tunnel_url}")

@app.route('/')
def home():
    return 'Welcome to the Smart Classroom by Dux'

@app.route('/sensor')
def sensor_data():
    # Replace with your sensor data retrieval logic
    return 'Sensor data response'

if __name__ == '__main__':
    # Notify the server of the localtunnel URL
    try:
        response = requests.post('https://temp.aiiot.website/data.php', json={'url': tunnel_url})
        if response.status_code == 200:
            print("URL sent to server successfully.")
        else:
            print(f"Failed to send URL. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error sending URL to server: {e}")

    # Run Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)
