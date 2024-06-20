#include <wiringPi.h>
#include <iostream>
#include <cstdlib>
#include <cstring>
#include <netinet/in.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <fcntl.h>

#define RELAY_PIN 0       // GPIO17
#define PROJECTOR_PIN 1   // GPIO18

void setup() {
    wiringPiSetup();
    pinMode(RELAY_PIN, OUTPUT);
    digitalWrite(RELAY_PIN, LOW);  // Relay off
    pinMode(PROJECTOR_PIN, OUTPUT);
    digitalWrite(PROJECTOR_PIN, LOW);  // Projector off
}

void handleRequest(int client_socket) {
    const int buffer_size = 2048;
    char buffer[buffer_size];
    memset(buffer, 0, buffer_size);
    int total_read = 0;

    while (total_read < buffer_size - 1) {
        int read_size = read(client_socket, buffer + total_read, buffer_size - 1 - total_read);
        if (read_size < 0) {
            std::cerr << "Error reading request: " << strerror(errno) << std::endl;
            close(client_socket);
            return;
        }
        if (read_size == 0) {
            break;
        }
        total_read += read_size;
    }

    if (total_read > 0) {
        std::cout << "Received request: " << buffer << std::endl;

        const char* response;
        if (strncmp(buffer, "POST /control HTTP", 18) == 0) {
            if (strstr(buffer, "device=lamp&action=on") != NULL) {
                digitalWrite(RELAY_PIN, HIGH);  // Relay on
                std::cout << "Turning relay ON" << std::endl;
            } else if (strstr(buffer, "device=lamp&action=off") != NULL) {
                digitalWrite(RELAY_PIN, LOW);  // Relay off
                std::cout << "Turning relay OFF" << std::endl;
            } else if (strstr(buffer, "device=projector&action=on") != NULL) {
                digitalWrite(PROJECTOR_PIN, HIGH);  // Projector on
                std::cout << "Turning projector ON" << std::endl;
            } else if (strstr(buffer, "device=projector&action=off") != NULL) {
                digitalWrite(PROJECTOR_PIN, LOW);  // Projector off
                std::cout << "Turning projector OFF" << std::endl;
            }
            response = "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nAccess-Control-Allow-Origin: *\r\n\r\n{\"status\":\"success\"}";
        } else {
            response = "HTTP/1.1 400 Bad Request\r\nContent-Type: application/json\r\nAccess-Control-Allow-Origin: *\r\n\r\n{\"status\":\"error\"}";
        }

        write(client_socket, response, strlen(response));
    } else {
        std::cerr << "Received empty request or error reading request" << std::endl;
    }

    close(client_socket);
}

int main() {
    setup();

    int server_socket;
    struct sockaddr_in server_addr, client_addr;
    socklen_t client_len = sizeof(client_addr);

    server_socket = socket(AF_INET, SOCK_STREAM, 0);
    if (server_socket < 0) {
        std::cerr << "Error opening socket: " << strerror(errno) << std::endl;
        return 1;
    }

    int opt = 1;
    setsockopt(server_socket, SOL_SOCKET, SO_REUSEADDR | SO_REUSEPORT, &opt, sizeof(opt));

    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(5000);

    if (bind(server_socket, (struct sockaddr*)&server_addr, sizeof(server_addr)) < 0) {
        std::cerr << "Error binding socket: " << strerror(errno) << std::endl;
        close(server_socket);
        return 1;
    }

    listen(server_socket, 5);

    std::cout << "Server running on port 5000" << std::endl;

    while (true) {
        int client_socket = accept(server_socket, (struct sockaddr*)&client_addr, &client_len);
        if (client_socket < 0) {
            std::cerr << "Error accepting connection: " << strerror(errno) << std::endl;
            continue;
        }
        handleRequest(client_socket);
    }

    close(server_socket);
    return 0;
}
