import Adafruit_DHT
import platform_detect

DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 27

try:
    platform = platform_detect.platform_detect()
    if platform == 'Raspberry_Pi':
        humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
        if humidity is not None and temperature is not None:
            print(f"Temp: {temperature:.1f}C  Humidity: {humidity:.1f}%")
        else:
            print("Failed to retrieve data from humidity sensor")
    else:
        print("Unsupported platform")
except RuntimeError as e:
    print(f"RuntimeError: {e}")
