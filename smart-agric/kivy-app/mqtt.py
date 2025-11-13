import paho.mqtt.client as mqtt
import json
import time
import random

# MQTT Configuration
BROKER = "f3150d0d05ce46d0873bf1a69c56ff38.s1.eu.hivemq.cloud"  # e.g., HiveMQ Cloud URL
PORT = 8883  # Use 8883 for TLS, 1883 for non-TLS
USERNAME = "Ayodeji"
PASSWORD = "cand4f694a@A"
TOPIC = "agripal/farm1/sensor1"

# Initialize MQTT Client
client = mqtt.Client(client_id="raspberry_pi_sensor_1")
client.username_pw_set(USERNAME, PASSWORD)

# Enable TLS for secure connection
client.tls_set()

# Callbacks
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
    else:
        print(f"Failed to connect, return code {rc}")

def on_publish(client, userdata, mid):
    print(f"Message {mid} published")

client.on_connect = on_connect
client.on_publish = on_publish

# Connect to broker
client.connect(BROKER, PORT, 60)
client.loop_start()

# Publish sensor data
try:
    while True:
        # Read sensor data (replace with actual sensor readings)
        sensor_data = {
            "device_id": "sensor_1",
            "farm_id": "farm1",
            "timestamp": int(time.time()),
            "soil_moisture": random.uniform(20, 80),
            "temperature": random.uniform(15, 35),
            "ph_level": random.uniform(5.5, 7.5),
            "nitrogen": random.uniform(50, 200)
        }
        
        # Publish to MQTT
        result = client.publish(TOPIC, json.dumps(sensor_data), qos=1)
        
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            print(f"Published: {sensor_data}")
        
        time.sleep(20)  # Send data every minute
        
except KeyboardInterrupt:
    print("Stopping...")
    client.loop_stop()
    client.disconnect()

