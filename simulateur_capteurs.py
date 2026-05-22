from datetime import datetime, timezone
import time, json, random
import paho.mqtt.client as mqtt
import os

CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {"sensor_count": 1}

client = mqtt.Client()
client.connect("localhost", 1883, 60)

print("Simulator started. Using strict UTC timestamps.")

while True:
    config = load_config()
    count = config.get("sensor_count", 1)
    
    # Force UTC
    now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    
    for i in range(count):
        machine_id = f"machine-{100 + i}"
        
        # Temperature
        temp = round(random.uniform(-50, 200), 2)
        msg_temp = json.dumps({
            "machine_id": machine_id,
            "valeur": temp,
            "timestamp": now,
            "type_capteur": "temperature"
        })
        client.publish("raffinerie/temp", msg_temp)
        
        # Vibration
        vib = round(random.uniform(-1, 6), 2)
        msg_vib = json.dumps({
            "machine_id": machine_id,
            "valeur": vib,
            "timestamp": now,
            "type_capteur": "vibration"
        })
        client.publish("raffinerie/vib", msg_vib)
        
    print(f"[{now}] Published data for {count} machines.")
    time.sleep(1.0)
