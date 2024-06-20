import Adafruit_DHT
import RPi.GPIO as GPIO
import socket

RELAY_PIN = 17      # GPIO17 for lamp
PROJECTOR_PIN = 18  # GPIO18 for projector
DHT_PIN = 19        # GPIO19 for DHT sensor
DHT_TYPE = Adafruit_DHT.DHT11    # DHT sensor type

GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)
GPIO.output(RELAY_PIN, GPIO.LOW)  # Relay off
GPIO.setup(PROJECTOR_PIN, GPIO.OUT)
GPIO.output(PROJECTOR_PIN, GPIO.LOW)  # Projector off

def handle_request(request):
    response = ""
    if "POST /control" in request:
        # Handle control requests for lamp and projector
        if "device=lamp&action=on" in request:
            GPIO.output(RELAY_PIN, GPIO.HIGH)  # Relay on
            print("Turning relay ON")
        elif "device=lamp&action=off" in request:
            GPIO.output(RELAY_PIN, GPIO.LOW)  # Relay off
            print("Turning relay OFF")
        elif "device=projector&action=on" in request:
            GPIO.output(PROJECTOR_PIN, GPIO.HIGH)  # Projector on
            print("Turning projector ON")
        elif "device=projector&action=off" in request:
            GPIO.output(PROJECTOR_PIN, GPIO.LOW)  # Projector off
            print("Turning projector OFF")
        response = "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nAccess-Control-Allow-Origin: *\r\n\r\n{\"status\":\"success\"}"
    elif "GET /temperature" in request:
        # Read temperature from sensor
        humidity, temperature = Adafruit_DHT.read_retry(DHT_TYPE, DHT_PIN)
        response = f"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n{{\"temperature\": {temperature}}}"
    elif "GET /humidity" in request:
        # Read humidity from sensor
        humidity, temperature = Adafruit_DHT.read_retry(DHT_TYPE, DHT_PIN)
        response = f"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n{{\"humidity\": {humidity}}}"
    else:
        response = "HTTP/1.1 400 Bad Request\r\nContent-Type: text/plain\r\n\r\nBad Request"

    return response

try:
    # Setup server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 5000))  # Bind to all network interfaces
    server_socket.listen(5)

    print("Server running on port 5000")

    # Main server loop
    while True:
        client_socket, addr = server_socket.accept()
        request = client_socket.recv(1024).decode('utf-8')
        print("Received request:", request)

        response = handle_request(request)

        client_socket.sendall(response.encode('utf-8'))
        client_socket.close()
finally:
    # Clean up GPIO
    GPIO.cleanup()

    # Close server socket
    server_socket.close()
