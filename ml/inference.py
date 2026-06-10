import json
import numpy as np
from kafka import KafkaConsumer
import psycopg2
import joblib
import os

# Configuration
KAFKA_BROKER = "localhost:9092"
TOPIC_NAME = "sensor-data"
DB_CONFIG = "dbname=iotdb user=admin password=admin host=127.0.0.1 port=5432"
CONFIG_FILE = "config.json"
MODEL_PATH = "ml/isolation_forest.joblib"
SCALER_PATH = "ml/scaler.gz"

def load_alert_threshold():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config_val = json.load(f).get("ml_threshold", 20.0)
                return 0.05 - (config_val * 0.005)
        except:
            return -0.05
    return -0.05

# Initialization
if not os.path.exists(MODEL_PATH):
    print(f"CRITICAL ERROR: Model {MODEL_PATH} not found. Please train it first.")
    exit(1)

model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)

# Buffers: {machine_id: {'temperature': [v1, v2], 'vibration': [v1, v2]}}
buffers = {} 

print("Starting MULTI-VARIATE ISOLATION FOREST inference...")

consumer = KafkaConsumer(
    TOPIC_NAME,
    bootstrap_servers=[KAFKA_BROKER],
    auto_offset_reset='latest',
    value_deserializer=lambda v: json.loads(v.decode('utf-8'))
)

try:
    conn = psycopg2.connect(DB_CONFIG)
    cur = conn.cursor()
except Exception as e:
    print(f"DB Connection Error: {e}")
    exit(1)

try:
    for message in consumer:
        score_threshold = load_alert_threshold()
        data = message.value
        m_id = data['machine_id']
        t_type = data['type_capteur']
        val = data['valeur']
        ts = data['timestamp']

        if m_id not in buffers:
            buffers[m_id] = {'temperature': [], 'vibration': []}
        
        # Store current reading in correct buffer
        if t_type in ['temperature', 'vibration']:
            buffers[m_id][t_type].append(val)
        else:
            continue

        # Multi-Variate Inference logic: 
        # We require a window of BOTH sensor types to compute rolling statistics.
        if len(buffers[m_id]['temperature']) >= 5 and len(buffers[m_id]['vibration']) >= 5:
            # Align on the latest observations
            temp_latest = buffers[m_id]['temperature'][-1]
            vib_latest = buffers[m_id]['vibration'][-1]
            
            # Local state features for Isolation Forest
            features = np.array([[
                temp_latest, 
                vib_latest, 
                np.mean(buffers[m_id]['temperature'][-5:]), 
                np.mean(buffers[m_id]['vibration'][-5:])
            ]])
            
            # Transformation & Scoring
            scaled_input = scaler.transform(features)
            score = float(model.decision_function(scaled_input)[0])
            is_alert = bool(score < score_threshold)

            # Persistence: Mapping Multi-Variate data to existing schema
            # 'valeur_actuelle' -> Temperature
            # 'ecart'           -> Vibration (Optimized for Chart.js display)
            cur.execute(
                "INSERT INTO predictive_alerts (timestamp, machine_id, type_capteur, valeur_actuelle, valeur_predite, ecart, est_alerte) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (ts, m_id, 'multi_variate', float(temp_latest), score, float(vib_latest), is_alert)
            )
            conn.commit()

            if is_alert:
                print(f"!!! MULTI-VARIATE ALERT [{m_id}] !!! Score: {score:.4f} | Temp: {temp_latest:.1f}, Vib: {vib_latest:.2f}")

            # Keep buffers small to prevent memory creep
            buffers[m_id]['temperature'] = buffers[m_id]['temperature'][-5:]
            buffers[m_id]['vibration'] = buffers[m_id]['vibration'][-5:]

except Exception as e:
    print(f"Inference error: {e}")
finally:
    if 'cur' in locals(): cur.close()
    if 'conn' in locals(): conn.close()
