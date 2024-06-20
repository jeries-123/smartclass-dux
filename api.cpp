#include "DHT.h"
#include <wiringPi.h>
#include <iostream>
#include <cstdlib>
#include <cstring>
#include <netinet/in.h>test 5
#include <unistd.h>
#include "Adafruit_DHT.h"


#define RELAY_PIN 17      // GPIO17 for lamp
#define PROJECTOR_PIN 18  // GPIO18 for projector
#define DHT_PIN 19        // GPIO19 for DHT sensor
#define DHT_TYPE DHT11    // DHT sensor type

Adafruit_DHT dht(DHT_PIN, DHT_TYPE);

void setup() {
    wiringPiSetup();
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
        // Handle control requests for lamp and projector
        // (same as before)
    } else if (strcmp(buffer, "GET /temperature HTTP/1.1") == 0) {
        float temperature = dht.readTemperature();
        if (isnan(temperature)) {
            response = "HTTP/1.1 500 Internal Server Error\r\nContent-Type: application/json\r\nAccess-Control-Allow-Origin: *\r\n\r\n{\"error\":\"Failed to read temperature\"}";
        } else {
            response = "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nAccess-Control-Allow-Origin: *\r\n\r\n{\"temperature\":" + std::to_string(temperature) + "}";
        }
    } else if (strcmp(buffer, "GET /humidity HTTP/1.1") == 0) {
        float humidity = dht.readHumidity();
        if (isnan(humidity)) {
            response = "HTTP/1.1 500 Internal Server Error\r\nContent-Type: application/json\r\nAccess-Control-Allow-Origin: *\r\n\r\n{\"error\":\"Failed to read humidity\"}";
        } else {
            response = "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nAccess-Control-Allow-Origin: *\r\n\r\n{\"humidity\":" + std::to_string(humidity) + "}";
        }
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
