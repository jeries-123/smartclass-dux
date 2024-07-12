import subprocess
import requests

def start_localtunnel():
    try:
        # Adjust the lt command as needed with correct path and parameters
        subprocess.Popen(['lt', '--port', '5000'], stdout=subprocess.PIPE)
        print("localtunnel started successfully.")
    except Exception as e:
        print(f"Error starting localtunnel: {str(e)}")

if __name__ == "__main__":
    start_localtunnel()
    app.run(debug=True)
