from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
import os
import subprocess
import psutil
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

CONFIG_FILE = "config.json"
SCRIPTS = {
    "simulator": "simulateur_capteurs.py",
    "bridge": "mqtt_to_kafka.py",
    "inference": "ml/inference.py"
}
PYTHON_EXE = os.path.join("venv", "Scripts", "python.exe")
DB_CONFIG = "dbname=iotdb user=admin password=admin host=127.0.0.1 port=5432"

class ConfigUpdate(BaseModel):
    sensor_count: int = None
    ml_threshold: float = None

def get_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def is_running(script_name):
    for proc in psutil.process_iter(['pid', 'cmdline']):
        try:
            if proc.info['cmdline'] and script_name in " ".join(proc.info['cmdline']):
                return proc.info['pid']
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return None

def get_db_connection():
    return psycopg2.connect(DB_CONFIG, cursor_factory=RealDictCursor)

@app.get("/api/status")
def get_status():
    status = {}
    for name, script in SCRIPTS.items():
        status[name] = is_running(script) is not None
    status["config"] = get_config()
    return status

@app.post("/api/pipeline/start")
def start_pipeline():
    for name, script in SCRIPTS.items():
        if not is_running(script):
            subprocess.Popen([PYTHON_EXE, script])
    return {"message": "Pipeline starting..."}

@app.post("/api/pipeline/stop")
def stop_pipeline():
    for name, script in SCRIPTS.items():
        pid = is_running(script)
        if pid:
            try:
                psutil.Process(pid).terminate()
            except psutil.NoSuchProcess:
                pass
    return {"message": "Pipeline stopping..."}

@app.post("/api/config")
def update_config(data: ConfigUpdate):
    config = get_config()
    if data.sensor_count is not None:
        config["sensor_count"] = data.sensor_count
    if data.ml_threshold is not None:
        config["ml_threshold"] = data.ml_threshold
    save_config(config)
    return config

@app.get("/api/data/sensors")
def get_sensor_data():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT timestamp, machine_id, valeur, type_capteur 
        FROM mesures_filtrees 
        WHERE type_capteur IN ('temperature', 'vibration')
        ORDER BY timestamp DESC LIMIT 1000
    """)
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

@app.get("/api/data/predictions")
def get_prediction_data():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT timestamp, machine_id, valeur_actuelle, valeur_predite, ecart 
        FROM predictive_alerts 
        ORDER BY timestamp DESC LIMIT 50
    """)
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

@app.get("/api/data/alerts")
def get_recent_alerts():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT timestamp, machine_id, valeur_actuelle, valeur_predite, ecart 
        FROM predictive_alerts 
        WHERE est_alerte = True 
        ORDER BY timestamp DESC LIMIT 20
    """)
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
