from flask import Flask, render_template
from threading import Thread
from signaling_server import run_websocket

app = Flask(__name__)

# Main route to render the index.html page
@app.route('/')
def index():
    return render_template('index.html')

# Running Flask and WebSocket server together
if __name__ == '__main__':
    # Start WebSocket server in a separate thread
    websocket_thread = Thread(target=run_websocket)
    websocket_thread.start()

    # Run Flask app (this will run the web server)
    app.run(host='0.0.0.0', port=5000, debug=True)
