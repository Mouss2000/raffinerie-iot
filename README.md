# Raffinerie IoT - Intelligent Monitoring & Predictive Maintenance

A distributed Big Data and AI pipeline designed for real-time industrial anomaly detection. This system monitors refinery equipment using multi-variate analysis (Temperature + Vibration) and an unsupervised Isolation Forest model.

## 🚀 Key Features
*   **Distributed Pipeline:** MQTT -> Kafka -> Spark Structured Streaming.
*   **Dual Storage:** TimescaleDB for structured analytics and MinIO for raw data lake archiving.
*   **Multi-Variate AI:** Real-time anomaly detection using an Isolation Forest trained on 125,000+ industrial data points.
*   **Web Control Center:** Real-time dashboard with dual-axis visualization and dynamic hardware scaling.

---

## 🛠️ Prerequisites
1.  **Docker Desktop** (with at least 6GB RAM allocated).
2.  **Python 3.10+**.
3.  **Virtual Environment:** Pre-configured in the `venv/` folder.

---

## 🏁 Startup Sequence (Step-by-Step)

Follow these steps in order to ensure all services connect correctly:

### Step 1: Launch Infrastructure (Docker)
Open a terminal in the project root and run:
```powershell
docker-compose up -d --build
```
*Wait ~30 seconds for Kafka and Zookeeper to initialize.*

### Step 2: Start the Control API (Backend)
Open a new terminal and run:
```powershell
.\venv\Scripts\python.exe api/main.py
```
*This starts the FastAPI server on http://localhost:8000.*

### Step 3: Open the Dashboard (Frontend)
Open the file `web/index.html` in any modern web browser (Chrome/Edge/Firefox).

### Step 4: Start the Pipeline
On the Web UI, click the **START PIPELINE** button. This will automatically launch:
1.  The Sensor Simulator
2.  The MQTT-to-Kafka Bridge
3.  The Multi-Variate AI Inference Engine

---

## 🎮 How to Use the Control Center

### 1. Monitoring
*   **Real-Time Stream:** View raw sensor data. Blue = Temperature, Green = Vibration.
*   **AI Performance:** Watch the AI's "Judgment." The Yellow line (Score) will drop when weird behavior is detected.
*   **Alert Console:** Real-time logs of every flagged anomaly.

### 2. Live Configuration
*   **Machine Count:** Change the number (e.g., to 10) and click **APPLY** to scale the simulated refinery.
*   **ML Alert Threshold:** 
    *   `10.0` = High Sensitivity (Many alerts).
    *   `20.0` = Recommended Balance.
    *   `50.0` = Low Sensitivity (Critical only).

---

## 🧠 AI Training (Optional)
If you wish to retrain the model on new data:
1.  Run the collection for any duration.
2.  Run `.\venv\Scripts\python.exe ml/extract_minio.py` to pull data from the lake.
3.  Run `.\venv\Scripts\python.exe ml/train_anomaly.py` to update the Isolation Forest.

---

## 📂 Project Structure
*   `api/`: FastAPI Backend & Script Orchestrator.
*   `ml/`: Isolation Forest model, Scalers, and Inference logic.
*   `spark/`: Spark Structured Streaming job (Dockerized).
*   `web/`: Real-time HTML5/Chart.js Dashboard.
*   `simulateur_capteurs.py`: Physics-based sensor emulator.
*   `mqtt_to_kafka.py`: Real-time ingestion bridge.
