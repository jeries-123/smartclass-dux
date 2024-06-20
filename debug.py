import Adafruit_DHT

DHT_PIN = 27
DHT_TYPE = Adafruit_DHT.DHT11

try:
    humidity, temperature = Adafruit_DHT.read_retry(DHT_TYPE, DHT_PIN, platform='Raspberry Pi')
    if humidity is not None and temperature is not None:
        print(f"Temperature: {temperature} C, Humidity: {humidity}%")
    else:
        print("Failed to retrieve sensor data")
except Exception as e:
    print(f"Error reading sensor data: {e}")
