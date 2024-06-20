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

def handle_request(client_socket):
    request = client_socket.recv(1024).decode()
    print("Received request:", request)

    response = ""
if "POST /control" in request:
    # Handle control requests for lamp and projector
    if "device=lamp&action=on" in request:
        digitalWrite(RELAY_PIN, HIGH)  # Relay on
        print("Turning relay ON")
    elif "device=lamp&action=off" in request:
        digitalWrite(RELAY_PIN, LOW)  # Relay off
        print("Turning relay OFF")
    elif "device=projector&action=on" in request:
        digitalWrite(PROJECTOR_PIN, HIGH)  # Projector on
        print("Turning projector ON")
    elif "device=projector&action=off" in request:
        digitalWrite(PROJECTOR_PIN, LOW)  # Projector off
        print("Turning projector OFF")
    response = "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nAccess-Control-Allow-Origin: *\r\n\r\n{\"status\":\"success\"}"
elif "GET /temperature" in request:
    temperature = dht.readTemperature()
    if not isnan(temperature):
        response = f"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nAccess-Control-Allow-Origin: *\r\n\r\n{{\"temperature\":{temperature}}}"
    else:
        response = "HTTP/1.1 500 Internal Server Error\r\nContent-Type: application/json\r\nAccess-Control-Allow-Origin: *\r\n\r\n{\"error\":\"Failed to read temperature\"}"
elif "GET /humidity" in request:
    humidity = dht.readHumidity()
    if not isnan(humidity):
        response = f"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nAccess-Control-Allow-Origin: *\r\n\r\n{{\"humidity\":{humidity}}}"
    else:
        response = "HTTP/1.1 500 Internal Server Error\r\nContent-Type: application/json\r\nAccess-Control-Allow-Origin: *\r\n\r\n{\"error\":\"Failed to read humidity\"}"
else:
    response = "HTTP/1.1 400 Bad Request\r\nContent-Type: application/json\r\nAccess-Control-Allow-Origin: *\r\n\r\n{\"status\":\"error\"}"


    client_socket.sendall(response.encode())
    client_socket.close()

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(('0.0.0.0', 5000))
server_socket.listen(5)

print("Server running on port 5000")

try:
    while True:
        client_socket, client_addr = server_socket.accept()
        handle_request(client_socket)
except KeyboardInterrupt:
    GPIO.cleanup()
