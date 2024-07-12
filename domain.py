import subprocess

try:
    result = subprocess.run(['lt', '--port', '5000', '--print-requests'], capture_output=True, text=True)
    print("Localtunnel result:", result.stdout.strip())
except Exception as e:
    print("Error running localtunnel:", e)
