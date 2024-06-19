#include <wiringPi.h>
#include <iostream>
#include <cstdlib>
#include <cstring>
#include <netinet/in.h>
#include <unistd.h>
#include "Adafruit_Python_DHT/Adafruit_DHT.h"


#define RELAY_PIN 0       // GPIO17
#define PROJECTOR_PIN 1   // GPIO18
#define DHT_PIN 7         // GPIO4

#define DHT_TYPE DHT11    // or DHT22

DHT dht(DHT_PIN, DHT_TYPE);

void setup() {
    wiringPiSetup();
    dht.begin();
    pinMode(RELAY_PIN, OUTPUT);
    digitalWrite(RELAY_PIN, LOW);  // Relay off
    pinMode(PROJECTOR_PIN, OUTPUT);
    digitalWrite(PROJECTOR_PIN, LOW);  // Projector off
}

void handleRequest(int client_socket) {
    const int buffer_size = 1024;
    char buffer[buffer_size];
    read(client_socket, buffer, buffer_size);

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
    } else if (strncmp(buffer, "GET /temperature", 16) == 0) {
        float temperature = dht.readTemperature();
        float humidity = dht.readHumidity();
        char temp_response[buffer_size];
        snprintf(temp_response, buffer_size, "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nAccess-Control-Allow-Origin: *\r\n\r\n{\"temperature\":%.1f,\"humidity\":%.1f}", temperature, humidity);
        response = temp_response;
    } else {
        response = "HTTP/1.1 400 Bad Request\r\nContent-Type: application/json\r\nAccess-Control-Allow-Origin: *\r\n\r\n{\"status\":\"error\"}";
    }

    write(client_socket, response, strlen(response));
    close(client_socket);
}

int main() {
    setup();

    int server_socket;
    struct sockaddr_in server_addr, client_addr;
    socklen_t client_len = sizeof(client_addr);

    server_socket = socket(AF_INET, SOCK_STREAM, 0);
    if (server_socket < 0) {
        std::cerr << "Error opening socket" << std::endl;
        return 1;
    }

    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(5000);

    if (bind(server_socket, (struct sockaddr*)&server_addr, sizeof(server_addr)) < 0) {
        std::cerr << "Error binding socket" << std::endl;
        return 1;
    }

    listen(server_socket, 5);

    std::cout << "Server running on port 5000" << std::endl;

    while (true) {
        int client_socket = accept(server_socket, (struct sockaddr*)&client_addr, &client_len);
        if (client_socket < 0) {
            std::cerr << "Error accepting connection" << std::endl;
            continue;
        }
        handleRequest(client_socket);
    }

    close(server_socket);
    return 0;
}