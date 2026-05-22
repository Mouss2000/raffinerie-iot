# Implementation Plan: Predictive ML & Web Control

## Objective
Implement LSTM predictive model for IoT anomalies. Build Web API/UI for pipeline control.

## Architecture
- **ML Storage**: MinIO (Raw JSON) -> Local Training Script.
- **Model**: LSTM (Time-series sequences). Output: `.h5` or `.pt`.
- **Inference**: Standalone Python microservice. Kafka Consumer (`sensor-data`) -> LSTM -> TimescaleDB (`predictive_alerts`).
- **Control API**: FastAPI. Routes: Start/Stop pipeline, update sensor config, adjust ML thresholds.
- **Web UI**: HTML/JS/Tailwind. Pipeline controls, config inputs.
- **Visualization**: Grafana (Monitoring).

## Implementation Steps

### Phase 1: LSTM Model (Data & Training)
1. Write script `ml/extract_minio.py` to pull history from `raffinerie-raw`.
2. Write script `ml/train_lstm.py` (PyTorch/TensorFlow). Sliding window prep. Train model. Save weights.

### Phase 2: Real-Time Inference Microservice
1. Create TimescaleDB table `predictive_alerts`.
2. Write `ml/inference.py`. Kafka consumer (`sensor-data`). Load model. Predict. Insert alerts on threshold breach.

### Phase 3: Control Backend (FastAPI)
1. Write `api/main.py`.
2. Endpoints:
   - `POST /api/pipeline/start` (Executes simulator/bridge).
   - `POST /api/pipeline/stop`.
   - `POST /api/config/sensors` (Updates JSON config for simulator).
   - `POST /api/config/threshold` (Updates threshold for `inference.py`).

### Phase 4: Web Interface
1. Create `web/index.html` + `web/app.js`.
2. UI controls bound to FastAPI endpoints.

### Phase 5: Pipeline Updates
1. Modify `simulateur_capteurs.py` to read sensor count from dynamic JSON config.

## Verification
- Model trains successfully from MinIO data.
- `inference.py` writes alerts to TimescaleDB.
- API endpoints manage subprocesses.
- UI buttons trigger API actions correctly.
