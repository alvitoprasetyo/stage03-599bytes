from machine import Pin
import network
import time
from umqtt.simple import MQTTClient

# WiFi Credentials
WIFI_SSID = "poco"
WIFI_PASS = "hotspot44231"

# Ubidots Config
UBIDOTS_TOKEN = "BBUS-jsfxoukARnkvGzSfmBBAdtzV60TQF3"
DEVICE_LABEL = "demo-machine"
MQTT_CLIENT_ID = "esp32-client"  # Unique client ID

# LED Pins
GREEN_LED = Pin(12, Pin.OUT)
YELLOW_LED = Pin(14, Pin.OUT)
RED_LED = Pin(27, Pin.OUT)

def connect_wifi():
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    if not wifi.isconnected():
        print("Connecting to WiFi...")
        wifi.connect(WIFI_SSID, WIFI_PASS)
        for _ in range(100):  # Wait up to 10 seconds
            if wifi.isconnected():
                break
            time.sleep(0.5)
    if wifi.isconnected():
        print("WiFi Connected:", wifi.ifconfig())
        return True
    else:
        print("WiFi Connection Failed")
        return False

def callback(topic, msg):
    print("Message arrived:", topic, msg)
    try:
        value = int(msg)
        GREEN_LED.value(value == 1)
        YELLOW_LED.value(value == 2)
        RED_LED.value(value == 3)
        print(f"LEDs updated - Status: {value}")
    except ValueError:
        print("Invalid message received")

def main():
    if not connect_wifi():
        return

    client = MQTTClient(
        client_id=MQTT_CLIENT_ID,
        server="industrial.api.ubidots.com",
        user=UBIDOTS_TOKEN,
        password="",
        port=1883,
        ssl=False
    )
    
    client.set_callback(callback)
    
    try:
        client.connect()
        print("Connected to Ubidots MQTT")
        client.subscribe(f"/v1.6/devices/{DEVICE_LABEL}/led_status/lv")
        print("Subscribed to topic")
        
        while True:
            client.check_msg()
            time.sleep(1)
            
    except Exception as e:
        print("MQTT Error:", e)
        RED_LED.on()  # Indicate error
    finally:
        client.disconnect()
        print("Disconnected")

if __name__ == "__main__":
    main()