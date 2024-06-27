import RPi.GPIO as GPIO
import socket
import ssl

RELAY_PIN = 27      # GPIO17 for lamp
PROJECTOR_PIN = 18  # GPIO18 for projector

GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)
GPIO.output(RELAY_PIN, GPIO.LOW)  # Relay off
GPIO.setup(PROJECTOR_PIN, GPIO.OUT)
GPIO.output(PROJECTOR_PIN, GPIO.LOW)  # Projector off

def handle_request(request):
    response = ""
    try:
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
        else:
            response = "HTTP/1.1 400 Bad Request\r\nContent-Type: text/plain\r\n\r\nBad Request"
    except Exception as e:
        print(f"Exception while handling request: {e}")
        response = "HTTP/1.1 500 Internal Server Error\r\nContent-Type: text/plain\r\n\r\nInternal Server Error"

    return response

try:
    # Load SSL certificate and key
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    
    # Attempt to load the certificate and key
    try:
        ssl_context.load_cert_chain(certfile='/Desktop/smartclass-dux/server.crt', keyfile='/Desktop/smartclass-dux/server.key')
        print("Loaded SSL certificate and key successfully.")
    except ssl.SSLError as e:
        print(f"Error loading SSL certificate/key: {e}")
        raise e  # Re-raise the exception to handle it later

    # Setup server socket with SSL
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 5000))  # Bind to all network interfaces
    server_socket.listen(5)

    print("Server running on port 5000 with HTTPS")

    # Main server loop
    while True:
        client_socket, addr = server_socket.accept()
        try:
            # Wrap client socket with SSL
            ssl_socket = ssl_context.wrap_socket(client_socket, server_side=True)
            request = ssl_socket.recv(1024)
            print("Received request:", request)

            response = handle_request(request.decode('utf-8'))

            ssl_socket.sendall(response.encode('utf-8'))
        except Exception as e:
            print(f"Error handling request: {e}")
        finally:
            ssl_socket.close()

except Exception as e:
    print(f"Exception during server setup: {e}")

finally:
    # Clean up GPIO
    GPIO.cleanup()

    # Close server socket if it exists
    if 'server_socket' in locals():
        server_socket.close()
