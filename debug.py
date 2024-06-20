import Adafruit_DHT
import time

DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 27

try:
    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
    if humidity is not None and temperature is not None:
        print(f"Temp: {temperature:.1f}C  Humidity: {humidity:.1f}%")
    else:
        print("Failed to retrieve data from the humidity sensor")
except RuntimeError as e:
    print(f"RuntimeError: {e}")

